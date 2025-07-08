import os, google.generativeai as genai

print(genai.__version__)

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def llm_gemini(payload: dict) -> dict:
    """
    Real call to Gemini (function-calling style).
    """
    response = genai.chat.completions.create(
        model="gemini-1.5-pro",
        tools=[{"name": payload["name"], "parameters": payload["args_schema"]}],
        messages=[payload["prompt"]],
    )
    return response.choices[0].message.tool_calls[0].function_response