import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Clé API manquante.")
    st.stop()

# --- 2. STYLE CSS AVANCÉ (ARRONDIS ET ANIMATIONS) ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp {
        background-color: #0e1117;
    }

    /* Bulles de chat hyper arrondies */
    .stChatMessage {
        border-radius: 30px !important;
        padding: 20px !important;
        margin: 10px 0 !important;
        border: 1px solid #30363d;
    }

    /* Animation de fondu pour l'apparition des bulles */
    .stChatMessage {
        animation: fadeIn 0.6s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Zone de texte (input) arrondie, même quand on écrit */
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }
    
    .stChatInputContainer textarea {
        border-radius: 30px !important;
        border: 2px solid #ff4b4b !important;
        padding: 10px 20px !important;
        background-color: #161b22 !important;
        color: white !important;
    }

    /* Cacher le bouton Streamlit pour un look plus propre */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTION DE L'HEURE BELGE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%A %d %B %Y à %H:%M")

st.title("🤖 ALUETOO AI")
st.caption(f"📍 Jette, Belgique | ⏰ {maintenant}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des anciens messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 4. LOGIQUE DE RÉPONSE ANIMÉE ---
if prompt := st.chat_input("Dis-moi quelque chose..."):
    # Affichage utilisateur
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Préparation de la réponse
    with st.chat_message("assistant"):
        placeholder = st.empty() # Zone pour l'animation
        full_response = ""
        
        # Instruction forcée pour l'IA
        ctx = f"Tu es ALUETOO AI. Nous sommes le {maintenant}. Agis comme une IA moderne de 2026."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}, {"role": "user", "content": prompt}],
            stream=True # On active le flux pour l'animation
        )

        # Animation "mot à mot" comme sur Gemini/ChatGPT
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                placeholder.markdown(full_response + "▌") # Petit curseur qui clignote
                time.sleep(0.01) # Vitesse de l'animation
        
        placeholder.markdown(full_response) # Affichage final sans le curseur

    st.session_state.messages.append({"role": "assistant", "content": full_response})
