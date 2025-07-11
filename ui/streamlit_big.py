import streamlit as st
import pandas as pd
import requests, os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(layout="wide")
st.header("Tester for LLM-API")

# 1. Make sure we have a place to store every turn
if "history" not in st.session_state:
    st.session_state.history = []

# 2. Capture *new* user input **first**, before rendering history
user_input = st.chat_input("Ask me anything…")
if user_input:
    # stash the user message
    st.session_state.history.append({
        "role": "user",
        "type": "user",
        "text": user_input
    })

    # call the backend right away
    resp = (
        requests.post(f"{API_URL}/mc/",
                      json={"project_id": "probandt","n_draws":8000})
        if any(k in user_input.lower() for k in ["monte","sim","probability"])
        else requests.post(f"{API_URL}/nlq/",
                            json={"question": user_input, "table":"real_estate_mock"})
    )

    if not resp.ok:
        out = {"role":"assistant","type":"error","text":resp.text}
    else:
        body = resp.json()
        if "rows" in body:
            out = {"role":"assistant","type":"nlq","sql": body["sql"],"rows":body["rows"]}
        else:
            out = {"role":"assistant","type":"mc",
                   "text":f"P(exit-cap<target): {body['p_below_target']:.1%}",
                   "img": body["hist_png"]}

    st.session_state.history.append(out)

# 3. Now render *all* turns, including the one we just added
for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        if turn["type"] == "user":
            st.markdown(f"**You:** {turn['text']}")
        elif turn["type"] == "error":
            st.error(turn["text"])
        elif turn["type"] == "mc":
            st.markdown(turn["text"])
            st.image(turn["img"], use_column_width=True)
        else:  # nlq
               st.markdown(f"**SQL I ran:**\n```sql\n{turn['sql']}\n```")
               rows = turn.get("rows", [])
               if not rows:
                    st.info("No rows returned.")
               else:
                    df = pd.DataFrame(rows)

                    # if it's an NOI time-series, plot it

                    df = df.sort_values("year")
                    st.line_chart(
                        df.set_index("year")["noi"],
                        use_container_width=True
                    )
                    # otherwise, show as table