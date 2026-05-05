import streamlit as st
import json
from groq import Groq
from datetime import datetime
import pytz
import base64
import re
import time

# ============================================================================
# CONFIG
# ============================================================================
st.set_page_config(
    page_title="ALUETOO AI Pro",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp {
    font-family: 'DM Sans', -apple-system, sans-serif;
    -webkit-font-smoothing: antialiased;
    background: #08080f !important;
    color: #e8e8f0;
    min-height: 100vh;
}
#MainMenu, footer, header { display: none !important; }

/* ── FOND ANIMÉ AVEC ORBES ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 80vw 60vh at 15% 20%, rgba(99,88,255,0.18) 0%, transparent 70%),
        radial-gradient(ellipse 60vw 50vh at 85% 75%, rgba(20,180,120,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 50vw 40vh at 50% 10%, rgba(255,60,80,0.08) 0%, transparent 70%);
    animation: orbs 18s ease-in-out infinite alternate;
}
@keyframes orbs {
    0%   { filter: hue-rotate(0deg) brightness(1); }
    50%  { filter: hue-rotate(20deg) brightness(1.1); }
    100% { filter: hue-rotate(-15deg) brightness(0.95); }
}

/* ── VERRE (mixin réutilisable via classe) ── */
.glass {
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255,255,255,0.09);
    border-top-color: rgba(255,255,255,0.15);
    border-left-color: rgba(255,255,255,0.12);
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: rgba(10,10,20,0.7) !important;
    backdrop-filter: blur(40px) saturate(200%) !important;
    -webkit-backdrop-filter: blur(40px) saturate(200%) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    z-index: 100;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── SIDEBAR INNER ── */
.sidebar-inner {
    padding: 28px 18px 20px;
    display: flex; flex-direction: column; height: 100vh; gap: 10px;
}
.sidebar-logo {
    font-size: 20px; font-weight: 600; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #a78bfa, #60efff, #a78bfa);
    background-size: 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite;
    margin-bottom: 4px;
}
@keyframes shimmer { 0%{background-position:0%} 100%{background-position:200%} }

/* ── BOUTONS SIDEBAR ── */
.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: rgba(255,255,255,0.8) !important;
    border-radius: 12px !important;
    font-size: 13.5px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 400 !important;
    padding: 8px 14px !important;
    transition: all 0.2s ease !important;
    text-align: left !important;
}
.stButton > button:hover {
    background: rgba(167,139,250,0.15) !important;
    border-color: rgba(167,139,250,0.4) !important;
    color: white !important;
    transform: translateX(2px) !important;
}
[data-testid="baseButton-primary"] > button,
.stButton > button[kind="primary"] {
    background: rgba(167,139,250,0.2) !important;
    border-color: rgba(167,139,250,0.5) !important;
    color: #c4b5fd !important;
}

/* ── INPUT RECHERCHE ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,0.7) !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(167,139,250,0.4) !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.1) !important;
}

/* ── TITRE CENTRAL ── */
.ai-title {
    text-align: center;
    font-size: 46px;
    font-weight: 600;
    letter-spacing: -2px;
    line-height: 1;
    margin: 30px 0 6px;
    background: linear-gradient(
        135deg,
        rgba(255,255,255,0.95) 0%,
        rgba(167,139,250,0.9) 35%,
        rgba(96,239,255,0.85) 65%,
        rgba(255,255,255,0.95) 100%
    );
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 6s linear infinite;
}
.ai-sub {
    text-align: center;
    font-size: 13px;
    color: rgba(255,255,255,0.28);
    letter-spacing: 0.3px;
    margin-bottom: 28px;
}

