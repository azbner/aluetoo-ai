import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS AVANCÉ ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
    }

    /* TEXTE EN DÉGRADÉ À CÔTÉ DU TITRE */
    .gradient-text {
        font-weight: bold;
        background: -webkit-linear-gradient(left, #ff4b4b, #8522f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 20px;
    }

    /* FORCE L'ARRONDI DE LA BARRE DE TEXTE (PILULE) */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
        padding: 5px !important;
        overflow: hidden !important;
    }

    div[data-testid="stChatInput"] textarea {
        border-radius: 50px !important;
        background-color: transparent !important;
        padding: 10px 20px !important;
    }

    /* Bulles de chat Galets */
    .stChatMessage {
        border-radius: 30px !important;
        padding: 1.2rem !important;
        border: 1px solid #1f2328;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
heure_actuelle = datetime.now(tz)
format_heure = heure_actuelle.strftime("%H:%M")

if 5 <= heure_actuelle.hour < 18:
    salutation = "Bonjour"
else:
    salutation = "Bonsoir"

# Affichage du Titre avec Dégradé
st.markdown(f'# 🤖 ALUETOO AI <span class="gradient-text">| Intelligence 2026</span>', unsafe_allow_html=True)
st.caption(f"{salutation}, nous sommes le {heure_actuelle.strftime('%d/%m/%Y')} à {format_heure}")

# --- 4. GESTION DES MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Premier message d'accueil
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"{salutation} ! Je suis ALUETOO AI. Comment puis-je t'aider aujourd'hui ?"
    })

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 5. CHAT ANIMÉ ---
if prompt := st.chat_input("Écris ton message..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Date : {format_heure}. Tu es en 2026. Réponds avec élégance."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}] + st.session_state.messages,
            stream=True 
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                placeholder.markdown(full_response + " ▎") 
                time.sleep(0.06)
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
