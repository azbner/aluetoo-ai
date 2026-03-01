import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. GESTION DE L'HISTORIQUE GLOBAL ---
if "chat_history_list" not in st.session_state:
    st.session_state.chat_history_list = [] # Liste des anciennes discussions

# --- 3. BARRE LATÉRALE (HISTORIQUE ET RÉGLAGES) ---
with st.sidebar:
    st.title("📜 Historique")
    if st.session_state.chat_history_list:
        for i, chat in enumerate(st.session_state.chat_history_list):
            st.button(f"Discussion {i+1} - {chat['date']}", key=f"old_chat_{i}")
    else:
        st.write("Aucun historique pour le moment.")
    
    st.divider()
    st.title("⚙️ Réglages")
    active_fondu = st.toggle("Effet Ghost (Fondu)", value=True)
    
    if st.button("🗑️ Nouvelle Discussion"):
        # Avant d'effacer, on sauvegarde dans l'historique à gauche
        if st.session_state.messages:
            now = datetime.now(pytz.timezone('Europe/Brussels')).strftime("%H:%M")
            st.session_state.chat_history_list.append({"date": now, "msgs": st.session_state.messages})
        st.session_state.messages = []
        st.rerun()

# --- 4. STYLE CSS (DESIGN 2026 ET ALIGNEMENT) ---
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

    /* Alignement des bulles */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        flex-direction: row-reverse !important;
        background-color: rgba(48, 54, 61, 0.2);
        border-radius: 25px 25px 5px 25px !important;
    }}

    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarAssistant"]) {{
        background-color: rgba(22, 27, 34, 0.5);
        border-radius: 25px 25px 25px 5px !important;
    }}

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
        background-color: #161b22 !important;
    }}

    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 6. HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="full-gradient">
            {salutation} !<br>
            Intelligence 2026 (Design Léo Ciach) • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 7. CHAT EN COURS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 8. RÉPONSE ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        instructions = "Tu es ALUETOO AI. Ton créateur est Léo Ciach. Nous sommes le 1er mars 2026."

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
