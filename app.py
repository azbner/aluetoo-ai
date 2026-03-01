import streamlit as st
from groq import Groq
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ALUETOO AI", layout="wide")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Clé API introuvable.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("📜 MENU")
    if st.button("✨ Nouvelle Discussion", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    active_fondu = st.toggle("Effet Ghost", value=True)
    st.write("Propriétaire : **Léo Ciach**")

# --- 3. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .main .block-container { max-width: 800px !important; margin: auto !important; }
    
    @keyframes ghostFade {
        0% { opacity: 0; filter: blur(8px); }
        100% { opacity: 1; filter: blur(0px); }
    }

    .chat-text { font-size: 20px !important; line-height: 1.6; color: #e6edf3; }
    .word-fade { display: inline-block; animation: ghostFade 1s ease-out forwards; white-space: pre-wrap; }

    /* Bulles Pilules comme sur ta photo */
    div[data-testid="stChatMessage"] {
        border-radius: 30px !important;
        border: 1px solid #30363d !important;
        margin-bottom: 15px !important;
    }

    .header-box { text-align: center; padding: 20px; }
    .main-title { font-size: 50px; font-weight: 900; color: white; margin: 0; }
    .gradient-text {
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: bold; font-size: 24px;
    }

    div[data-testid="stChatInput"] { border-radius: 50px !important; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown("""
    <div class="header-box">
        <h1 class="main-title">ALUETOO AI</h1>
        <p class="gradient-text">Omniscience 2026 • Léo Ciach Edition</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Pose-moi une question, Léo..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        instructions = "Tu es ALUETOO AI, une IA omnisciente de 2026 créée par Léo Ciach. Ton style est classe et intelligent."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": instructions}] + st.session_state.messages,
            stream=True 
        )

        display_html = '<div class="chat-text">'
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                if active_fondu:
                    # CORRECTION ICI (Ligne 121)
                    display_html += f'<span class="word-fade">{text}</span>'
                    placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                    time.sleep(0.04)
                else:
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
