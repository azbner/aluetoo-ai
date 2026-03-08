import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz
import base64
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ALUETOO AI - OMNISCIENT", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []

# --- 2. FONCTIONS TECHNIQUES (VISION & VOIX) ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def speak_text(text):
    # Utilise l'API native du navigateur (Gratuit et instantané)
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text.replace('"', "'").replace('\n', ' ')}");
    msg.lang = 'fr-FR';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 3. STYLE CSS (TON DESIGN XXL) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; }
    .mega-title {
        font-weight: 900;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 65px; text-align: center; margin-bottom: 10px;
    }
    .sub-mega-title {
        font-weight: 800;
        background: linear-gradient(to right, #00d4ff, #af40ff, #ff4b4b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 35px; text-align: center; display: block; margin-bottom: 30px;
    }
    .chat-text { font-size: 20px !important; color: #e6edf3; line-height: 1.6; }
    div[data-testid="stChatInput"] { border-radius: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
salutation = "Bonjour" if 5 <= datetime.now(tz).hour < 18 else "Bonsoir"

# --- 5. INTERFACE ---
st.markdown(f'<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-mega-title">{salutation}, je suis prêt.</div>', unsafe_allow_html=True)

# Sidebar pour les outils
with st.sidebar:
    st.header("📸 VISION")
    uploaded_file = st.file_uploader("Scanner une image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Image en mémoire", use_container_width=True)
    
    if st.button("🗑️ Effacer la mémoire"):
        st.session_state.messages = []
        st.rerun()

# --- 6. AFFICHAGE DES MESSAGES ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. TRAITEMENT DU CHAT ---
if prompt := st.chat_input("Pose ta question ou analyse une photo..."):
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Préparation du contenu (Texte simple ou Vision)
        if uploaded_file:
            model = "llama-3.2-11b-vision-preview"
            base64_img = encode_image(uploaded_file)
            content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
            ]
        else:
            model = "llama-3.3-70b-versatile"
            content = prompt

        # Appel API Groq
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Tu es ALUETOO AI, une IA créée par Léo Ciach. Tu peux voir les images."},
                {"role": "user", "content": content}
            ],
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

        # Bouton pour lire la réponse à voix haute
        if st.button("🔊 ÉCOUTER LA RÉPONSE"):
            speak_text(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
