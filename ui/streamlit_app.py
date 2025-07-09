# ui/streamlit_app.py
import os, json, requests, streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")

st.set_page_config(page_title="Your First-Year Analyst",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("<h2 style='font-weight:400;'>Your&nbsp;First-Year&nbsp;Analyst</h2>",
            unsafe_allow_html=True)
st.divider()

if "history" not in st.session_state:
    st.session_state.history = []

def call_backend(question: str) -> str:
    # Simple routing demo – expand with real intent detection later
    if "cap rate" in question.lower():
        r = requests.get(f"{API_URL}/forecast/cap_rate/probandt")
        data = r.json()
        return f"Forecast cap rates: {data['caps']}"
    else:
        return "Sorry, I only know cap rates as of right now!"

prompt = st.chat_input("Ask me anything…")
if prompt:
    st.session_state.history.append(("user", prompt))
    answer = call_backend(prompt)
    st.session_state.history.append(("bot", answer))

for role, text in st.session_state.history:
    align = "flex-start" if role == "bot" else "flex-end"
    st.markdown(
        f"<div style='display:flex; justify-content:{align}; "
        f"margin:4px 0;'><div style='background:#f5f5f5; "
        f"border-radius:8px; padding:8px 12px; "
        f"max-width:60ch;'>{text}</div></div>",
        unsafe_allow_html=True
    )
# Streamlit theme configuration can be set in the `.streamlit/config.toml` file.
# Remove this block as it is misplaced in the Python code.
    # The import statements are already present at the top of the file.
    # You can safely remove this redundant import block.

API_URL = os.getenv("API_URL", "http://127.0.0.1:8001")

def fetch_notes():
    try:
        return requests.get(f"{API_URL}/notes").json()
    except Exception as e:
        st.error(f"API error: {e}")
        return []

if st.button("Show notes"):
    notes = fetch_notes()
    st.table(notes)