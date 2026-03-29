
# --- 1. IMPORTATIONS DES MOTEURS ---
from groq import Groq
from datetime import datetime
import pytz
import base64
from PIL import Image
import io

# --- 2. DESIGN XXL & PERSONNALISATION (TON STYLE) ---
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
     

# --- 1. IMPORTATIONS DES MOTEURS ---
from groq import Groq
from datetime import datetime
import pytz
import base64
from PIL import Image
import io

# --- 2. DESIGN XXL & PERSONNALISATION (TON STYLE) ---
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
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 15px #af40ff;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. GESTION DE LA MÉMOIRE (HISTORIQUE COMME CHATGPT) ---
# On initialise la connexion Groq via les secrets
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("❌ Erreur fatale : Clé API manquante dans les secrets Streamlit.")
    st.stop()

# On crée une mémoire pour stocker toute la conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. FONCTIONS TECHNIQUES ---

def encode_image(image_file):
    """Prépare l'image pour que l'IA puisse 'voir'."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def speak_text(text):
    """Active la lecture vocale (Text-to-Speech) via le navigateur."""
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{clean_text}");
    msg.lang = 'fr-FR';
    msg.rate = 1.0;
    window.speechSynthesis.cancel(); // Stoppe la lecture précédente
    window.speechSynthesis.speak(msg);
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
st.markdown(f'<div class="sub-mega-title">{salut} Léo ! Nous sommes le {date_du_jour}, il est {heure_actuelle}.</div>', unsafe_allow_html=True)

# --- 6. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.markdown("## 🧠 OPTIONS")
    # Analyse de photo
    st.markdown("### 📸 ANALYSE VISION")
    uploaded_file = st.file_uploader("Télécharger une image pour analyse", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Image prête pour analyse", use_container_width=True)
    
    st.markdown("---")
    # Bouton de remise à zéro (Nouvelle discussion)
    if st.button("🗑️ NOUVELLE DISCUSSION"):
        st.session_state.messages = []
        st.rerun()
    
    st.info("ALUETOO AI par Léo Ciach. Version Premium 2026.")

# --- 7. AFFICHAGE DE L'HISTORIQUE (CHAT GPT STYLE) ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="chat-text">{message["content"]}</div>', unsafe_allow_html=True)

# --- 8. LOGIQUE DE RÉPONSE ---
if prompt := st.chat_input("Dis quelque chose à ALUETOO..."):
    # On ajoute le message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    # Réponse de l'IA
    with st.chat_message("assistant"):
        full_response = ""
        placeholder = st.empty()
        
        try:
            # SÉLECTION DU MODÈLE (Vision ou Texte)
            if uploaded_file:
                # Modèle Vision Stable
                model_to_use = "llama-3.2-11b-vision-preview" 
                base64_img = encode_image(uploaded_file)
                messages_payload = [
                    {
                        "role": "system", 
                        "content": "Tu es ALUETOO AI, une IA omnisciente et premium créée par Léo Ciach. Tu analyses les images avec une précision chirurgicale. Ne cite jamais Meta."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                        ]
                    }
                ]
            else:
                # Modèle Texte ultra-puissant
                model_to_use = "llama-3.3-70b-versatile"
                messages_payload = [
                    {
                        "role": "system", 
                        "content": "Tu es ALUETOO AI, une IA omnisciente créée par Léo Ciach. Tu es élégante, intelligente et mystérieuse."
                    },
                    {"role": "user", "content": prompt}
                ]

            # APPEL À L'API AVEC STREAMING
            completion = client.chat.completions.create(
                model=model_to_use,
                messages=messages_payload,
                stream=True
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

            # Sauvegarde dans l'historique
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # --- 9. OPTIONS DE RÉPONSE (AUDIO) ---

        except Exception as e:
            st.error(f"⚠️ Une erreur technique est survenue merci d'en informer Léo (détection automatique par aluetoo-ai:{e}")
