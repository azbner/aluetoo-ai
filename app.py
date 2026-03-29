import streamlit as st

# --- 0. CONFIGURATION SYSTÈME (INDISPENSABLE EN LIGNE 1) ---
st.set_page_config(
    page_title="ALUETOO AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. IMPORTATIONS DES MOTEURS ---
from groq import Groq
from datetime import datetime
import pytz
import base64
from PIL import Image
import io

# --- 2. DESIGN XXL & PERSONNALISATION (STYLE LÉO CIACH) ---
st.markdown("""
    <style>
    /* Fond de l'application */
    .stApp { background-color: #0b0e14; }
    
    /* Titre Principal de Luxe */
    .mega-title {
        font-weight: 900;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 65px; 
        text-align: center; 
        margin-top: -60px;
        letter-spacing: -2px;
    }
    
    /* Sous-titre dynamique */
    .sub-mega-title {
        font-weight: 700; 
        color: #e6edf3; 
        font-size: 24px; 
        text-align: center; 
        margin-bottom: 40px;
        opacity: 0.9;
    }
    
    /* Bulles de Chat Style ChatGPT */
    .chat-text { 
        font-size: 19px !important; 
        color: #e6edf3; 
        line-height: 1.6;
        font-family: 'Inter', sans-serif;
    }
    
    /* Barre d'entrée stylisée */
    div[data-testid="stChatInput"] { 
        border-radius: 30px !important; 
        border: 2px solid #af40ff !important;
        background-color: #161b22 !important;
    }
    
    /* Boutons personnalisés */
    .stButton>button { 
        border-radius: 15px; 
        background: linear-gradient(45deg, #af40ff, #00d4ff); 
        color: white; 
        border: none;
        font-weight: bold;
        transition: 0.3s;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 15px #af40ff;
    }
    </style>
""", unsafe_allow_html=True)
# --- 3. GESTION DE LA MÉMOIRE (HISTORIQUE) ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("❌ Erreur fatale : Clé API manquante dans les secrets Streamlit.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. FONCTIONS TECHNIQUES ---

def encode_image(image_file):
    """Prépare l'image pour l'analyse."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def speak_text(text):
    """Lecture vocale forcée pour mobile/APK."""
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

# --- 5. HEADER AVEC HEURE RÉELLE ---
tz = pytz.timezone('Europe/Paris')
now = datetime.now(tz)
date_du_jour = now.strftime("%d/%m/%Y")
heure_actuelle = now.strftime("%H:%M")
salut = "Bonjour" if 5 <= now.hour < 18 else "Bonsoir"

st.markdown('<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-mega-title">{salut} ! Nous sommes le {date_du_jour}, il est {heure_actuelle}.</div>', unsafe_allow_html=True)

# --- 6. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown("## 🧠 OPTIONS")
    st.markdown("### 📸 ANALYSE VISION")
    uploaded_file = st.file_uploader("Prendre ou choisir une photo", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Image prête pour analyse", use_container_width=True)
    
    st.markdown("---")
    if st.button("🗑️ NOUVELLE DISCUSSION"):
        st.session_state.messages = []
        st.rerun()
    
    st.info("ALUETOO AI par Léo Ciach. Version Premium 2026.")

# --- 7. AFFICHAGE DE L'HISTORIQUE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="chat-text">{message["content"]}</div>', unsafe_allow_html=True)

# --- 8. LOGIQUE DE RÉPONSE ---
if prompt := st.chat_input("Dis quelque chose à ALUETOO..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        full_response = ""
        placeholder = st.empty()
        
        try:
            if uploaded_file:
                # MODÈLE VISION DÉBLOQUÉ
                model_to_use = "meta-llama/llama-4-scout-17b-16e-instruct" 
                base64_img = encode_image(uploaded_file)
                messages_payload = [
                    {"role": "system", "content": "Tu es ALUETOO AI, une IA omnisciente et premium créée par Léo Ciach. Analyse avec précision."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]}
                ]
            else:
                model_to_use = "llama-3.3-70b-versatile"
                messages_payload = [
                    {"role": "system", "content": "Tu es ALUETOO AI, créée par Léo Ciach. Tu es élégante et intelligente."},
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
            
            # --- 9. BOUTON AUDIO UNIQUE ---
            if st.button("🔊 ÉCOUTER LA RÉPONSE", key=f"voice_btn_{len(st.session_state.messages)}"):
                speak_text(full_response)

        except Exception as e:
            st.error(f"⚠️ Une erreur technique est survenue. Merci d'en informer Léo (détection automatique par ALUETOO AI : {e})")
