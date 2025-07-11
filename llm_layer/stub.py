# llm_layer/stub.py

def llm_stub(payload: dict) -> dict:
    """
    Development stub that mimics Gemini JSON output
    without spending tokens.
    """
    name = payload.get("name")
    print("STUB → tool name:", name)

    # 1. Cap-rate forecast tool
    if name == "get_cap_rate_forecast":
        return {
            "years": [2026, 2027, 2028, 2029, 2030],
            "caps":  [0.055, 0.057, 0.059, 0.061, 0.063],
            "plot_png": ""
        }

    # 2. NLQ → SQL tool
    if name == "nlq_to_sql":
        import re

        # pull user question
        full = payload["prompt"]["content"].lower()
        q    = full.split("question:")[-1].strip()
        tbl  = "real_estate_mock"

        # ─── Time-series: NOI series ────────────────────────────────
        if m := re.search(r"noi series of project\s*([a-zA-Z0-9_]+)", q):
            proj = m.group(1)
            return {
                "sql": (
                    f"SELECT fiscal_year AS year, value AS noi\n"
                    f"  FROM metrics_raw"
                    f" WHERE project_id = '{proj}'\n"
                    f"   AND metric = 'noi'\n"
                    f" ORDER BY fiscal_year"
                )
            }

        # ─── Field‐comparison mapping ────────────────────────────────
        FIELD_MAP = {
            "ltv":             "ltv",
            "ltc":             "ltc",
            "exit cap rate":   "exit_cap_rate",
            "cap rate":        "exit_cap_rate",
            "interest rate":   "interest_rate",
            "irr levered":     "irr_levered",
            "irr unlevered":   "irr_unlevered",
        }

        conds = []
        for fld, col in FIELD_MAP.items():
            pattern = rf"{re.escape(fld)}\s*(<|>)\s*([0-9]+(?:\.[0-9]+)?)\s*%?"
            for m in re.finditer(pattern, q):
                op, raw = m.group(1), m.group(2)
                val = float(raw)
                conds.append(
                    f"CAST(REPLACE({col}, '%','') AS REAL) {op} {val}"
                )

        if conds:
            sql = (
                f"SELECT *\n"
                f"  FROM {tbl}\n"
                f" WHERE " + " AND ".join(conds) + "\n"
                f" LIMIT 200"
            )
            return {"sql": sql}

        # ─── Fallback sample ────────────────────────────────────────
        return {"sql": f"SELECT * FROM {tbl} LIMIT 10"}

    # 3. All other tools (fallback)
    return {"message": f"stub response for tool '{name}'"}