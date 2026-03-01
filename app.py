import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS AVANCÉ (DÉGRADÉS, ARRONDIS ET FONDU) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
    }

    /* Animation de fondu pour l'écriture */
    @keyframes textFadeIn {
        from { opacity: 0; filter: blur(4px); transform: translateY(3px); }
        to { opacity: 1; filter: blur(0px); transform: translateY(0px); }
    }

    .writing-effect {
        display: inline;
        animation: textFadeIn 0.9s ease-out forwards;
    }

    /* HEADER DÉGRADÉ */
    .header-container {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: white;
        margin-bottom: 5px;
    }

    .salutation-text {
        font-size: 24px;
        color: #e6edf3;
        margin-bottom: 5px;
    }

    .gradient-subtitle {
        font-weight: bold;
        background: -webkit-linear-gradient(left, #ff4b4b, #8522f0, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 20px;
        display: block;
    }

    /* BARRE DE TEXTE PILULE ULTIME */
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

    /* Bulles de chat */
    .stChatMessage {
        border-radius: 30px !important;
        border: 1px solid #1f2328;
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

# --- 4. AFFICHAGE DU HEADER RE-DESIGNÉ ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="salutation-text">{salutation} !</div>
        <div class="gradient-subtitle">
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

# --- 6. CHAT AVEC EFFET DE FONDU ---
if prompt := st.chat_input("Pose ta question à ALUETOO AI..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Nous sommes le {format_date}. Tu es une IA de 2026 ultra-moderne."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}] + st.session_state.messages,
            stream=True 
        )

        display_container = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                # Application de l'effet span pour le fondu
                display_container += f'<span class="writing-effect">{text}</span>'
                placeholder.markdown(display_container, unsafe_allow_html=True)
                time.sleep(0.04)
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
