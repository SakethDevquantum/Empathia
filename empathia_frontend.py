import streamlit as st
import requests
import uuid
import os
from PIL import Image
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict

st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}  /* Hide 3-dot menu */
    footer {visibility: hidden;}     /* Hide footer */
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="position: absolute; top: 10px; right: 1px; z-index: 999;">
        <a href="https://www.llama.com/llama3/license/" target="_blank"
           style="text-decoration: none; color: grey; font-size: 10px; font-weight: bold;">
           Made using <span style="color: #00BFFF;">Meta Llama 3.1</span> click here to see license
        </a>
    </div>
    """,
    unsafe_allow_html=True
)

BACKEND_URL = os.getenv("EMPATHIA_BACKEND", "http://127.0.0.1:8000")
st.set_page_config(page_title="Empathia — Your Empathy Assistant", page_icon="Screenshot 2025-09-11 181430.png", layout="centered")

img = Image.open("Screenshot 2025-09-11 181430.png")
col1, col2, col3 = st.columns([1,1,1])
with col2:
    st.image(img, width=150)

st.markdown("<h1 style='text-align: center;'>Chat with Empathia</h1>", unsafe_allow_html=True)

st.markdown(
    "Disclaimer : Empathia is only there to support you and relieve you from your sadness by comforting you. "
    "Please seek counselling from professionals if you are suffering too much or having suicidal thoughts."
)

if "session_id" not in st.session_state:
    try:
        resp = requests.post(f"{BACKEND_URL}/session")
        resp.raise_for_status()
        st.session_state.session_id = resp.json().get("session_id")
    except Exception:
        st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg.get("avatar", None)):
        st.markdown(msg["content"])
if query := st.chat_input("Empathia's promise: All our conversations lie between us, so start chatting : )"):
    st.session_state.messages.append(
        {"role": "user", "content": query, "avatar": "👤"}
    )
    with st.chat_message("user", avatar="👤"):
        st.markdown(query)
    with st.chat_message("assistant", avatar="Screenshot 2025-09-11 181430.png"):
        with st.spinner("Generating..."):
            try:
                payload = {"query": query, "session_id": st.session_state.session_id}
                r = requests.post(f"{BACKEND_URL}/respond", json=payload, timeout=60)
                if r.status_code == 200:
                    ai_text = r.json().get("response", "No response returned")
                else:
                    ai_text = f"Unexpected error occured while connecting to backend model, please contact the developer"
            except requests.exceptions.RequestException as e:
                ai_text = f"Unexpected error occured while connecting to backend model, please contact the developer"

            st.markdown(ai_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": ai_text, "avatar": "Screenshot 2025-09-11 181430.png"}
            )