import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONNEXION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. INTERFACE LUXE (CSS REVISE) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
    }

    /* Bulles de chat Galets */
    .stChatMessage {
        border-radius: 30px !important;
        padding: 1.2rem !important;
        margin: 10px 0 !important;
        border: 1px solid #1f2328;
        animation: fadeInSlide 0.8s ease-out;
    }

    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* LA ZONE DE TEXTE (FIXÉE) */
    /* On s'assure qu'elle est bien visible et arrondie */
    .stChatInputContainer {
        padding: 10px !important;
        background-color: transparent !important;
    }

    .stChatInputContainer textarea {
        border-radius: 50px !important; /* L'arrondi total que tu voulais */
        border: 2px solid #30363d !important;
        padding: 12px 20px !important;
        background-color: #161b22 !important;
        color: white !important;
        line-height: 1.5 !important;
    }

    /* Animation quand on clique pour écrire */
    .stChatInputContainer textarea:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.2) !important;
    }

    /* On garde le reste propre sans masquer l'essentiel */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEURE ET DATE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%A %d %B %Y à %H:%M")

st.title("🤖 ALUETOO AI")
st.caption(f"Propulsé par LEO CIACH | {maintenant}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 4. CHAT ANIMÉ ---
if prompt := st.chat_input("Demande à ALUETOO AI..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Nous sommes le {maintenant}. Tu es en 2026. Réponds avec style."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}, {"role": "user", "content": prompt}],
            stream=True 
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                # Curseur fin et élégant
                placeholder.markdown(full_response + " ▎") 
                time.sleep(0.06) # Vitesse fluide
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
