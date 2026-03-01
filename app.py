import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS (CENTRAGE, SWITCH À DROITE ET PILULE) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }

    /* Centrage de la page */
    .main .block-container {
        max-width: 750px !important;
        margin: auto !important;
        padding-top: 1rem !important;
    }

    /* Positionnement du Switch en haut à droite */
    .stToggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: rgba(22, 27, 34, 0.8);
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #30363d;
    }

    /* Animation Ghost */
    @keyframes ghostFade {
        0% { opacity: 0; filter: blur(6px); }
        100% { opacity: 1; filter: blur(0px); }
    }

    /* Texte du chat stable à 20px */
    .chat-text {
        font-size: 20px !important;
        line-height: 1.6;
        color: #e6edf3;
    }

    .word-fade {
        display: inline-block;
        animation: ghostFade 1.2s ease-out forwards;
        white-space: pre-wrap;
    }

    /* Header centré */
    .header-container { text-align: center; margin-bottom: 40px; }
    .main-title { font-size: 45px; font-weight: 800; color: white; }
    .full-gradient {
        font-weight: bold;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 22px;
        display: block;
    }

    /* Barre Pilule */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important; 
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
        padding: 5px !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        border-radius: 50px !important;
        padding-left: 20px !important;
        font-size: 18px !important;
    }

    /* Style des bulles de chat */
    .stChatMessage { 
        border-radius: 25px !important; 
        border: 1px solid #1f2328;
        margin-bottom: 10px;
    }

    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 4. LE SWITCH (Visible sur l'écran) ---
active_fondu = st.toggle("Effet Ghost", value=True)

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

# --- 6. MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. RÉPONSE ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es ALUETOO AI."}] + st.session_state.messages,
            stream=True 
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                
                if active_fondu:
                    display_html += f'<span class="word-fade">{text}</span>'
                    placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                    time.sleep(0.06)
                else:
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