/* ── BULLES CHAT ── */
.msg-row-user {
    display: flex; justify-content: flex-end;
    margin: 6px 0 2px; padding: 0 8px;
}
.msg-row-ai {
    display: flex; justify-content: flex-start;
    margin: 6px 0 0; padding: 0 8px;
}
.bubble-user {
    max-width: 68%;
    background: linear-gradient(135deg, rgba(99,88,255,0.85), rgba(124,58,237,0.75));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(167,139,250,0.3);
    border-top-color: rgba(200,180,255,0.5);
    color: rgba(255,255,255,0.95);
    padding: 11px 15px;
    border-radius: 18px 18px 4px 18px;
    font-size: 14.5px;
    line-height: 1.55;
    box-shadow: 0 4px 20px rgba(99,88,255,0.25), 0 0 0 0.5px rgba(255,255,255,0.05) inset;
}
.bubble-ai {
    max-width: 72%;
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255,255,255,0.09);
    border-top-color: rgba(255,255,255,0.16);
    border-left-color: rgba(255,255,255,0.12);
    color: rgba(235,235,245,0.92);
    padding: 11px 15px;
    border-radius: 18px 18px 18px 4px;
    font-size: 14.5px;
    line-height: 1.6;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3), 0 0 0 0.5px rgba(255,255,255,0.03) inset;
}

/* ── TOOLBAR ACTIONS ── */
.toolbar {
    display: flex; gap: 4px; margin: 2px 8px 12px 8px;
}
.toolbar-btn {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    color: rgba(255,255,255,0.35);
    border-radius: 8px;
    padding: 3px 9px;
    font-size: 11.5px;
    cursor: pointer;
    transition: all 0.15s;
    backdrop-filter: blur(10px);
}
.toolbar-btn:hover {
    background: rgba(167,139,250,0.12);
    border-color: rgba(167,139,250,0.3);
    color: rgba(255,255,255,0.75);
}

/* ── INDICATEUR STATUT ── */
.status-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 12.5px;
    color: rgba(255,255,255,0.45);
    margin: 8px 0 8px 8px;
}
.status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #30d158;
    box-shadow: 0 0 6px #30d158;
    animation: pulse-dot 1.4s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%,100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.7); }
}

/* ── INPUT CHAT ── */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.04) !important;
    backdrop-filter: blur(30px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(30px) saturate(180%) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-top-color: rgba(255,255,255,0.16) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 0 0.5px rgba(255,255,255,0.04) inset !important;
    max-width: 780px !important;
    margin: 4px auto 24px !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: rgba(255,255,255,0.85) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14.5px !important;
    padding: 13px 16px !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255,255,255,0.22) !important;
}

/* ── CODE BLOCKS ── */
pre, code {
    font-family: 'DM Mono', monospace !important;
    font-size: 13px !important;
}
pre {
    background: rgba(0,0,0,0.4) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    margin: 10px 0 !important;
    overflow-x: auto;
}

/* ── TOGGLE ── */
.stCheckbox > label, .stToggle > label {
    color: rgba(255,255,255,0.55) !important;
    font-size: 13px !important;
}

/* ── UPLOAD ── */
.stFileUploader { display: none !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(167,139,250,0.3); }

