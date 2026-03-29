import streamlit as st

# --- 1. CONFIGURATION (OBLIGATOIRE EN LIGNE 1) ---
st.set_page_config(page_title="ALUETOO AI", layout="wide", page_icon="🚀")

from groq import Groq
from datetime import datetime
import pytz
import base64
from PIL import Image
import io

# --- 2. DESIGN XXL & STYLE PREMIUM ---
st.markdown("""
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
        font-weight: 700; color: #e6edf3; font-size: 24px; text-align: center; margin-bottom: 30px;
    }
    .chat-text { font-size: 18px !important; color: #e6edf3; line-height: 1.6; }
    div[data-testid="stChatInput"] { border-radius: 50px !important; border: 2px solid #af40ff !important; }
    .stButton>button { border-radius: 15px; background: linear-gradient(45deg, #af40ff, #00d4ff); color: white; border: none; font-weight: bold; padding: 10px 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONNEXION & MÉMOIRE ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("⚠️ Clé API manquante dans les Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. FONCTION AUDIO (CORRIGÉE) ---
def speak_text(text):
    """Lecture vocale renforcée avec débloqueur pour APK."""
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var msg = new SpeechSynthesisUtterance("{clean_text}");
        msg.lang = 'fr-FR';
        msg.rate = 1.0;
        window.speechSynthesis.getVoices();
        window.speechSynthesis.speak(msg);
    }})();
    </script>
    """
    st.components.v1.html(js_code, height=0)

def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# --- 5. HEADER DYNAMIQUE ---
tz = pytz.timezone('Europe/Paris')
now = datetime.now(tz)
salut = "Bonjour" if 5 <= now.hour < 18 else "Bonsoir"
st.markdown('<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-mega-title">{salut} Léo ! Il est {now.strftime("%H:%M")}.</div>', unsafe_allow_html=True)

# --- 6. BARRE LATÉRALE (VISION) ---
with st.sidebar:
    st.markdown("### 📸 ANALYSE PHOTO")
    uploaded_file = st.file_uploader("Prendre ou choisir une photo", type=["jpg", "png", "jpeg"])
    st.markdown("---")
    if st.button("🗑️ NOUVELLE DISCUSSION"):
        st.session_state.messages = []
        st.rerun()

# --- 7. CHAT (HISTORIQUE) ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 8. LOGIQUE D'ENVOI ---
if prompt := st.chat_input("Pose ta question à ALUETOO..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        full_response = ""
        placeholder = st.empty()
        
        try:
            if uploaded_file:
                # MODÈLE LLAMA 4 POUR LA VISION (Ton nouveau modèle)
                model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
                base64_img = encode_image(uploaded_file)
                payload = [
                    {"role": "system", "content": "Tu es ALUETOO AI, créée par Léo Ciach."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]}
                ]
            else:
                model_name = "llama-3.3-70b-versatile"
                payload = [
                    {"role": "system", "content": "Tu es ALUETOO AI, une IA premium créée par Léo Ciach."},
                    {"role": "user", "content": prompt}
                ]

            completion = client.chat.completions.create(
                model=model_name,
                messages=payload,
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # --- LE BOUTON ÉCOUTER (UNIK PAR RÉPONSE) ---
            if st.button("🔊 ÉCOUTER LA RÉPONSE", key=f"voice_{len(st.session_state.messages)}"):
                speak_text(full_response)

        except Exception as e:
            st.error(f"Erreur technique : {e}")
