import streamlit as st
import json
from groq import Groq
from datetime import datetime
import pytz
import base64
import re
import time

st.set_page_config(page_title="ALUETOO AI Pro", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
* { font-family: -apple-system, 'SF Pro Display', sans-serif; -webkit-font-smoothing: antialiased; }
.stApp { background: #000; color: #f5f5f7; }
#MainMenu, footer, header { display: none; }

/* GRADIENT ANIMÉ ALUETOO */
@keyframes grad { 0%{background-position:0%} 100%{background-position:200%} }
.title {
    font-size: 40px; font-weight: 700; text-align: center; margin: 16px 0 8px 0;
    background: linear-gradient(90deg, #ff3b30, #af52de, #0a84ff, #30d158, #ff3b30);
    background-size: 200%; animation: grad 6s linear infinite;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* BULLES iMESSAGE */
.msg-user {
    background: linear-gradient(135deg, #0a84ff, #5e5ce6);
    color: white; padding: 10px 14px; border-radius: 18px 18px 4px 18px;
    max-width: 75%; margin-left: auto; margin-bottom: 8px; font-size: 15px;
}
.msg-ai {
    background: #1c1c1e; border: 0.5px solid #2c2c2e; color: #f5f5f7;
    padding: 10px 14px; border-radius: 18px 18px 18px 4px;
    max-width: 75%; margin-right: auto; margin-bottom: 8px; font-size: 15px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}

/* INPUT APPLE GLASS - FIX DÉFINITIF HAUTEUR */
[data-testid="stChatInput"] {
    position: fixed!important;
    bottom: 0!important;
    left: 0!important;
    right: 0!important;
    background: rgba(28, 28, 30, 0.8)!important;
    backdrop-filter: saturate(180%) blur(20px)!important;
    -webkit-backdrop-filter: saturate(180%) blur(20px)!important;
    border-top: 0.5px solid rgba(255, 255, 255, 0.15)!important;
    padding: 8px 16px 8px 16px!important;
    margin: 0!important;
    z-index: 999!important;
}

/* Conteneur interne de st.chat_input */
[data-testid="stChatInput"] > div {
    background: rgba(44, 44, 46, 0.6)!important;
    border: 0.5px solid rgba(255, 255, 255, 0.15)!important;
    border-radius: 20px!important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1)!important;
    max-height: 120px!important;
}

[data-testid="stChatInput"]:focus-within > div {
    border: 0.5px solid rgba(10, 132, 255, 0.6)!important;
    box-shadow:
        0 0 0 3px rgba(10, 132, 255, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.15)!important;
}

/* LE FIX: cibler la vraie textarea de baseweb */
[data-testid="stChatInput"] textarea {
    background: transparent!important;
    color: #f5f5f7!important;
    font-size: 16px!important;
    line-height: 20px!important;
    padding: 10px 44px 10px 14px!important;
    min-height: 20px!important;
    max-height: 100px!important;
    border: none!important;
    resize: none!important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(235, 235, 245, 0.5)!important;
}

/* BOUTON ENVOYER BLEU iOS */
[data-testid="stChatInputSubmitButton"] {
    background: #0a84ff!important;
    border-radius: 50%!important;
    right: 6px!important;
    bottom: 6px!important;
    width: 28px!important;
    height: 28px!important;
    min-width: 28px!important;
    min-height: 28px!important;
    border: none!important;
    transition: 0.2s!important;
}

[data-testid="stChatInputSubmitButton"]:hover {
    background: #0066cc!important;
    transform: scale(1.05)!important;
}

[data-testid="stChatInputSubmitButton"] svg {
    width: 16px!important;
    height: 16px!important;
    color: white!important;
}

/* BOUTONS CUSTOM */
.input-btn {
    position: absolute;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(60, 60, 62, 0.8);
    border: none;
    color: #8e8e93;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    z-index: 1000;
    bottom: 6px;
    transition: 0.2s;
}

.input-btn:hover {
    background: rgba(10, 132, 255, 0.8);
    color: white;
}

.mic { right: 40px; }
.attach { right: 72px; }

/* STATUS BAR */
.status-bar {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px; background: rgba(28, 28, 30, 0.8);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 12px;
    margin: 8px auto; font-size: 12px; color: #8e8e93;
    border: 0.5px solid rgba(255, 255, 255, 0.1);
    max-width: 180px;
}
.status-dot {
    width: 6px; height: 6px; border-radius: 50%; background: #30d158;
    animation: blink 1.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Cache uploader */
[data-testid="stFileUploader"] { display: none; }

/* Padding pour pas que le chat soit sous l'input */
.main.block-container {
    padding-bottom: 80px!important;
    padding-top: 1rem!important;
}
</style>
""", unsafe_allow_html=True)

if "GROQ_API_KEY" not in st.secrets:
    st.error("Ajoute GROQ_API_KEY dans.streamlit/secrets.toml")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

defaults = {
    "conversations": {}, "current_id": None, "messages": [],
    "generating": False, "stop_gen": False, "uploaded": None
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

SYSTEM = """Tu es ALUETOO AI créée par Léo Ciach. Tu es premium, rapide, éthique.
- Raisonnement logique, décompose les problèmes
- Adaptabilité : ajuste selon contexte
- Utilise ● pour listes
- Réponds dans la langue de l'utilisateur"""

def new_chat():
    cid = f"chat_{int(time.time())}"
    st.session_state.conversations[cid] = {"title": "Nouvelle discussion", "messages": [], "created": datetime.now()}
    st.session_state.current_id = cid
    st.session_state.messages = []

def save_current():
    if st.session_state.current_id and st.session_state.messages:
        st.session_state.conversations[st.session_state.current_id]["messages"] = st.session_state.messages
        if st.session_state.messages:
            first = st.session_state.messages[0]["content"][:40]
            st.session_state.conversations[st.session_state.current_id]["title"] = first

with st.sidebar:
    st.markdown("### ✨ ALUETOO Pro")
    if st.button("➕ Nouveau chat", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()
    st.markdown("---")
    for cid, conv in sorted(st.session_state.conversations.items(), key=lambda x: x[1]["created"], reverse=True):
        title = conv["title"]
        is_active = cid == st.session_state.current_id
        if st.button(title, key=cid, use_container_width=True, type="secondary" if not is_active else "primary"):
            st.session_state.current_id = cid
            st.session_state.messages = conv["messages"].copy()
            st.rerun()

if not st.session_state.current_id:
    new_chat()

st.markdown('<div class="title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;color:#86868b;font-size:13px;margin-bottom:20px;">Fondations: Compute • Données • Algorithmes • Éthique • {datetime.now(pytz.timezone("Europe/Paris")).strftime("%H:%M")}</div>', unsafe_allow_html=True)

chat_container = st.container()

with chat_container:
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"):
                st.image(base64.b64decode(msg["image"]), width=250)
        else:
            st.markdown(f'<div class="msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1,1,8])
            with col1:
                if st.button("📋", key=f"copy{idx}", help="Copier"):
                    st.toast("Copié!")
            with col2:
                if st.button("🔄", key=f"regen{idx}", help="Régénérer"):
                    st.session_state.messages = st.session_state.messages[:idx]
                    st.rerun()

# JS: force rows=1 + ajoute boutons
st.components.v1.html("""
<script>
function fixInput() {
    const input = window.parent.document.querySelector('[data-testid="stChatInput"]');
    if (!input) return;

    const ta = input.querySelector('textarea');
    if (ta) {
        ta.setAttribute('rows', '1');
        ta.style.height = '20px';
    }

    if (input.querySelector('.mic')) return;

    const mic = document.createElement('button');
    mic.innerHTML = '🎤'; mic.className = 'input-btn mic';
    mic.onclick = () => {
        const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        r.lang = 'fr-FR'; r.start();
        r.onresult = e => {
            ta.value = e.results[0][0].transcript;
            ta.dispatchEvent(new Event('input', {bubbles:true}));
        };
    };

    const attach = document.createElement('button');
    attach.innerHTML = '📎'; attach.className = 'input-btn attach';
    attach.onclick = () => {
        const fileInput = window.parent.document.querySelector('input[type=file]');
        if(fileInput) fileInput.click();
    };

    input.appendChild(mic); input.appendChild(attach);
}
setInterval(fixInput, 300);
</script>
""", height=0)

uploaded = st.file_uploader("", type=["png","jpg","jpeg","pdf","txt"], label_visibility="collapsed")
if uploaded:
    st.session_state.uploaded = base64.b64encode(uploaded.read()).decode()
    st.toast(f"Fichier {uploaded.name} prêt")

if prompt := st.chat_input("Message à ALUETOO..."):
    user_msg = {"role": "user", "content": prompt}
    if st.session_state.uploaded:
        user_msg["image"] = st.session_state.uploaded

    st.session_state.messages.append(user_msg)
    save_current()

    st.markdown(f'<div class="msg-user">{prompt}</div>', unsafe_allow_html=True)
    if user_msg.get("image"):
        st.image(base64.b64decode(user_msg["image"]), width=250)

    status = st.empty()
    status.markdown('<div class="status-bar"><div class="status-dot"></div> ALUETOO réfléchit...</div>', unsafe_allow_html=True)

    api_msgs = [{"role": "system", "content": SYSTEM}]
    for m in st.session_state.messages:
        if m.get("image"):
            api_msgs.append({"role": "user", "content": [
                {"type": "text", "text": m["content"]},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{m['image']}"}}
            ]})
        else:
            api_msgs.append({"role": m["role"], "content": m["content"]})

    model = "meta-llama/llama-4-scout-17b-16e-instruct" if user_msg.get("image") else "llama-3.3-70b-versatile"

    st.session_state.generating = True
    placeholder = st.empty()
    full = ""

    try:
        stream = client.chat.completions.create(model=model, messages=api_msgs, stream=True, temperature=0.7)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                placeholder.markdown(f'<div class="msg-ai">{full}▌</div>', unsafe_allow_html=True)

        placeholder.markdown(f'<div class="msg-ai">{full}</div>', unsafe_allow_html=True)
        status.empty()
        st.session_state.messages.append({"role": "assistant", "content": full})
        save_current()

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        st.session_state.generating = False
        st.session_state.uploaded = None
        st.rerun()
