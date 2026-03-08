import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz
import base64
from PIL import Image
import io

# --- 1. CONFIGURATION & CONNEXION ---
st.set_page_config(page_title="ALUETOO AI", layout="wide")

# Récupération de la clé API
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Erreur : La clé GROQ_API_KEY est manquante dans les secrets.")
    st.stop()

# Initialisation de la mémoire
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. FONCTIONS TECHNIQUES ---

def encode_image(image_file):
    """Transforme l'image pour que l'IA puisse la lire."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def speak_text(text):
    """Fait parler l'IA via le navigateur."""
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{clean_text}");
    msg.lang = 'fr-FR';
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 3. DESIGN XXL (TON STYLE) ---
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
    .sub-mega-title {
        font-weight: 800;
        background: linear-gradient(to right, #00d4ff, #af40ff, #ff4b4b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 35px; text-align: center; margin-bottom: 30px;
    }
    .chat-text { font-size: 20px !important; color: #e6edf3; }
    div[data-testid="stChatInput"] { border-radius: 50px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER ---
tz = pytz.timezone('Europe/Brussels')
h = datetime.now(tz).hour
salut = "Bonjour" if 5 <= h < 18 else "Bonsoir"

st.markdown('<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-mega-title">{salut} !, je t\'écoute.</div>', unsafe_allow_html=True)

# --- 5. BARRE LATÉRALE (VISION) ---
with st.sidebar:
    st.markdown("### 📸 ANALYSE PHOTO")
    uploaded_file = st.file_uploader("Envoie une image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Image prête")
    
    if st.button("✨ Nouvelle Discussion"):
        st.session_state.messages = []
        st.rerun()

# --- 6. LE CHAT ---
# Afficher l'historique
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# Entrée utilisateur
if prompt := st.chat_input("Pose ta question..."):
    # Affichage immédiat du message utilisateur
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    
    # Ajout à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Choix du modèle et préparation du contenu
            if uploaded_file:
                model_to_use = "llama-3.2-11b-vision-preview"
                base64_img = encode_image(uploaded_file)
                content_payload = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
            else:
                model_to_use = "llama-3.3-70b-versatile"
                content_payload = prompt

            # Appel API
            completion = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": "Tu es ALUETOO AI, une IA omnisciente créée par Léo Ciach."},
                    {"role": "user", "content": content_payload}
                ],
                stream=True
            )

            # Streaming de la réponse
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

            # Option de lecture vocale
            if st.button("🔊 LIRE À VOIX HAUTE"):
                speak_text(full_response)

        except Exception as e:
            st.error(f"Erreur technique : {e}")

    # Sauvegarde de la réponse
    st.session_state.messages.append({"role": "assistant", "content": full_response})

