import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS AVANCÉ (DÉGRADÉS ET ARRONDIS) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
    }

    /* TITRE ET SOUS-TITRE EN DÉGRADÉ */
    .header-container {
        text-align: center;
        margin-bottom: 20px;
    }
    
    .main-title {
        font-size: 45px;
        font-weight: 800;
        margin-bottom: 0px;
        color: white;
    }

    .gradient-subtitle {
        font-weight: bold;
        background: -webkit-linear-gradient(left, #ff4b4b, #8522f0, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 28px; /* Agrandissement comme demandé */
        display: block;
        margin-top: 5px;
    }

    /* BARRE DE TEXTE - LE LOOK PILULE ULTIME */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 2px solid #30363d !important;
        padding: 8px !important;
        background-color: #161b22 !important;
    }

    div[data-testid="stChatInput"] textarea {
        border-radius: 50px !important;
        padding-left: 25px !important;
        font-size: 16px !important;
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
heure_actuelle = datetime.now(tz)
format_date = heure_actuelle.strftime("%d/%m/%Y")
format_heure = heure_actuelle.strftime("%H:%M")

if 5 <= heure_actuelle.hour < 18:
    salutation = "Bonjour"
else:
    salutation = "Bonsoir"

# --- 4. AFFICHAGE DU HEADER STYLE 2026 ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="gradient-subtitle">
            {salutation} ! Intelligence {format_date} • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. GESTION DES MESSAGES (SANS MESSAGE DE DÉPART) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 6. CHAT AVEC ANIMATION ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Nous sommes le {format_date} à {format_heure}. Tu es en 2026. Réponds avec élégance et précision."

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
                time.sleep(0.05)
        
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
