import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS AVANCÉ (ULTRA-ARRONDI & FADEOUT) ---
st.markdown("""
    <style>
    /* Global Rounded Look */
    .stApp {
        background-color: #0e1117;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* Bulles de chat : Coins ultra-arrondis et bordures douces */
    .stChatMessage {
        border-radius: 35px !important; /* Plus arrondi encore */
        padding: 25px !important;
        margin: 15px 0 !important;
        border: 1px solid #2d333b;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        animation: slideUp 0.8s ease-out; /* Animation d'entrée plus lente */
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* La zone de saisie (Input) : Courbe parfaite */
    .stChatInputContainer {
        padding-bottom: 30px !important;
    }
    
    .stChatInputContainer textarea {
        border-radius: 40px !important; /* Forme de pilule */
        border: 2px solid #30363d !important;
        padding: 15px 25px !important;
        background-color: #1c2128 !important;
        transition: border-color 0.3s, box-shadow 0.3s;
    }

    .stChatInputContainer textarea:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.2) !important;
    }

    /* Icône de l'avatar arrondie */
    .stChatMessage .st-emotion-cache-18ni7ve {
        border-radius: 50% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONTEXTE TEMPOREL ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%A %d %B %Y à %H:%M")

st.title("🤖 ALUETOO AI")
st.caption(f"Créé par LEO CIACH | {maintenant}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 4. ANIMATION DE RÉPONSE LENTE ---
if prompt := st.chat_input("Dis-moi quelque chose..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Date : {maintenant}. Agis comme une IA de 2026. Ne mentionne pas 2023."

        # On utilise le streaming pour l'effet d'écriture
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}, {"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                # Effet de curseur avec animation ralentie
                placeholder.markdown(full_response + " ●") 
                time.sleep(0.05) # <-- RÉGLAGE DE VITESSE : Augmente ce chiffre pour ralentir encore plus
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
