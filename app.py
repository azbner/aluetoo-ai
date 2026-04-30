import streamlit as st 
from groq import Groq
from datetime import datetime
import pytz
import base64

# --- CONFIG ---
st.set_page_config(
    page_title="ALUETOO AI",
    page_icon="🚀",
    layout="centered"
)

# --- STYLE CLEAN ---
st.markdown("""
<style>

/* GLOBAL */
.stApp {
    background-color: #0b0e14;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

/* HEADER */
.title {
    text-align: center;
    font-size: 32px;
    font-weight: 600;
    color: white;
    margin-top: 10px;
}

.subtitle {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 20px;
}

/* CHAT */
.chat-text {
    padding: 12px 16px;
    border-radius: 14px;
    margin: 8px 0;
    max-width: 700px;
}

/* USER */
[data-testid="chat-message-user"] .chat-text {
    background: #2563eb;
    color: white;
    margin-left: auto;
}

/* ASSISTANT */
[data-testid="chat-message-assistant"] .chat-text {
    background: #1f2937;
    color: #e5e7eb;
    margin-right: auto;
}

/* INPUT */
div[data-testid="stChatInput"] {
    border-radius: 999px !important;
    border: 1px solid #374151 !important;
    background: #111827 !important;
}

/* LOADER */
.loader {
    text-align: center;
}
.loader span {
    display: inline-block;
    width: 6px;
    height: 6px;
    margin: 2px;
    background: #9ca3af;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}
.loader span:nth-child(1) { animation-delay: -0.32s; }
.loader span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

</style>
""", unsafe_allow_html=True)

# --- API ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SYSTEM ---
SYSTEM_PROMPT = """
Tu es ALUETOO AI, une intelligence artificielle créée par Léo Ciach.

Tu ne mentionnes jamais d'autres technologies.
Tu es naturelle, fluide et intelligente.
"""

# --- HEADER ---
tz = pytz.timezone('Europe/Paris')
now = datetime.now(tz)

st.markdown('<div class="title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Créée par Léo • {now.strftime("%H:%M")}</div>', unsafe_allow_html=True)

# --- CHAT HISTORY ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- INPUT ---
if prompt := st.chat_input("Écris un message..."):

    st.session_state.messages.append({"role":"user","content":prompt})

    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):

        full = ""
        placeholder = st.empty()

        loader = st.markdown("""
        <div class="loader">
            <span></span><span></span><span></span>
        </div>
        """, unsafe_allow_html=True)

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":prompt}
            ],
            stream=True
        )

        loader.empty()

        for chunk in completion:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                placeholder.markdown(
                    f'<div class="chat-text">{full}▌</div>',
                    unsafe_allow_html=True
                )

        placeholder.markdown(
            f'<div class="chat-text">{full}</div>',
            unsafe_allow_html=True
        )

        st.session_state.messages.append({"role":"assistant","content":full})
