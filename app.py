import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ALUETOO AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

# --- 2. STYLE CSS (DESIGN XXL & DÉGRADÉ) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .main .block-container {
        max-width: 900px !important;
        margin: auto !important;
    }
    
    /* Animation Ghost */
    @keyframes ghostFade {
        0% { opacity: 0; filter: blur(6px); }
        100% { opacity: 1; filter: blur(0px); }
    }
    .chat-text { font-size: 20px !important; color: #e6edf3; }
    .word-fade { display: inline-block; animation: ghostFade 1.2s ease-out forwards; white-space: pre-wrap; }

    /* TITRES XXL EN DEGRADE */
    .header-container { text-align: center; margin-bottom: 40px; line-height: 1.2; }
    
    .mega-title {
        font-weight: 900;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 65px; /* Très grand */
        display: block;
        margin-bottom: 10px;
    }

    .sub-mega-title {
        font-weight: 800;
        background: linear-gradient(to right, #00d4ff, #af40ff, #ff4b4b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 45px; /* Même taille que le bonjour */
        display: block;
    }

    /* Historique Important */
    .history-box {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid #30363d;
        border-radius: 25px;
        padding: 20px;
        margin-bottom: 30px;
    }

    div[data-testid="stChatInput"] { border-radius: 50px !important; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 4. HISTORIQUE EN HAUT (IMPORTANT) ---
with st.container():
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.markdown("### 📜 GESTION DES DISCUSSIONS")
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("✨ Nouvelle Discussion", use_container_width=True):
            if st.session_state.messages:
                st.session_state.all_chats.insert(0, st.session_state.messages)
            st.session_state.messages = []
            st.rerun()
    with c2:
        if st.session_state.all_chats:
            opts = [f"Ancienne Discussion {len(st.session_state.all_chats)-i}" for i in range(len(st.session_state.all_chats))]
            sel = st.selectbox("Historique :", ["Choisir..."] + opts, label_visibility="collapsed")
            if sel != "Choisir...":
                idx = len(st.session_state.all_chats) - int(sel.split()[-1])
                st.session_state.messages = st.session_state.all_chats[idx]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. HEADER XXL ---
st.markdown(f"""
    <div class="header-container">
        <div class="mega-title">ALUETOO AI</div>
        <div class="sub-mega-title">{salutation} (design mis à jour le 1 mars 2026)</div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. CHAT ---
active_fondu = st.toggle("Effet Ghost", value=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Pose ta question ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        instructions = "Tu es ALUETOO AI, une IA omnisciente créée par Léo Ciach. Tu sais tout."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": instructions}] + st.session_state.messages,
            stream=True 
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                if active_fondu:
                    display_html += f'<span class="word-fade">{text}</span>'
                    placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                    time.sleep(0.04)
                else:
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
