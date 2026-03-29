import streamlit as st

# --- 0. CONFIGURATION OBLIGATOIRE ---
st.set_page_config(page_title="ALUETOO AI", layout="wide", page_icon="🚀")

# --- 1. IMPORTATIONS ---
from groq import Groq
from datetime import datetime
import pytz
import base64
from PIL import Image
import io

# --- 2. MANIFEST & DESIGN XXL ---
st.markdown(
    """
    <head>
        <link rel="manifest" href="manifest.json">
        <meta name="theme-color" content="#0b0e14">
    </head>
    <style>
    .stApp { background-color: #0b0e14; }
    .mega-title {
        font-weight: 900;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 60px; text-align: center; margin-top: -50px;
    }
    .sub-mega-title {
        font-weight: 700;
        color: #e6edf3;
        font-size: 25px; text-align: center; margin-bottom: 30px;
    }
    .chat-text { font-size: 18px !important; color: #e6edf3; line-height: 1.6; }
    div[data-testid="stChatInput"] { border-radius: 50px !important; border: 1px solid #af40ff !important; }
    .stButton>button { border-radius: 20px; background: linear-gradient(45deg, #af40ff, #00d4ff); color: white; border: none; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. CONNEXION & MÉMOIRE ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ Clé API manquante dans les Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. FONCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def speak_text(text):
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""<script>var msg = new SpeechSynthesisUtterance("{clean_text}"); msg.lang = 'fr-FR'; window.speechSynthesis.speak(msg);</script>"""
    st.components.v1.html(js_code, height=0)

# --- 5. HEADER DYNAMIQUE ---
tz = pytz.timezone('Europe/Paris')
now = datetime.now(tz)
date_str = now.strftime("%d/%m/%Y")
heure_str = now.strftime("%H:%M")
salut = "Bonjour" if 5 <= now.hour < 18 else "Bonsoir"

st.markdown('<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-mega-title">{salut} Léo ! Nous sommes le {date_str}, il est {heure_str}.</div>', unsafe_allow_html=True)

# --- 6. BARRE LATÉRALE ---
with st.sidebar:
    st.markdown("### 📸 VISION")
    uploaded_file = st.file_uploader("Analyser une photo", type=["jpg", "png", "jpeg"])
    st.markdown("---")
    if st.button("🗑️ NOUVELLE DISCUSSION"):
        st.session_state.messages = []
        st.rerun()

# --- 7. CHAT & HISTORIQUE ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Pose ta question à ALUETOO..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        full_response = ""
        placeholder = st.empty()
        
        try:
            if uploaded_file:
                # CORRECTION ICI : Le bon nom de modèle sans "model=" en double
                model_to_use = "llama-3.2-11b-vision-preview" 
                base64_img = encode_image(uploaded_file)
                messages_payload = [
                    {"role": "system", "content": "Tu es ALUETOO AI, créée par Léo Ciach. Analyse cette image avec précision."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]}
                ]
            else:
                model_to_use = "llama-3.3-70b-versatile"
                messages_payload = [
                    {"role": "system", "content": "Tu es ALUETOO AI, créée par Léo Ciach."},
                    {"role": "user", "content": prompt}
                ]

            completion = client.chat.completions.create(
                model=model_to_use,
                messages=messages_payload,
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Bouton Audio
            if st.button("🔊 ÉCOUTER"):
                speak_text(full_response)

        except Exception as e:
            st.error(f"Erreur technique : {e}")
