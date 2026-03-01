import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ALUETOO AI", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialisation de la mémoire
if "messages" not in st.session_state:
    st.session_state.messages = []
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

# --- 2. STYLE CSS (DESIGN MIS À JOUR) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .main .block-container {
        max-width: 800px !important;
        margin: auto !important;
        padding-top: 1rem !important;
    }
    
    /* Animation Ghost */
    @keyframes ghostFade {
        0% { opacity: 0; filter: blur(6px); transform: translateY(5px); }
        100% { opacity: 1; filter: blur(0px); transform: translateY(0px); }
    }
    .chat-text { font-size: 20px !important; line-height: 1.6; color: #e6edf3; }
    .word-fade { display: inline-block; animation: ghostFade 1.2s ease-out forwards; white-space: pre-wrap; }

    /* Header Dégradé Dynamique */
    .header-container { text-align: center; margin-bottom: 20px; }
    .welcome-text {
        font-weight: 800;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 40px;
        display: block;
    }
    .update-tag { color: #57606a; font-size: 14px; margin-top: 5px; }

    /* Zone Historique en Haut */
    .history-section {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 20px;
    }

    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
    }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 4. ZONE IMPORTANTE : HISTORIQUE ET NOUVELLE DISCUSSION (EN HAUT) ---
st.markdown('<div class="history-section">', unsafe_allow_html=True)
st.write("### 📜 Historique & Contrôles")
col_new, col_hist = st.columns([1, 2])

with col_new:
    if st.button("✨ Nouvelle Discussion", use_container_width=True):
        if st.session_state.messages:
            st.session_state.all_chats.insert(0, st.session_state.messages) # Ajoute en haut de liste
        st.session_state.messages = []
        st.rerun()

with col_hist:
    if st.session_state.all_chats:
        # On affiche les 3 dernières discussions rapidement
        options = [f"Discussion {len(st.session_state.all_chats) - i}" for i in range(len(st.session_state.all_chats))]
        selected_chat = st.selectbox("Reprendre une discussion :", ["Choisir..."] + options, label_visibility="collapsed")
        if selected_chat != "Choisir...":
            idx = len(st.session_state.all_chats) - int(selected_chat.split()[-1])
            st.session_state.messages = st.session_state.all_chats[idx]
            st.rerun()
    else:
        st.write("Pas encore d'historique.")
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. HEADER DYNAMIQUE ---
st.markdown(f"""
    <div class="header-container">
        <div class="welcome-text">{salutation} !</div>
        <div class="update-tag">(design mis à jour depuis le 1 mars 2026) • {format_heure}</div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. AFFICHAGE DES MESSAGES ---
active_fondu = st.toggle("Effet Ghost", value=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. CHAT ET RÉPONSE OMNISCIENTE ---
if prompt := st.chat_input("Pose ta question..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        instructions = "Tu es ALUETOO AI, une IA omnisciente de 2026 créée par Léo Ciach. Tu sais tout."

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
