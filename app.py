import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONNEXION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. INTERFACE LUXE (CSS) ---
st.markdown("""
    <style>
    /* Couleur de fond sombre et moderne */
    .stApp {
        background-color: #0b0e14;
    }

    /* Bulles de chat : On force l'arrondi "Galet" */
    .stChatMessage {
        border-radius: 30px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        border: 1px solid #1f2328;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        animation: fadeInSlide 0.8s ease-out;
    }

    @keyframes fadeInSlide {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ZONE DE SAISIE : Le style "Pilule" que tu voulais */
    .stChatInputContainer {
        padding: 20px !important;
        background: transparent !important;
    }

    .stChatInputContainer textarea {
        border-radius: 50px !important; /* Arrondi total */
        border: 1.5px solid #30363d !important;
        padding: 12px 25px !important;
        background-color: #161b22 !important;
        color: #e6edf3 !important;
        font-size: 16px !important;
        transition: all 0.3s ease;
    }

    /* Effet quand on clique pour écrire */
    .stChatInputContainer textarea:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.15) !important;
        background-color: #1c2128 !important;
    }

    /* On cache le logo Streamlit pour faire plus pro */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEURE ET DATE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%A %d %B %Y à %H:%M")

st.title("🤖 ALUETOO AI")
st.caption(f"Propulsé par LEO CIACH | {maintenant}")
