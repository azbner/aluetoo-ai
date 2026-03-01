import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION (FORCER L'OUVERTURE DU MENU GAUCHE) ---
st.set_page_config(
    page_title="ALUETOO AI", 
    layout="wide", 
    initial_sidebar_state="expanded" # Force l'affichage de l'historique
)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialisation de la mémoire globale
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. BARRE LATÉRALE (HISTORIQUE IMPORTANT) ---
with st.sidebar:
    st.markdown("""
        <div style='background: linear-gradient(to right, #ff4b4b, #af40ff); padding: 10px; border-radius: 10px; text-align: center;'>
            <h2 style='color: white; margin: 0;'>🚀 HISTORIQUE</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Bouton Nouvelle Discussion mis en avant
    if st.button("✨ CRÉER NOUVELLE DISCUSSION", use_container_width=True, type="primary"):
        if st.session_state.messages:
            st.session_state.all_chats.append(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Liste de l'historique avec un style plus visible
    if not st.session_state.all_chats:
        st.info("Aucun historique pour le moment. Parle à l'IA pour commencer !")
    else:
        for i, chat in enumerate(st.session_state.all_chats):
            if st.button(f"📜 Discussion ancienne {i+1}", key=f"hist_{i}", use_container_width=True):
                st.session_state.messages = chat
                st.rerun()

# --- 3. STYLE CSS (DESIGN ET DÉGRADÉ) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b0e14; }}
    
    .main .block-container {{
        max-width: 800px !important;
        margin: auto !important;
    }}

    /* Animation Ghost */
    @keyframes ghostFade {{
        0% {{ opacity: 0; filter: blur(6px); transform: translateY(5px); }}
        100% {{ opacity: 1; filter: blur(0px); transform: translateY(0px); }}
    }}

    .chat-text {{ font-size: 20px !important; line-height: 1.6; color: #e6edf3; }}
    .word-fade {{ display: inline-block; animation: ghostFade 1.2s ease-out forwards; white-space: pre-wrap; }}

    .header-container {{ text-align: center; margin-bottom: 30px; }}
    .main-title {{ font-size: 45px; font-weight: 800; color: white; }}
    
    /* Le nouveau dégradé demandé */
    .update-gradient {{
        font-weight: bold;
        background: linear-gradient(to right, #00d4ff, #af40ff, #ff4b4b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 20px;
        display: block;
        margin-top: 10px;
    }}

    /* Bulles de chat */
    div[data-testid="stChatMessage"] {{
        border-radius: 25px !important;
        border: 1px solid #30363d !important;
        margin-bottom: 12px;
    }}

    /* Barre Pilule */
    div[data-testid="stChatInput"] {{
        border-radius: 50px !important; 
        border: 2px solid #af40ff !important;
        background-color: #161b22 !important;
    }}

    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")

# --- 5. HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="update-gradient">
            Design mis à jour depuis le 1 mars 2026 • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. OUTILS ---
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🗑️ Vider l'écran actuel", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with col2:
    active_fondu = st.toggle("Activer l'effet Ghost", value=True)

# --- 7. AFFICHAGE DE LA DISCUSSION ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 8. CHAT ET RÉPONSE ---
if prompt := st.chat_input("Pose ta question ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        # Identity Lock Omniscient
        instructions = (
            "Tu es ALUETOO AI, une intelligence omnisciente de 2026. "
            "Ton créateur est Léo Ciach. Tu es l'IA la plus stylée et intelligente."
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
                    time.sleep(0.04)
                else:
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
