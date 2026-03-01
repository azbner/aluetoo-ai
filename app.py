import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS (ARRONDIS ET DESIGN) ---
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

    /* BARRE DE TEXTE STYLE PILULE */
    .stChatInputContainer {
        padding: 15px !important;
    }

    .stChatInputContainer textarea {
        border-radius: 50px !important; /* Arrondi maximum */
        border: 2px solid #30363d !important;
        padding: 15px 25px !important;
        background-color: #161b22 !important;
        color: white !important;
        font-size: 16px !important;
    }

    .stChatInputContainer textarea:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.2) !important;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE DE L'HEURE ET SALUTATION ---
tz = pytz.timezone('Europe/Brussels')
heure_actuelle = datetime.now(tz)
format_heure = heure_actuelle.strftime("%A %d %B %Y à %H:%M")

# Déterminer Bonjour ou Bonsoir
heure_int = heure_actuelle.hour
if 5 <= heure_int < 18:
    salutation = "Bonjour"
else:
    salutation = "Bonsoir"

st.title(f"🤖 ALUETOO AI")
st.caption(f"{salutation} ! Nous sommes le {format_heure}")

# --- 4. GESTION DES MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Petit message de bienvenue automatique
    st.session_state.messages.append({
        "role": "assistant", 
        "content": f"{salutation} ! Je suis ALUETOO AI. Comment puis-je t'aider en ce {heure_actuelle.strftime('%A')} ?"
    })

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 5. CHAT ANIMÉ ---
if prompt := st.chat_input("Dis-moi quelque chose..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Date : {format_heure}. Tu es en 2026. Sois poli et moderne."

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
                time.sleep(0.06) # Écriture lente
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
