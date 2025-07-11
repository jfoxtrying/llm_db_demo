# app/endpoints/mc_endpoint.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.analytics.mc import run_mc
from app.db import get_company_db
import numpy as np

router = APIRouter(prefix="/mc")


class MCReq(BaseModel):
    project_id: str
    n_draws:   int = 10_000          # default


@router.post("/")
def mc(req: MCReq, db = Depends(get_company_db)):
    # ── 1 · scalar metrics (everything except yearly NOI) ─────────────
    q_static = text("""
        SELECT LOWER(TRIM(metric)) AS metric, value
        FROM   metrics_raw
        WHERE  project_id = :pid
          AND  metric NOT LIKE 'noi%'        -- skip yearly NOI rows
    """)
    params: dict[str, float] = {}
    for r in db.execute(q_static, {"pid": req.project_id}).mappings():
        try:
            params[r["metric"]] = float(r["value"])
        except (TypeError, ValueError):
            # silently ignore non-numeric cells
            continue

    # ── 2 · derive NOI μ / σ if missing  ─────────────────────────────
    if "noi_mu" not in params or "noi_sd" not in params:
        noi_vals = [
            float(v)
            for (v,) in db.execute(
                text("""
                    SELECT value
                    FROM   metrics_raw
                    WHERE  project_id = :pid
                      AND  metric      = 'noi'
                      AND  value IS NOT NULL
                """),
                {"pid": req.project_id},
            )
        ]

        if len(noi_vals) >= 2:
            params["noi_mu"] = float(np.mean(noi_vals))
            params["noi_sd"] = float(np.std(noi_vals, ddof=1))

        elif len(noi_vals) == 1:
            base_noi = noi_vals[0]
            rg = (params.get("rental_growth") or
                  params.get("rental_growth_assumption") or 0.0)
            try:
                rg = float(rg)
            except ValueError:
                rg = 0.0

            next_noi          = base_noi * (1 + rg)
            params["noi_mu"]  = (base_noi + next_noi) / 2
            params["noi_sd"]  = abs(next_noi - base_noi) / np.sqrt(2)

        else:
            raise HTTPException(
                status_code=422,
                detail="No NOI rows found for this project – please insert at least one."
            )

    # ── 3 · sanity-check that everything the MC model needs is present ─
    required = [
        "debt_ltv_min", "debt_ltv_max",
        "interest_rate_min", "interest_rate_max",
        "exit_cap_rate",
        "noi_mu", "noi_sd",
    ]
    missing = [k for k in required if k not in params]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing parameters in metrics_raw: {', '.join(missing)}"
        )

    # ── 4 · Monte-Carlo simulation  ───────────────────────────────────
    out = run_mc(
        req.n_draws,
        params["debt_ltv_min"], params["debt_ltv_max"],
        params["interest_rate_min"], params["interest_rate_max"],
        params["exit_cap_rate"],
        params["noi_mu"], params["noi_sd"],
    )
    return out