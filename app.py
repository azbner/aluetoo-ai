import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION GROQ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. INITIALISATION DE LA MÉMOIRE (HISTORIQUE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []

# --- 3. BARRE LATÉRALE (SIDEBAR) ---
# Si tu ne la vois pas, clique sur la petite flèche ">" en haut à gauche de ton écran
with st.sidebar:
    st.title("📜 Historique")
    st.write("Sessions de Léo Ciach")
    
    if st.button("➕ Nouvelle Discussion"):
        if st.session_state.messages:
            st.session_state.chat_sessions.append(st.session_state.messages)
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.title("⚙️ Réglages")
    active_fondu = st.toggle("Effet Ghost", value=True)
    
    st.divider()
    st.info("Créateur : Léo Ciach\nVersion : Intelligence 2026")

# --- 4. STYLE CSS (CENTRAGE ET DESIGN) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b0e14; }}
    
    /* Force le centrage du chat */
    .main .block-container {{
        max-width: 800px !important;
        margin: auto !important;
        display: block !important;
    }}

    /* Animation Ghost */
    @keyframes ghostFade {{
        0% {{ opacity: 0; filter: blur(6px); transform: translateY(5px); }}
        100% {{ opacity: 1; filter: blur(0px); transform: translateY(0px); }}
    }}

    .chat-text {{ font-size: 20px !important; line-height: 1.6; color: #e6edf3; }}
    .word-fade {{ display: inline-block; animation: ghostFade 1.2s ease-out forwards; white-space: pre-wrap; }}

    /* Bulles : Assistant à gauche, User à droite */
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
        flex-direction: row-reverse !important;
        background-color: rgba(48, 54, 61, 0.2) !important;
    }}

    /* Header */
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

# --- 7. AFFICHAGE DES MESSAGES ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 8. ENTREE CHAT ET RÉPONSE ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        instructions = "Tu es ALUETOO AI. Ton créateur est Léo Ciach. Tu es une IA de 2026."

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
