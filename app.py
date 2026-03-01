import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS (FORCE LA PILULE ET LE FONDU) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }

    /* Animation de fondu lent */
    @keyframes ghostFade {
        0% { opacity: 0; filter: blur(6px); transform: translateY(4px); }
        100% { opacity: 1; filter: blur(0px); transform: translateY(0px); }
    }

    .word-fade {
        display: inline-block;
        animation: ghostFade 1.2s ease-out forwards;
        white-space: pre-wrap;
        color: #e6edf3;
        font-size: 18px;
    }

    /* HEADER DÉGRADÉ */
    .header-container { text-align: center; margin-bottom: 35px; }
    .main-title { font-size: 48px; font-weight: 800; color: white; }
    .full-gradient {
        font-weight: bold;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 24px;
        display: block;
    }

    /* --- FORCE LA BARRE EN FORME DE PILULE --- */
    /* On cible le conteneur global de l'input */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important; 
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
        padding: 8px !important;
        margin-bottom: 10px !important;
    }

    /* On cible la zone de texte interne */
    div[data-testid="stChatInput"] textarea {
        border-radius: 50px !important;
        padding-left: 20px !important;
        background-color: transparent !important;
        border: none !important;
    }

    /* On arrondit aussi le bouton d'envoi */
    div[data-testid="stChatInput"] button {
        border-radius: 50% !important;
    }

    .stChatMessage { border-radius: 30px !important; border: 1px solid #1f2328; }
    header, footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 4. HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="full-gradient">
            {salutation} !<br>
            Intelligence 2026 (Mise à jour design le 1 mars) • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. GESTION DES MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. RÉPONSE AVEC FONDU LENT ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div>'
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es ALUETOO AI."}] + st.session_state.messages,
            stream=True 
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                display_html += f'<span class="word-fade">{text}</span>'
                placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                time.sleep(0.06)
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
