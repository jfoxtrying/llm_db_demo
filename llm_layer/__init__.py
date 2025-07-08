import os
from .cache import cached
from .stub import llm_stub

_use_stub = os.getenv("USE_STUB", "1") == "1"

if _use_stub:
    base_llm = llm_stub
else:
    from .gemini import llm_gemini
    base_llm = llm_gemini

call_llm = cached(base_llm)