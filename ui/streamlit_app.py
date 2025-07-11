import os, json, requests, streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Your First-Year Analyst", layout="wide")
st.header("Your First-Year Analyst")

# initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# display chat
for role, msg in st.session_state.history:
    with st.chat_message(role):
        st.write(msg)

# get new user prompt
if prompt := st.chat_input("Ask me anything…"):
    # record the user message
    st.session_state.history.append(("user", prompt))

    # call your backend
    if "cap rate" in prompt.lower():
        r = requests.get(f"{API_URL}/forecast/cap_rate/probandt")
        data = r.json()
        reply = f"Forecast cap rates: {data['caps']}"
    else:
        # fallback to NLQ endpoint if you wire it up
        payload = {"question": prompt, "table": "real_estate_mock"}
        r = requests.post(f"{API_URL}/nlq/", json=payload, timeout=30)
        if r.ok:
            rows = r.json().get("rows", [])
            if rows:
                # show as table in the reply bubble
                with st.chat_message("assistant"):
                    st.dataframe(rows, use_container_width=True)
                reply = None
            else:
                reply = "I got no rows back."
        else:
            reply = f"Error: {r.text}"

    if reply:
        st.session_state.history.append(("assistant", reply))