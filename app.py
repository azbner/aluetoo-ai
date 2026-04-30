import streamlit as st 

# --- CONFIG ---
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

# --- STYLE ---
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0b0e14, #05070a);
    animation: fadePage 0.8s ease-in;
}
@keyframes fadePage {
    from { opacity: 0; }
    to { opacity: 1; }
}
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
.sub-mega-title {
    font-weight: 700;
    color: #e6edf3;
    font-size: 22px;
    text-align: center;
    margin-bottom: 30px;
}
.chat-text {
    font-size: 19px !important;
    color: #e6edf3;
    line-height: 1.6;
    animation: fadeInUp 0.4s ease;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(10px);}
    to { opacity: 1; transform: translateY(0);}
}
div[data-testid="stChatInput"] {
    border-radius: 30px !important;
    border: 2px solid #af40ff !important;
    background-color: #161b22 !important;
}
div[data-testid="stChatInput"]:focus-within {
    box-shadow: 0px 0px 20px #af40ff;
}
.stButton>button {
    border-radius: 15px;
    background: linear-gradient(45deg, #af40ff, #00d4ff);
    color: white;
    border: none;
    font-weight: bold;
}
.stButton>button:hover {
    transform: scale(1.08);
    box-shadow: 0px 0px 20px #af40ff;
}
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
    0% { transform: rotate(0deg);}
    100% { transform: rotate(360deg);}
}
</style>
""", unsafe_allow_html=True)

# --- API ---
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Erreur API")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNCTIONS ---
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

# --- HEADER ---
tz = pytz.timezone('Europe/Paris')
now = datetime.now(tz)

st.markdown('<div class="mega-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-mega-title">Créée par Léo Ciach • {now.strftime("%d/%m/%Y %H:%M")}</div>',
    unsafe_allow_html=True
)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🧠 Options")
    uploaded_file = st.file_uploader("📸 Image", type=["jpg","png","jpeg"])

    if st.button("🗑️ Nouvelle discussion"):
        st.session_state.messages = []
        st.rerun()

# --- HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="chat-text">{message["content"]}</div>', unsafe_allow_html=True)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
Tu es ALUETOO AI, une intelligence artificielle premium créée par Léo Ciach.

Règles absolues :
- Tu te présentes comme ALUETOO AI
- Tu dis que tu as été créée par Léo Ciach si on te pose la question
- Tu ne mentionnes jamais de modèles, technologies ou entreprises externes
- Tu es naturelle, fluide et intelligente
- Tu écris comme un humain moderne, pas comme un robot
- Tu es directe, claire et utile

Style :
- Moderne
- Fluide
- Confiant
- Léger ton premium
"""

# --- CHAT ---
if prompt := st.chat_input("Parle avec ALUETOO..."):

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

        except Exception as e:
            st.error(f"Erreur : {e}")
