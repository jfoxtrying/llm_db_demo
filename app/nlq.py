from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from app.db import get_company_db          # existing session dependency
from llm_layer import call_llm             # stub or Gemini

router = APIRouter(prefix="/nlq")

class NLQReq(BaseModel):
    question: str

@router.post("/")
def run_nlq(req: NLQReq, db = Depends(get_company_db)):
    # 1· Ask LLM to turn question → safe SQL
    payload = {
        "name": "nlq_to_sql",
        "prompt": {
            "role": "user",
            "content": (
                "Translate the question into a single **read-only** SQL query "
                "against table 'metrics_raw' (columns: project_id,fiscal_year,metric,value,unit). "
                "Return JSON {sql:\"…\"}. Question: " + req.question
            )
        },
        "args_schema": {}          # no args needed
    }
    res = call_llm(payload)        # stub ⇒ canned SQL, Gemini ⇒ real
    sql = res["sql"]

    # basic allow-list safety
    if any(k in sql.lower() for k in ("update", "delete", "insert", ";")):
        raise HTTPException(400, "Illegal SQL")

    rows = db.execute(text(sql)).fetchall()
    return {"sql": sql, "rows": [dict(r) for r in rows]}