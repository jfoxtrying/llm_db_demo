def llm_stub(payload: dict) -> dict:
    """
    Development stub that mimics Gemini JSON output
    without spending tokens.
    """
    name = payload.get("name")
    if name == "get_cap_rate_forecast":
        return {
            "years": [2026, 2027, 2028, 2029, 2030],
            "caps":  [0.055, 0.057, 0.059, 0.061, 0.063],
            "plot_png": ""
        }
    return {"message": "stub response"}