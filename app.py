import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS AVANCÉ (DÉGRADÉS GÉANTS ET EFFET GHOST) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
    }

    /* ANIMATION DE FONDU POUR L'ÉCRITURE */
    @keyframes textFadeIn {
        from { opacity: 0; filter: blur(5px); transform: translateY(5px); }
        to { opacity: 1; filter: blur(0px); transform: translateY(0px); }
    }

    .writing-effect {
        display: inline;
        animation: textFadeIn 1.2s ease-out forwards;
        color: #e6edf3;
    }

    /* HEADER AVEC TOUT EN DÉGRADÉ */
    .header-container {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: white;
        margin-bottom: 10px;
    }

    .full-gradient {
        font-weight: bold;
        background: -webkit-linear-gradient(left, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 26px; /* Agrandi */
        display: block;
        line-height: 1.4;
    }

    /* BARRE DE TEXTE PILULE */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 2px solid #30363d !important;
        padding: 8px !important;
        background-color: #161b22 !important;
    }

    div[data-testid="stChatInput"] textarea {
        border-radius: 50px !important;
        padding-left: 25px !important;
    }

    /* Bulles de chat Galets */
    .stChatMessage {
        border-radius: 30px !important;
        border: 1px solid #1f2328;
        background-color: #161b22;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_date = maintenant.strftime("%d/%m/%Y")
format_heure = maintenant.strftime("%H:%M")

if 5 <= maintenant.hour < 18:
    salutation = "Bonjour"
else:
    salutation = "Bonsoir"

# --- 4. AFFICHAGE DU HEADER (TOUT DÉGRADÉ) ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="full-gradient">
            {salutation} !<br>
            Intelligence 2026 (Mise à jour design le 1 mars 2026) • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. GESTION DES MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. CHAT AVEC EFFET FONDU DÉGRADÉ ---
if prompt := st.chat_input("Pose ta question à ALUETOO AI..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Nous sommes le {format_date}. Tu es en 2026."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}] + st.session_state.messages,
            stream=True 
        )

        display_html = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                # Chaque mot apparaît avec l'animation CSS writing-effect
                display_html += f'<span class="writing-effect">{text}</span>'
                placeholder.markdown(display_html, unsafe_allow_html=True)
                time.sleep(0.05)
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
