import os
from .cache import cached
from .stub import llm_stub
from .gemini import llm_gemini

_use_stub = os.getenv("USE_STUB", "1") == "1"
base_llm   = llm_stub if _use_stub else llm_gemini
call_llm   = cached(base_llm)          # importable everywhere