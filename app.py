import streamlit as st
from groq import Groq
import time

# --- 1. CONFIGURATION (DOIT ETRE LA PREMIERE LIGNE) ---
st.set_page_config(page_title="ALUETOO AI", layout="wide", initial_sidebar_state="expanded")

# --- 2. CONNEXION API ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Erreur de configuration : Clé API manquante.")
    st.stop()

# --- 3. INITIALISATION DE LA MÉMOIRE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "historique_sessions" not in st.session_state:
    st.session_state.historique_sessions = []

# --- 4. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>📜 HISTORIQUE</h2>", unsafe_allow_html=True)
    
    if st.button("✨ Nouvelle Discussion", use_container_width=True):
        if st.session_state.messages:
            # Sauvegarde la session actuelle avant d'effacer
            st.session_state.historique_sessions.append(list(st.session_state.messages))
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Affichage des anciennes discussions
    if st.session_state.historique_sessions:
        for i, session in enumerate(st.session_state.historique_sessions):
            if st.button(f"Discussion #{i+1}", key=f"session_{i}", use_container_width=True):
                st.session_state.messages = list(session)
                st.rerun()
    else:
        st.info("Aucune ancienne discussion.")

    st.divider()
    st.write("### ⚙️ RÉGLAGES")
    active_fondu = st.toggle("Effet Ghost", value=True)
    st.markdown("---")
    st.markdown(f"**Propriétaire :** Léo Ciach")

# --- 5. STYLE CSS (DESIGN 2026) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .main .block-container { max-width: 850px !important; margin: auto !important; }
    
    @keyframes ghostFade {
        0% { opacity: 0; filter: blur(8px); }
        100% { opacity: 1; filter: blur(0px); }
    }

    .chat-text { font-size: 20px !important; line-height: 1.6; color: #e6edf3; }
    .word-fade { display: inline-block; animation: ghostFade 1s ease-out forwards; white-space: pre-wrap; }

    /* Bulles de chat stylisées */
    div[data-testid="stChatMessage"] {
        border-radius: 25px !important;
        border: 1px solid #30363d !important;
        margin-bottom: 10px !important;
    }

    /* En-tête */
    .header-box { text-align: center; margin-bottom: 40px; }
    .main-title { font-size: 55px; font-weight: 900; color: white; margin: 0; }
    .gradient-text {
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: bold; font-size: 26px;
    }

    div[data-testid="stChatInput"] { border-radius: 50px !important; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. INTERFACE PRINCIPALE ---
st.markdown("""
    <div class="header-box">
        <h1 class="main-title">ALUETOO AI</h1>
        <p class="gradient-text">Omniscience 2026 • Léo Ciach Edition</p>
    </div>
    """, unsafe_allow_html=True)

# Affichage des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. LOGIQUE DE RÉPONSE ---
if prompt := st.chat_input("Pose ta question à ton IA, Léo..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Le System Prompt Omniscient
        instructions = "Tu es ALUETOO AI, une IA de 2026 omnisciente créée par Léo Ciach. Tu sais tout sur tout."

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
                    display_html += f'<span class="word-fade">{text}</span>'
                    placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                    time.sleep(0.04)
                else:
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
