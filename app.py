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

# --- STYLE PRO ---
st.markdown("""
<style>

/* GLOBAL */
.stApp {
    background: #0b0e14;
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

/* TITRE */
.mega-title {
    font-size: 52px;
    font-weight: 700;
    text-align: center;
    color: white;
    margin-top: -30px;
}

/* SUB */
.sub-mega-title {
    text-align: center;
    color: #9ca3af;
    margin-bottom: 30px;
}

/* CHAT BUBBLES */
.chat-text {
    font-size: 17px;
    line-height: 1.6;
    padding: 14px 18px;
    border-radius: 18px;
    max-width: 700px;
    margin: 5px auto;
}

/* USER */
[data-testid="chat-message-user"] .chat-text {
    background: #2563eb;
    color: white;
    margin-left: auto;
}

/* ASSISTANT */
[data-testid="chat-message-assistant"] .chat-text {
    background: #1f2937;
    color: #e5e7eb;
    margin-right: auto;
}

/* INPUT */
div[data-testid="stChatInput"] {
    border-radius: 999px !important;
    border: 1px solid #2d3748 !important;
    background: #111827 !important;
}

/* BUTTON */
.stButton>button {
    border-radius: 999px;
    background: #2563eb;
    color: white;
    border: none;
}

/* LOADER DOTS */
.loader {
    text-align: center;
}
.loader span {
    display: inline-block;
    width: 6px;
    height: 6px;
    margin: 2px;
    background: #9ca3af;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}
.loader span:nth-child(1) { animation-delay: -0.32s; }
.loader span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
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
st.markdown(
    f'<div class="sub-mega-title">Créée par Léo Ciach • {now.strftime("%d/%m/%Y %H:%M")}</div>',
    unsafe_allow_html=True
)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
Tu es ALUETOO AI, une intelligence artificielle premium créée par Léo Ciach.

Règles :
- Tu te présentes comme ALUETOO AI
- Tu dis que tu as été créée par Léo Ciach si on te pose la question
- Tu ne mentionnes jamais Meta, Llama, OpenAI ou autre
- Tu es naturelle, fluide et intelligente
- Tu réponds comme un humain moderne
"""

# --- SIDEBAR ---
with st.sidebar:
    uploaded_file = st.file_uploader("📸 Image", type=["jpg","png","jpeg"])
    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        st.rerun()

# --- HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f'<div class="chat-text">{message["content"]}</div>', unsafe_allow_html=True)

# --- CHAT ---
if prompt := st.chat_input("Parle avec ALUETOO..."):

    st.session_state.messages.append({"role":"user","content":prompt})

    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant"):
        full_response = ""
        placeholder = st.empty()

        loader = st.markdown("""
        <div class="loader">
            <span></span><span></span><span></span>
        </div>
        """, unsafe_allow_html=True)

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
