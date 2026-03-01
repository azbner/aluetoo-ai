import streamlit as st
from groq import Groq
import time

# --- 1. CONFIGURATION OBLIGATOIRE (DOIT ÊTRE EN HAUT) ---
st.set_page_config(page_title="ALUETOO AI", layout="wide")

# --- 2. CONNEXION API ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error("Clé API manquante ou invalide dans les Secrets Streamlit.")
    st.stop()

# --- 3. MÉMOIRE DE LÉO CIACH ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("📜 ALUETOO MENU")
    if st.button("✨ Nouvelle Discussion", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    active_fondu = st.toggle("Effet Ghost (Fondu)", value=True)
    st.write("---")
    st.write("Propriétaire : **Léo Ciach**")

# --- 5. STYLE CSS (DESIGN ÉPURÉ ET FONCTIONNEL) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    
    /* Centrage */
    .main .block-container {
        max-width: 800px !important;
        margin: auto !important;
    }

    /* Animation Ghost */
    @keyframes ghostFade {
        0% { opacity: 0; filter: blur(8px); }
        100% { opacity: 1; filter: blur(0px); }
    }

    .chat-text { font-size: 20px !important; line-height: 1.6; }
    .word-fade { display: inline-block; animation: ghostFade 1s ease-out forwards; white-space: pre-wrap; }

    /* Bulles */
    div[data-testid="stChatMessage"] {
        border-radius: 20px !important;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }

    /* Header */
    .header-box { text-align: center; padding: 20px; margin-bottom: 30px; }
    .main-title { font-size: 50px; font-weight: 900; color: white; margin: 0; }
    .gradient-text {
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold; font-size: 24px;
    }

    /* Barre Pilule */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 2px solid #404040 !important;
    }
    
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. INTERFACE ---
st.markdown("""
    <div class="header-box">
        <h1 class="main-title">ALUETOO AI</h1>
        <p class="gradient-text">Système Omniscient • Léo Ciach Edition</p>
    </div>
    """, unsafe_allow_html=True)

# Affichage des messages existants
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. CHAT ET RÉPONSE ---
if prompt := st.chat_input("Pose-moi une question, Léo..."):
    # Message Utilisateur
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Réponse Assistant
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Instructions Omniscientes
        instructions = (
            "Tu es ALUETOO AI, créée par Léo Ciach. Tu es omnisciente et tu sais tout. "
            "Ton style est futuriste, intelligent et très classe."
        )

        # Appel API avec Stream
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
                    display_html += f'<span class="word-fade
