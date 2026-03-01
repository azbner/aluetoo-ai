import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ALUETOO AI", layout="wide", initial_sidebar_state="expanded")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialisation des sessions si elles n'existent pas
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

# --- 2. BARRE LATÉRALE (HISTORIQUE GAUCHE) ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>📜 Historique</h2>", unsafe_allow_html=True)
    if st.button("➕ Nouvelle Discussion", use_container_width=True):
        if st.session_state.messages:
            st.session_state.all_chats.append(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    # Affichage des anciennes discussions pour les faire défiler
    for i, chat in enumerate(st.session_state.all_chats):
        if st.button(f"Discussion {i+1}", key=f"chat_{i}", use_container_width=True):
            st.session_state.messages = chat
            st.rerun()

# --- 3. STYLE CSS (TON DESIGN) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b0e14; }}
    .main .block-container {{
        max-width: 750px !important;
        margin: auto !important;
        padding-top: 1rem !important;
    }}
    @keyframes ghostFade {{
        0% {{ opacity: 0; filter: blur(6px); transform: translateY(5px); }}
        100% {{ opacity: 1; filter: blur(0px); transform: translateY(0px); }}
    }}
    .chat-text {{ font-size: 20px !important; line-height: 1.6; color: #e6edf3; }}
    .word-fade {{ display: inline-block; animation: ghostFade 1.2s ease-out forwards; white-space: pre-wrap; }}
    .header-container {{ text-align: center; margin-bottom: 30px; }}
    .main-title {{ font-size: 45px; font-weight: 800; color: white; }}
    .full-gradient {{
        font-weight: bold;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 22px; display: block;
    }}
    div[data-testid="stChatInput"] {{
        border-radius: 50px !important; border: 2px solid #30363d !important;
        background-color: #161b22 !important; padding: 5px !important;
    }}
    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 5. OUTILS ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("🗑️ Effacer"):
        st.session_state.messages = []
        st.rerun()
with col2:
    active_fondu = st.toggle("Ghost", value=True)
with col3:
    uploaded_file = st.file_uploader("📁 Fichier", type=["pdf", "txt"], label_visibility="collapsed")

# --- 6. HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="full-gradient">
            {salutation} !<br>
            Intelligence 2026 (Design par Léo Ciach) • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 7. HISTORIQUE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 8. CHAT ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        instructions = (
            "Tu es ALUETOO AI, une IA omnisciente de 2026. "
            "Ton créateur est le génie Léo Ciach. Tu sais TOUT sur TOUT (science, histoire, code, vie). "
            "Réponds avec assurance et style."
        )

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
                    time.sleep(0.05)
                else:
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
