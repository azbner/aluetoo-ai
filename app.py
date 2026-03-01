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
        from { opacity: 0; filter: blur(3px); transform: translateY(2px); }
        to { opacity: 1; filter: blur(0px); transform: translateY(0px); }
    }

    .writing-effect {
        display: inline;
        animation: textFadeIn 0.8s ease-out forwards;
    }

    /* HEADER DÉGRADÉ */
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .main-title {
        font-size: 45px;
        font-weight: 800;
        color: white;
    }

    .gradient-subtitle {
        font-weight: bold;
        background: -webkit-linear-gradient(left, #ff4b4b, #8522f0, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 28px;
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

# Affichage du Header
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="gradient-subtitle">
            {salutation} ! Intelligence {format_date} • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. GESTION DES MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 5. CHAT AVEC EFFET DE FONDU ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Date : {format_date}. Tu es en 2026. Réponds avec élégance."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}] + st.session_state.messages,
            stream=True 
        )

        # Ici on crée l'effet de fondu mot par mot
        display_container = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                # On enveloppe chaque nouveau bout de texte dans un span avec l'animation
                display_container += f'<span class="writing-effect">{text}</span>'
                placeholder.markdown(display_container, unsafe_allow_html=True)
                time.sleep(0.04)
        
        # Une fois fini, on remet le texte propre pour le stockage
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
