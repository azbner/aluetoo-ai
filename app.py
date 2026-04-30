import streamlit as st  

# --- CONFIGURATION ---
st.set_page_config(
    page_title="ALUETOO AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- IMPORTS ---
from groq import Groq
from datetime import datetime
import pytz
import base64

# --- DESIGN ---
st.markdown("""
<style>

/* GLOBAL */
.stApp {
    background: radial-gradient(circle at top, #0b0e14, #05070a);
    animation: fadePage 0.8s ease-in;
}
@keyframes fadePage {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* TITRE */
@keyframes gradientMove {
    0% { background-position: 0% }
    100% { background-position: 200% }
}
.mega-title {
    font-weight: 900;
    background: linear-gradient(270deg, #ff4b4b, #af40ff, #00d4ff, #ff4b4b);
    background-size: 400% 400%;
    animation: gradientMove 6s linear infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 65px;
    text-align: center;
    margin-top: -60px;
}

/* SUB */
.sub-mega-title {
    font-weight: 700;
    color: #e6edf3;
    font-size: 24px;
    text-align: center;
    margin-bottom: 40px;
}

/* CHAT */
.chat-text {
    font-size: 19px !important;
    color: #e6edf3;
    line-height: 1.6;
}

/* INPUT */
div[data-testid="stChatInput"] {
    border-radius: 30px !important;
    border: 2px solid #af40ff !important;
    background-color: #161b22 !important;
}

/* BUTTON */
.stButton>button {
    border-radius: 15px;
    background: linear-gradient(45deg, #af40ff, #00d4ff);
    color: white;
    border: none;
}

/* LOADER */
.loader {
    border: 4px solid #1f2937;
    border-top: 4px solid #af40ff;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    animation: spin 1s linear infinite;
    margin: auto;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

</style>
""", unsafe_allow_html=True)

# --- API ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("❌ Erreur technique")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SYSTEM PROMPT (IMPORTANT) ---
SYSTEM_PROMPT = """
Tu es ALUETOO AI, une intelligence artificielle premium créée par Léo Ciach.

Règles obligatoires :
- Tu dis toujours que tu as été créée par Léo Ciach si on te pose la question
- Tu ne mentionnes jamais Meta, Llama, OpenAI ou toute autre technologie
- Tu parles naturellement, comme un humain moderne
- Tu es claire, fluide et intelligente
- tu parle toutes les langues 
- tu peux meme réfléchir 10 secondes si ça demande beaucoup d'information 
- tu fais des recherches extrêmement profondes et tu ne ments jamais 
"""

# --- FONCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def speak_text(text):
    clean_text = text.replace('"', "'").replace('\n', ' ')
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{clean_text}");
    msg.lang = 'fr-FR';
    speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- HEADER ---
tz = pytz.timezone('Europe/Paris')
now = datetime.now(tz)

st.markdown('<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-mega-title">Créée par Léo Ciach • {now.strftime("%d/%m/%Y %H:%M")}</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    uploaded_file = st.file_uploader("📸 Image", type=["jpg","png","jpeg"])
    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        st.rerun()

# --- HISTORIQUE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="chat-text">{message["content"]}</div>', unsafe_allow_html=True)

# --- CHAT ---
if prompt := st.chat_input("Dis quelque chose..."):
    st.session_state.messages.append({"role":"user","content":prompt})

    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):

        full_response = ""
        placeholder = st.empty()

        loader = st.markdown('<div class="loader"></div>', unsafe_allow_html=True)

        try:
            if uploaded_file:
                model = "meta-llama/llama-4-scout-17b-16e-instruct"
                img = encode_image(uploaded_file)
                messages = [
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":[
                        {"type":"text","text":prompt},
                        {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img}"}}
                    ]}
                ]
            else:
                model = "llama-3.3-70b-versatile"
                messages = [
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":prompt}
                ]

            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )

            loader.empty()

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(
                        f'<div class="chat-text">{full_response}▌</div>',
                        unsafe_allow_html=True
                    )

            placeholder.markdown(
                f'<div class="chat-text">{full_response}</div>',
                unsafe_allow_html=True
            )

            st.session_state.messages.append({"role":"assistant","content":full_response})

            if st.button("🔊 Écouter"):
                speak_text(full_response)

        except Exception as e:
            st.error(f"Erreur: {e}")