/* ── CAPTION / MISC ── */
.stCaption { color: rgba(255,255,255,0.2) !important; font-size: 11px !important; }
.stToast { background: rgba(30,30,50,0.9) !important; backdrop-filter: blur(20px) !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INIT CLIENT
# ============================================================================
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Clé GROQ_API_KEY manquante dans les secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ── Session state ──
defaults = {
    "conversations": {}, "current_id": None, "messages": [],
    "generating": False, "stop_gen": False, "auto_speak": False,
    "uploaded": None, "uploaded_name": None, "search_query": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Prompt système ──
SYSTEM = """Tu es ALUETOO AI, créée par Léo Ciach. Tu es précise, rapide et bienveillante.
● Raisonne logiquement, décompose les problèmes complexes étape par étape.
● Adapte ton ton et ta longueur au contexte de la question.
● Sois transparente : si tu n'es pas sûre, dis-le clairement.
● Reste neutre et équitable.
● Utilise ● pour les listes.
● Réponds TOUJOURS dans la langue de l'utilisateur."""

# ============================================================================
# HELPERS
# ============================================================================
def new_chat():
    cid = f"chat_{int(time.time())}"
    st.session_state.conversations[cid] = {
        "title": "Nouvelle discussion",
        "messages": [],
        "created": datetime.now()
    }
    st.session_state.current_id = cid
    st.session_state.messages = []

def save_current():
    cid = st.session_state.current_id
    if cid and st.session_state.messages:
        conv = st.session_state.conversations.get(cid)
        if conv:
            conv["messages"] = st.session_state.messages.copy()
            first = st.session_state.messages[0]["content"]
            conv["title"] = first[:45] + ("…" if len(first) > 45 else "")

def build_api_messages():
    api_msgs = [{"role": "system", "content": SYSTEM}]
    for m in st.session_state.messages:
        if m.get("image"):
            api_msgs.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": m["content"]},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{m['image']}"}}
                ]
            })
        else:
            api_msgs.append({"role": m["role"], "content": m["content"]})
    return api_msgs

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 28px 18px 0;">
        <div class="sidebar-logo">✦ ALUETOO AI</div>
        <div style="font-size:11px;color:rgba(255,255,255,0.2);margin-bottom:18px;">Pro Edition</div>
    </div>
    """, unsafe_allow_html=True)

    col_new, _ = st.columns([3, 1])
    with col_new:
        if st.button("＋  Nouveau chat", use_container_width=True, type="primary"):
            new_chat()
            st.rerun()

    search = st.text_input("", placeholder="🔍  Rechercher une discussion…", label_visibility="collapsed")
    st.session_state.search_query = search

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:8px 0 10px;"></div>', unsafe_allow_html=True)

    # Liste conversations
    sorted_convs = sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1]["created"], reverse=True
    )
    for cid, conv in sorted_convs:
        title = conv["title"]
        if search.lower() in title.lower() or not search:
            is_active = cid == st.session_state.current_id
            btn_type = "primary" if is_active else "secondary"
            if st.button(title, key=f"conv_{cid}", use_container_width=True, type=btn_type):
                st.session_state.current_id = cid
                st.session_state.messages = conv["messages"].copy()
                st.rerun()

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:10px 0;"></div>', unsafe_allow_html=True)
    st.session_state.auto_speak = st.toggle("🔊  Lecture automatique", value=st.session_state.auto_speak)
    st.caption("Raccourcis : ⌘K nouveau · ⌘/ rechercher")

# ── Init premier chat si vide ──
if not st.session_state.current_id:
    new_chat()

# ============================================================================
# HEADER
# ============================================================================
paris_time = datetime.now(pytz.timezone("Europe/Paris")).strftime("%H:%M")
st.markdown(f'<div class="ai-title">ALUETOO AI</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="ai-sub">Compute · Données · Algorithmes · Éthique &nbsp;·&nbsp; {paris_time}</div>',
    unsafe_allow_html=True
)

# ============================================================================
# ZONE MESSAGES
# ============================================================================
for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-row-user"><div class="bubble-user">{msg["content"]}</div></div>',
            unsafe_allow_html=True
        )
        if msg.get("image"):
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                st.image(base64.b64decode(msg["image"]), use_container_width=True)
    else:
        st.markdown(
            f'<div class="msg-row-ai"><div class="bubble-ai">{msg["content"]}</div></div>',
            unsafe_allow_html=True
        )
        # Toolbar actions
        c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 6])
        with c1:
            if st.button("📋", key=f"copy_{idx}", help="Copier"):
                st.toast("✓ Copié dans le presse-papier")
        with c2:
            if st.button("🔊", key=f"speak_{idx}", help="Écouter"):
                clean_text = re.sub(r'●', '.', msg["content"])
                st.components.v1.html(
                    f"<script>speechSynthesis.cancel();speechSynthesis.speak(Object.assign(new SpeechSynthesisUtterance({json.dumps(clean_text)}),{{lang:navigator.language}}))</script>",
                    height=0
                )
        with c3:
            if st.button("🔄", key=f"regen_{idx}", help="Régénérer"):
                # Supprime la réponse IA et relance
                st.session_state.messages = st.session_state.messages[:idx]
                st.rerun()
        with c4:
            if st.button("👍", key=f"like_{idx}", help="Bonne réponse"):
                st.toast("✓ Merci pour votre retour !")

# ============================================================================
# UPLOAD FICHIER (caché visuellement)
# ============================================================================
uploaded_file = st.file_uploader(
    "Joindre",
    type=["png", "jpg", "jpeg", "gif", "webp"],
    label_visibility="collapsed",
    key="file_uploader"
)
if uploaded_file:
    st.session_state.uploaded = base64.b64encode(uploaded_file.read()).decode()
    st.session_state.uploaded_name = uploaded_file.name

# Prévisualisation si image en attente
if st.session_state.uploaded:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(
            base64.b64decode(st.session_state.uploaded),
            caption=f"📎 {st.session_state.uploaded_name}",
            use_container_width=True
        )
    if st.button("✕ Retirer l'image"):
        st.session_state.uploaded = None
        st.session_state.uploaded_name = None
        st.rerun()

# ============================================================================
# BOUTON STOP (si génération en cours)
# ============================================================================
if st.session_state.generating:
    if st.button("⏹  Arrêter", type="primary", use_container_width=False):
        st.session_state.stop_gen = True
        st.rerun()

# ============================================================================
# SAISIE ET GÉNÉRATION
# ============================================================================
if prompt := st.chat_input("Message à ALUETOO…"):
    # Ajoute le message utilisateur
    user_msg = {"role": "user", "content": prompt}
    if st.session_state.uploaded:
        user_msg["image"] = st.session_state.uploaded

    st.session_state.messages.append(user_msg)
    save_current()

    # Affiche le message utilisateur immédiatement
    st.markdown(
        f'<div class="msg-row-user"><div class="bubble-user">{prompt}</div></div>',
        unsafe_allow_html=True
    )
    if user_msg.get("image"):
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.image(base64.b64decode(user_msg["image"]), use_container_width=True)

    # Indicateur
    status_ph = st.empty()
    status_ph.markdown(
        '<div class="status-pill"><div class="status-dot"></div> ALUETOO réfléchit…</div>',
        unsafe_allow_html=True
    )

    # Choix du modèle
    model = (
        "meta-llama/llama-4-scout-17b-16e-instruct"
        if user_msg.get("image")
        else "llama-3.3-70b-versatile"
    )

    # Génération streaming
    st.session_state.generating = True
    st.session_state.stop_gen = False
    placeholder = st.empty()
    full_response = ""

    try:
        api_messages = build_api_messages()
        stream = client.chat.completions.create(
            model=model,
            messages=api_messages,
            stream=True,
            temperature=0.7,
            max_tokens=2048
        )

        for chunk in stream:
            if st.session_state.stop_gen:
                break
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                status_ph.markdown(
                    '<div class="status-pill"><div class="status-dot"></div> Génération…</div>',
                    unsafe_allow_html=True
                )
                placeholder.markdown(
                    f'<div class="msg-row-ai"><div class="bubble-ai">{full_response}<span style="opacity:0.4">▌</span></div></div>',
                    unsafe_allow_html=True
                )

        placeholder.markdown(
            f'<div class="msg-row-ai"><div class="bubble-ai">{full_response}</div></div>',
            unsafe_allow_html=True
        )
        status_ph.empty()

        # Sauvegarde
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        save_current()

        # Lecture auto
        if st.session_state.auto_speak and full_response:
            clean_text = re.sub(r'●', '.', full_response)
            st.components.v1.html(
                f"<script>speechSynthesis.cancel();speechSynthesis.speak(Object.assign(new SpeechSynthesisUtterance({json.dumps(clean_text)}),{{lang:navigator.language}}))</script>",
                height=0
            )

    except Exception as e:
        status_ph.empty()
        st.error(f"Erreur API : {e}")
    finally:
        st.session_state.generating = False
        st.session_state.uploaded = None
        st.session_state.uploaded_name = None
        st.rerun()

