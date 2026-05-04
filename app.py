import streamlit as st
import json
from groq import Groq
from datetime import datetime
import pytz
import base64
import re
import time

# ============================================================================
# CONFIG APPLE PRO
# ============================================================================
st.set_page_config(page_title="ALUETOO AI Pro", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
* { font-family: -apple-system, 'SF Pro Display', sans-serif; -webkit-font-smoothing: antialiased; }
.stApp { background: #000; color: #f5f5f7; }
#MainMenu, footer, header { display: none; }

/* GRADIENT ANIMÉ ALUETOO */
@keyframes grad { 0%{background-position:0%} 100%{background-position:200%} }
.title {
    font-size: 52px; font-weight: 700; text-align: center; margin: 20px 0;
    background: linear-gradient(90deg, #ff3b30, #af52de, #0a84ff, #30d158, #ff3b30);
    background-size: 200%; animation: grad 6s linear infinite;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* LAYOUT 3 COLONNES APPLE */
.main-container { display: flex; max-width: 1400px; margin: 0 auto; gap: 20px; padding: 0 20px; }
.chat-area { flex: 1; max-width: 800px; margin: 0 auto; }

/* BULLES iMESSAGE */
.msg-user {
    background: linear-gradient(135deg, #0a84ff, #5e5ce6);
    color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px;
    max-width: 75%; margin-left: auto; margin-bottom: 8px; font-size: 15px;
    box-shadow: 0 2px 8px rgba(10,132,255,0.3);
}
.msg-ai {
    background: #1c1c1e; border: 0.5px solid #2c2c2e; color: #f5f5f7;
    padding: 12px 16px; border-radius: 18px 18px 18px 4px;
    max-width: 75%; margin-right: auto; margin-bottom: 4px; font-size: 15px;
    backdrop-filter: blur(20px);
}

/* BARRE OUTILS MESSAGE */
.msg-toolbar {
    display: flex; gap: 8px; margin: 0 0 16px 0; opacity: 0; transition: 0.2s;
}
.msg-ai:hover +.msg-toolbar,.msg-toolbar:hover { opacity: 1; }
.tool-btn {
    background: #2c2c2e; border: none; color: #8e8e93; padding: 4px 10px;
    border-radius: 6px; font-size: 12px; cursor: pointer; transition: 0.15s;
}
.tool-btn:hover { background: #3a3a3c; color: white; }

/* INPUT APPLE */
[data-testid="stChatInput"] {
    background: #1c1c1e!important; border: 1px solid #333!important;
    border-radius: 24px!important; max-width: 720px!important; margin: 0 auto 20px!important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5)!important;
}
[data-testid="stChatInput"] textarea {
    background: transparent!important; color: white!important;
    padding: 12px 100px 12px 16px!important; font-size: 15px!important;
}

/* BOUTONS INPUT */
.input-btn {
    position: absolute; width: 32px; height: 32px; border-radius: 50%;
    background: #2c2c2e; border: none; color: #8e8e93; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; z-index: 1000; transition: 0.2s;
}
.input-btn:hover { background: #0a84ff; color: white; transform: scale(1.05); }
.mic { right: 52px; bottom: 8px; }
.attach { right: 14px; bottom: 8px; }
.stop-btn {
    background: #ff3b30!important; color: white!important;
    animation: pulse 1s infinite;
}
@keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.1)} }

/* SIDEBAR HISTORIQUE */
.sidebar-history {
    background: #0c0c0e; border-right: 1px solid #1c1c1e;
    height: 100vh; overflow-y: auto; padding: 20px;
}
.history-item {
    padding: 10px 12px; margin: 4px 0; border-radius: 8px;
    background: #1c1c1e; cursor: pointer; font-size: 13px;
    border: 1px solid transparent; transition: 0.15s;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.history-item:hover { background: #2c2c2e; border-color: #0a84ff; }
.history-item.active { background: #0a84ff20; border-color: #0a84ff; }

/* INDICATEUR STATUT */
.status-bar {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 16px; background: #1c1c1e; border-radius: 12px;
    margin: 10px 0; font-size: 13px; color: #8e8e93;
    border: 1px solid #2c2c2e;
}
.status-dot {
    width: 8px; height: 8px; border-radius: 50%; background: #30d158;
    animation: blink 1.5s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* CODE BLOCKS */
pre {
    background: #0c0c0e!important; border: 1px solid #2c2c2e!important;
    border-radius: 10px!important; padding: 12px!important; margin: 8px 0!important;
    overflow-x: auto; position: relative;
}
.copy-code {
    position: absolute; top: 8px; right: 8px;
    background: #2c2c2e; border: none; color: #8e8e93;
    padding: 4px 8px; border-radius: 5px; font-size: 11px; cursor: pointer;
}
.copy-code:hover { background: #0a84ff; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INIT
# ============================================================================
if "GROQ_API_KEY" not in st.secrets: st.stop()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Session state complet
defaults = {
    "conversations": {}, "current_id": None, "messages": [],
    "generating": False, "stop_gen": False, "auto_speak": True,
    "uploaded": None, "search_query": ""
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

SYSTEM = """Tu es ALUETOO AI créée par Léo Ciach. Tu es premium, rapide, éthique.
- Raisonnement logique, décompose les problèmes
- Adaptabilité : ajuste selon contexte
- Transparence : explique ton raisonnement si demandé
- Neutralité : évite biais, respecte équité
- Confidentialité : ne stocke rien
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

# ============================================================================
# SIDEBAR - HISTORIQUE ET CONTRÔLES
# ============================================================================
with st.sidebar:
    st.markdown("### ✨ ALUETOO Pro")

    if st.button("➕ Nouveau chat", use_container_width=True, type="primary"):
        new_chat()
        st.rerun()

    # Recherche historique
    search = st.text_input("🔍 Rechercher", placeholder="Mots-clés...", label_visibility="collapsed")
    st.session_state.search_query = search

    st.markdown("---")

    # Liste conversations
    for cid, conv in sorted(st.session_state.conversations.items(), key=lambda x: x[1]["created"], reverse=True):
        title = conv["title"]
        if search.lower() in title.lower() or not search:
            is_active = cid == st.session_state.current_id
            if st.button(title, key=cid, use_container_width=True, type="secondary" if not is_active else "primary"):
                st.session_state.current_id = cid
                st.session_state.messages = conv["messages"].copy()
                st.rerun()

    st.markdown("---")
    st.session_state.auto_speak = st.toggle("🔊 Lecture auto", value=st.session_state.auto_speak)
    st.caption("Raccourcis: ⌘K nouveau, ⌘/ rechercher")

# Init premier chat
if not st.session_state.current_id:
    new_chat()

# ============================================================================
# HEADER
# ============================================================================
st.markdown('<div class="title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:center;color:#86868b;font-size:13px;margin-bottom:25px;">Fondations: Compute • Données • Algorithmes • Éthique • {datetime.now(pytz.timezone("Europe/Paris")).strftime("%H:%M")}</div>', unsafe_allow_html=True)

# ============================================================================
# ZONE CHAT
# ============================================================================
chat_container = st.container()

with chat_container:
    for idx, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f'<div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("image"):
                st.image(base64.b64decode(msg["image"]), width=250)
        else:
            # Message IA avec toolbar
            st.markdown(f'<div class="msg-ai" id="msg-{idx}">{msg["content"]}</div>', unsafe_allow_html=True)

            # Toolbar
            col1, col2, col3, col4, col5 = st.columns([1,1,6])
            with col1:
                if st.button("📋", key=f"copy{idx}", help="Copier"):
                    st.toast("Copié!")
            with col2:
                if st.button("🔊", key=f"speak{idx}", help="Lire"):
                    clean = re.sub(r'●', '. ', msg["content"])
                    st.components.v1.html(f"<script>speechSynthesis.speak(new SpeechSynthesisUtterance({json.dumps(clean)}))</script>", height=0)
            with col3:
                if st.button("🔄", key=f"regen{idx}", help="Régénérer"):
                    # Régénère la réponse
                    st.session_state.messages = st.session_state.messages[:idx]
                    st.rerun()
            with col4:
                if st.button("👍", key=f"up{idx}", help="Bien") or st.button("👎", key=f"down{idx}", help="Mal"):
                    st.toast("Feedback enregistré")

# ============================================================================
# INPUT AVEC BOUTONS
# ============================================================================
# Injection JS pour boutons
st.components.v1.html("""
<script>
function addButtons() {
    const input = window.parent.document.querySelector('[data-testid="stChatInput"]');
    if (!input || input.querySelector('.mic')) return;

    const mic = document.createElement('button');
    mic.innerHTML = '🎤'; mic.className = 'input-btn mic'; mic.title = 'Dicter (⌘⇧V)';
    mic.onclick = () => {
        const r = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        r.lang = navigator.language; r.start();
        mic.classList.add('stop-btn'); mic.innerHTML = '⏹';
        r.onresult = e => {
            document.querySelector('textarea').value = e.results[0][0].transcript;
            document.querySelector('textarea').dispatchEvent(new Event('input', {bubbles:true}));
        };
        r.onend = () => { mic.classList.remove('stop-btn'); mic.innerHTML = '🎤'; };
    };

    const attach = document.createElement('button');
    attach.innerHTML = '📎'; attach.className = 'input-btn attach'; attach.title = 'Joindre';
    attach.onclick = () => document.querySelector('input[type=file]').click();

    input.appendChild(mic); input.appendChild(attach);
}
setInterval(addButtons, 500);
</script>
""", height=0)

# Upload caché
uploaded = st.file_uploader("", type=["png","jpg","jpeg","pdf","txt"], label_visibility="collapsed")
if uploaded:
    st.session_state.uploaded = base64.b64encode(uploaded.read()).decode()

# ============================================================================
# GESTION PROMPT
# ============================================================================
if prompt := st.chat_input("Message à ALUETOO... (⌘↵ pour envoyer)"):
    # Ajout message
    user_msg = {"role": "user", "content": prompt}
    if st.session_state.uploaded:
        user_msg["image"] = st.session_state.uploaded

    st.session_state.messages.append(user_msg)
    save_current()

    # Affichage user
    st.markdown(f'<div class="msg-user">{prompt}</div>', unsafe_allow_html=True)
    if user_msg.get("image"):
        st.image(base64.b64decode(user_msg["image"]), width=250)

    # Indicateur statut
    status = st.empty()
    status.markdown('<div class="status-bar"><div class="status-dot"></div> ALUETOO réfléchit...</div>', unsafe_allow_html=True)

    # Préparation API
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

    # Génération avec STOP
    st.session_state.generating = True
    st.session_state.stop_gen = False

    placeholder = st.empty()
    full = ""

    try:
        stream = client.chat.completions.create(model=model, messages=api_msgs, stream=True, temperature=0.7)

        for chunk in stream:
            if st.session_state.stop_gen:
                break
            if chunk.choices[0].delta.content:
                full += chunk.choices[0].delta.content
                status.markdown('<div class="status-bar"><div class="status-dot"></div> Génération en cours...</div>', unsafe_allow_html=True)
                placeholder.markdown(f'<div class="msg-ai">{full}▌</div>', unsafe_allow_html=True)

        placeholder.markdown(f'<div class="msg-ai">{full}</div>', unsafe_allow_html=True)
        status.empty()

        st.session_state.messages.append({"role": "assistant", "content": full})
        save_current()

        if st.session_state.auto_speak:
            clean = re.sub(r'●', '. ', full)
            st.components.v1.html(f"<script>speechSynthesis.speak(new SpeechSynthesisUtterance({json.dumps(clean)}))</script>", height=0)

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        st.session_state.generating = False
        st.session_state.uploaded = None
        st.rerun()

# Bouton STOP si génération
if st.session_state.generating:
    if st.button("⏹ Arrêter la génération", type="primary"):
        st.session_state.stop_gen = True
        st.rerun()
