import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz
from streamlit_mic_recorder import mic_recorder # Pour le micro
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ALUETOO AI - VISION & VOICE", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialisation des états
if "messages" not in st.session_state:
    st.session_state.messages = []
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

# --- 2. FONCTION LECTURE VOCALE (AUDIO) ---
def speak_text(text):
    # Utilise le navigateur pour lire le texte sans serveur externe
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text.replace('"', "'")}");
    msg.lang = 'fr-FR';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 3. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .mega-title {
        font-weight: 900;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 65px; text-align: center;
    }
    .chat-text { font-size: 18px; color: #e6edf3; }
    /* Style pour les boutons audio/photo */
    .stButton>button { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown('<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)

# --- 5. BARRE D'OUTILS (PHOTO & MICRO) ---
with st.sidebar:
    st.markdown("### 🛠️ OUTILS MULTIMÉDIA")
    
    # GESTION PHOTO
    uploaded_file = st.file_uploader("📷 Analyser une photo", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        st.image(uploaded_file, caption="Photo chargée", use_column_width=True)

    # GESTION MICRO
    st.markdown("🎤 **Parler à l'IA :**")
    audio = mic_recorder(start_prompt="Démarrer l'écoute", stop_prompt="Arrêter & Envoyer", key='recorder')

# --- 6. LOGIQUE DE CHAT ---

# Affichage des messages
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# Gestion de l'entrée (Texte ou Audio)
prompt = st.chat_input("Pose ta question ici...")

# Si on reçoit de l'audio, on pourrait utiliser Whisper ici (pour l'instant on gère le texte)
if audio:
    # Ici on ajouterait Whisper pour transcrire l'audio.json
    st.warning("Transcription audio en cours d'implémentation (nécessite Whisper API)")

if prompt or uploaded_file:
    user_content = prompt if prompt else "Analyse cette image."
    
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{user_content}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": user_content})

    with st.chat_message("assistant"):
        # Sélection du modèle (Vision si photo, sinon Classique)
        model_name = "llama-3.2-11b-vision-preview" if uploaded_file else "llama-3.3-70b-versatile"
        
        completion = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": "Tu es ALUETOO AI. Tu peux voir et entendre."}] + st.session_state.messages,
            stream=False # Stream désactivé pour faciliter la lecture vocale après
        )

        response = completion.choices[0].message.content
        st.markdown(f'<div class="chat-text">{response}</div>', unsafe_allow_html=True)
        
        # LECTURE AUTOMATIQUE
        if st.button("🔊 Lire la réponse"):
            speak_text(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
