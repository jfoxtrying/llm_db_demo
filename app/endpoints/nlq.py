# app/endpoints/nlq.py   (replace the old file)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from app.db import get_company_db
from llm_layer import call_llm

router = APIRouter(prefix="/nlq", tags=["Natural-Language SQL"])

SAFE_TABLES = {
    "real_estate_mock": [
        "property_id", "property_name", "property_type", "location",
        "project_year", "exit_year", "exit_cap_rate", "interest_rate",
        "noi", "purchase_price_value", "ltv", "ltc", "rental_growth_assumption",
        "irr_unlevered", "irr_levered"
    ],
    "metrics_raw": [  # still there for other questions
        "project_id", "fiscal_year", "metric", "value", "unit"
    ]
}

class NLQReq(BaseModel):
    question: str
    table:    str = "real_estate_mock"   # default

@router.post("/")
def run_nlq(req: NLQReq, db=Depends(get_company_db)):
    if req.table not in SAFE_TABLES:
        raise HTTPException(400, f"Unsupported table {req.table}")

    # 1── Ask LLM to translate the question to safe SQL
    payload = {
     "name": "nlq_to_sql",
     "prompt": {
         "role": "user",
         "content": (
             "Translate the question into a single **read-only** SQL query … "
             f"Question: {req.question}"
         )
     },
     "args_schema": {},

     "question": req.question          # ← plain text for the stub / LLM
 }
    print("NLQ payload name =", payload["name"])   # just before call_llm(...)
    res = call_llm(payload)            # ❸
    sql = res.get("sql")
    if not sql:
        raise HTTPException(500, f"LLM bad: {res!r}")

    # 2── Guard-rails
    lowered = sql.lower()
    if any(k in lowered for k in ("update", "delete", "insert", "drop", ";")):
        raise HTTPException(400, "Illegal SQL verb")
    if "limit" not in lowered:
        sql += " LIMIT 200"             # auto-limit

    rows = db.execute(text(sql)).mappings().all()
    return {"sql": sql, "rows": rows}