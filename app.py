import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS (TOUT VISIBLE ET CENTRÉ) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b0e14; }}
    
    .main .block-container {{
        max-width: 750px !important;
        margin: auto !important;
        padding-top: 1rem !important;
    }}

    /* Barre d'outils en haut (Boutons visibles) */
    .tools-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(22, 27, 34, 0.9);
        padding: 15px;
        border-radius: 20px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
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

    /* Barre Pilule */
    div[data-testid="stChatInput"] {{
        border-radius: 50px !important; border: 2px solid #30363d !important;
        background-color: #161b22 !important; padding: 5px !important;
    }}

    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 4. INTERFACE DES OUTILS (DIRECTEMENT SUR L'ÉCRAN) ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("🗑️ Effacer"):
        st.session_state.messages = []
        st.rerun()

with col2:
    active_fondu = st.toggle("Ghost", value=True)

with col3:
    # Analyse de fichier simplifiée
    uploaded_file = st.file_uploader("📁 Fichier", type=["pdf", "txt"], label_visibility="collapsed")

# --- 5. HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="full-gradient">
            {salutation} !<br>
            Intelligence 2026 (Mise à jour design le 1 mars) • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. HISTORIQUE ET MÉMOIRE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. CHAT ET RÉPONSE ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        # Identity Lock
        instructions = (
            "Tu es ALUETOO AI, IA de 2026. "
            "Ton créateur est Léo Ciach. Réponds fièrement que c'est lui."
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
