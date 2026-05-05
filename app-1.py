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
    page_title="ALUETOO AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

/* ══ RESET ══ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, .stApp {
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
    background: #07070e !important;
    color: #e2e2ec;
    min-height: 100vh;
    overflow-x: hidden;
}
#MainMenu, footer, header, .stDeployButton { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ══ ORBES FOND ══ */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 70vw 55vh at 10% 15%, rgba(88,76,255,0.22) 0%, transparent 65%),
        radial-gradient(ellipse 55vw 45vh at 88% 80%, rgba(16,185,129,0.13) 0%, transparent 65%),
        radial-gradient(ellipse 45vw 35vh at 55% 5%,  rgba(239,68,68,0.09) 0%, transparent 65%),
        radial-gradient(ellipse 60vw 50vh at 30% 90%, rgba(124,58,237,0.10) 0%, transparent 65%);
    animation: orbs 20s ease-in-out infinite alternate;
}
@keyframes orbs {
    0%   { filter: hue-rotate(0deg)   brightness(1);    transform: scale(1); }
    50%  { filter: hue-rotate(15deg)  brightness(1.08); transform: scale(1.03); }
    100% { filter: hue-rotate(-10deg) brightness(0.96); transform: scale(0.98); }
}

/* ══ DRAWER SIDEBAR ══ */
#sidebar-overlay {
    display: none; position: fixed; inset: 0; z-index: 998;
    background: rgba(0,0,0,0.5);
    backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
}
#sidebar-overlay.open { display: block; }
#sidebar-drawer {
    position: fixed; top: 0; left: -320px; width: 300px; height: 100vh;
    z-index: 999; transition: left 0.3s cubic-bezier(0.25,0.46,0.45,0.94);
    background: rgba(10,10,20,0.93);
    backdrop-filter: blur(40px) saturate(200%); -webkit-backdrop-filter: blur(40px) saturate(200%);
    border-right: 1px solid rgba(255,255,255,0.07);
    display: flex; flex-direction: column;
    padding: 28px 16px 24px; overflow-y: auto;
}
#sidebar-drawer.open { left: 0; }

@keyframes shimmer { 0%{background-position:0%} 100%{background-position:200%} }
.drawer-logo {
    font-size: 19px; font-weight: 600; letter-spacing: -0.4px;
    background: linear-gradient(135deg, #a78bfa, #67e8f9, #a78bfa);
    background-size: 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 5s linear infinite;
    margin-bottom: 3px;
}
.drawer-sub { font-size: 10.5px; color: rgba(255,255,255,0.2); margin-bottom: 20px; text-transform: uppercase; letter-spacing: 0.6px; }
.drawer-new-btn {
    width: 100%; background: rgba(167,139,250,0.15);
    border: 1px solid rgba(167,139,250,0.35); border-radius: 12px;
    color: #c4b5fd; font-family: 'DM Sans',sans-serif; font-size: 13.5px;
    padding: 9px 14px; cursor: pointer; margin-bottom: 12px;
    transition: all 0.2s; text-align: left; font-weight: 500;
}
.drawer-new-btn:hover { background: rgba(167,139,250,0.25); transform: translateX(2px); }
.drawer-search {
    width: 100%; background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;
    color: rgba(255,255,255,0.7); font-size: 13px; font-family: 'DM Sans',sans-serif;
    padding: 8px 12px; margin-bottom: 12px; outline: none; transition: border-color 0.2s;
}
.drawer-search:focus { border-color: rgba(167,139,250,0.45); }
.drawer-divider { height:1px; background:rgba(255,255,255,0.06); margin:4px 0 10px; }
.conv-item {
    padding: 9px 12px; border-radius: 10px; cursor: pointer;
    font-size: 13px; color: rgba(255,255,255,0.5);
    border: 1px solid transparent; margin-bottom: 3px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    transition: all 0.15s;
}
.conv-item:hover { background:rgba(255,255,255,0.05); color:rgba(255,255,255,0.8); }
.conv-item.active { background:rgba(167,139,250,0.12); border-color:rgba(167,139,250,0.3); color:#c4b5fd; }
.drawer-footer {
    margin-top: auto; padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.06);
    font-size: 11px; color: rgba(255,255,255,0.18);
    text-align: center; line-height: 1.8;
}

/* ══ TOPBAR ══ */
.topbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 100; height: 52px;
    background: rgba(7,7,14,0.8);
    backdrop-filter: blur(30px) saturate(180%); -webkit-backdrop-filter: blur(30px) saturate(180%);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; justify-content: space-between; padding: 0 20px;
}
.topbar-left { display:flex; align-items:center; gap:12px; }
.menu-btn {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.09);
    border-radius: 9px; color: rgba(255,255,255,0.6);
    width:34px; height:34px; cursor:pointer; font-size:15px;
    display:flex; align-items:center; justify-content:center; transition: all 0.2s;
}
.menu-btn:hover { background:rgba(167,139,250,0.15); color:#c4b5fd; }
.topbar-title {
    font-size:15px; font-weight:600; letter-spacing:-0.3px;
    background: linear-gradient(135deg, #a78bfa, #67e8f9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.status-badge {
    display:flex; align-items:center; gap:5px;
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.07);
    border-radius:20px; padding:4px 10px; font-size:11.5px; color:rgba(255,255,255,0.3);
}
.status-dot-green {
    width:6px; height:6px; border-radius:50%; background:#30d158;
    box-shadow:0 0 5px #30d158; animation: blink 2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* ══ LAYOUT PRINCIPAL ══ */
.main-wrap { max-width:760px; margin:0 auto; padding:62px 16px 170px; position:relative; z-index:1; }

/* ══ HERO ══ */
.hero { text-align:center; padding:60px 0 36px; }
.hero-title {
    font-size: clamp(36px,8vw,58px);
    font-weight:600; letter-spacing:-2.5px; line-height:1;
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(167,139,250,0.9) 30%, rgba(96,239,255,0.85) 60%, rgba(255,255,255,0.9) 100%);
    background-size:200%;
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    animation: shimmer 7s linear infinite; margin-bottom:10px;
}
.hero-sub { font-size:14px; color:rgba(255,255,255,0.22); letter-spacing:0.2px; line-height:1.7; }
.hero-author { font-size:11px; color:rgba(255,255,255,0.13); margin-top:5px; font-style:italic; }
.suggestions { display:flex; flex-wrap:wrap; gap:8px; justify-content:center; margin-top:32px; }
.sug-chip {
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.09);
    border-top-color:rgba(255,255,255,0.14); border-radius:20px; padding:8px 16px;
    font-size:13px; color:rgba(255,255,255,0.42); cursor:pointer; transition:all 0.2s;
    backdrop-filter:blur(12px);
}
.sug-chip:hover { background:rgba(167,139,250,0.12); border-color:rgba(167,139,250,0.35); color:rgba(255,255,255,0.8); transform:translateY(-1px); }

/* ══ BULLES ══ */
.msg-row-user { display:flex; justify-content:flex-end; margin:8px 0 2px; }
.msg-row-ai   { display:flex; justify-content:flex-start;  margin:8px 0 0; }
.bubble-user {
    max-width:72%;
    background: linear-gradient(135deg, rgba(88,76,255,0.8), rgba(124,58,237,0.7));
    backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
    border:1px solid rgba(167,139,250,0.25); border-top-color:rgba(200,180,255,0.45);
    color:rgba(255,255,255,0.93); padding:11px 15px;
    border-radius:18px 18px 4px 18px; font-size:14.5px; line-height:1.58;
    box-shadow:0 4px 20px rgba(88,76,255,0.2); word-break:break-word;
}
.bubble-ai {
    max-width:78%;
    background:rgba(255,255,255,0.035);
    backdrop-filter:blur(30px) saturate(180%); -webkit-backdrop-filter:blur(30px) saturate(180%);
    border:1px solid rgba(255,255,255,0.08); border-top-color:rgba(255,255,255,0.14); border-left-color:rgba(255,255,255,0.11);
    color:rgba(232,232,240,0.92); padding:12px 15px;
    border-radius:18px 18px 18px 4px; font-size:14.5px; line-height:1.65;
    box-shadow:0 8px 32px rgba(0,0,0,0.3); word-break:break-word;
}
.bubble-ai code {
    font-family:'DM Mono',monospace; background:rgba(0,0,0,0.35);
    border:1px solid rgba(255,255,255,0.08); border-radius:5px; padding:1px 6px; font-size:12.5px;
}
pre { background:rgba(0,0,0,0.4)!important; border:1px solid rgba(255,255,255,0.07)!important; border-radius:10px!important; padding:12px 14px!important; margin:8px 0!important; overflow-x:auto; font-family:'DM Mono',monospace!important; font-size:12.5px!important; }

/* ══ STATUT ══ */
.status-pill {
    display:inline-flex; align-items:center; gap:8px;
    background:rgba(255,255,255,0.04); backdrop-filter:blur(20px);
    border:1px solid rgba(255,255,255,0.08); border-radius:20px;
    padding:7px 14px; font-size:12.5px; color:rgba(255,255,255,0.38); margin:6px 0;
}
.thinking-dots span {
    display:inline-block; width:4px; height:4px; border-radius:50%;
    background:rgba(167,139,250,0.7); margin:0 1.5px;
    animation:bounce 1.2s ease-in-out infinite;
}
.thinking-dots span:nth-child(2){animation-delay:0.2s}
.thinking-dots span:nth-child(3){animation-delay:0.4s}
@keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-5px)}}

/* ══ BARRE INPUT FIXE ══ */
.input-bar-wrapper {
    position:fixed; bottom:0; left:0; right:0; z-index:200;
    padding:10px 16px 22px;
    background: linear-gradient(to top, rgba(7,7,14,0.99) 55%, transparent);
}
.input-bar-inner { max-width:760px; margin:0 auto; }
.input-glass {
    background:rgba(255,255,255,0.05);
    backdrop-filter:blur(40px) saturate(200%); -webkit-backdrop-filter:blur(40px) saturate(200%);
    border:1px solid rgba(255,255,255,0.11); border-top-color:rgba(255,255,255,0.18);
    border-radius:22px;
    box-shadow:0 8px 40px rgba(0,0,0,0.5), 0 0 0 0.5px rgba(255,255,255,0.04) inset;
    overflow:hidden;
}
.img-preview-bar {
    display:flex; align-items:center; gap:8px; padding:10px 14px 0;
}
.img-preview-bar img {
    width:44px; height:44px; object-fit:cover;
    border-radius:9px; border:1px solid rgba(255,255,255,0.1);
}
.remove-img-btn {
    background:rgba(255,59,48,0.2); border:1px solid rgba(255,59,48,0.3);
    border-radius:6px; color:#ff6b60; font-size:11px; padding:3px 7px;
    cursor:pointer; transition:0.15s; font-family:'DM Sans',sans-serif;
}
.remove-img-btn:hover { background:rgba(255,59,48,0.35); }

/* Override Streamlit chat input */
[data-testid="stChatInput"] {
    background:transparent!important; border:none!important;
    border-radius:0!important; box-shadow:none!important;
    padding:0!important; margin:0!important; max-width:100%!important;
}
[data-testid="stChatInput"] > div {
    background:transparent!important; border:none!important;
    border-radius:0!important; padding:4px 8px!important;
}
[data-testid="stChatInput"] textarea {
    background:transparent!important; color:rgba(255,255,255,0.85)!important;
    font-family:'DM Sans',sans-serif!important; font-size:14.5px!important;
    padding:10px 52px 10px 14px!important; min-height:44px!important; resize:none!important;
}
[data-testid="stChatInput"] textarea::placeholder { color:rgba(255,255,255,0.2)!important; }
[data-testid="stChatInput"] button {
    background:rgba(167,139,250,0.22)!important; border:1px solid rgba(167,139,250,0.4)!important;
    border-radius:12px!important; margin-right:8px!important;
}

/* Boutons d'action sous l'input */
.bar-actions {
    display:flex; align-items:center; justify-content:space-between;
    padding:4px 12px 10px;
}
.bar-left { display:flex; gap:5px; align-items:center; }
.action-btn {
    display:flex; align-items:center; gap:5px;
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);
    border-radius:10px; color:rgba(255,255,255,0.38);
    padding:5px 11px; font-size:13px; cursor:pointer; transition:all 0.2s;
    font-family:'DM Sans',sans-serif;
}
.action-btn:hover { background:rgba(167,139,250,0.12); border-color:rgba(167,139,250,0.3); color:rgba(255,255,255,0.75); }
.action-btn.recording {
    background:rgba(255,59,48,0.15)!important; border-color:rgba(255,59,48,0.4)!important;
    color:#ff6b60!important; animation:pulse-rec 1s ease-in-out infinite;
}
@keyframes pulse-rec{0%,100%{box-shadow:0 0 0 0 rgba(255,59,48,0.3)}50%{box-shadow:0 0 0 6px rgba(255,59,48,0)}}
.stop-btn {
    display:flex; align-items:center; gap:5px;
    background:rgba(255,59,48,0.15); border:1px solid rgba(255,59,48,0.35);
    border-radius:10px; color:#ff6b60; padding:5px 12px; font-size:13px;
    cursor:pointer; font-family:'DM Sans',sans-serif; transition:all 0.15s;
}
.stop-btn:hover { background:rgba(255,59,48,0.25); }
.bar-hint { font-size:11px; color:rgba(255,255,255,0.13); }

/* Cache upload natif */
.stFileUploader { display:none!important; }
[data-testid="stFileUploader"] { display:none!important; }

/* Misc */
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:rgba(255,255,255,0.08);border-radius:2px}
::-webkit-scrollbar-thumb:hover{background:rgba(167,139,250,0.25)}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INIT
# ============================================================================
if "GROQ_API_KEY" not in st.secrets:
    st.error("⚠️ Clé GROQ_API_KEY manquante dans les secrets Streamlit.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

defaults = {
    "conversations": {}, "current_id": None, "messages": [],
    "generating": False, "stop_gen": False, "auto_speak": False,
    "uploaded_b64": None, "uploaded_name": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

SYSTEM = """Tu es ALUETOO AI, une intelligence artificielle créée par Léo Ciach.
Tu n'es pas créée par Meta, Anthropic, OpenAI ou Google. Tu es ALUETOO AI, point.
● Raisonne logiquement, décompose les problèmes complexes.
● Adapte ton ton et ta longueur au contexte.
● Si tu n'es pas sûre, dis-le clairement.
● Reste neutre et équitable.
● Utilise ● pour les listes.
● Réponds TOUJOURS dans la langue de l'utilisateur."""

SUGGESTIONS = [
    "✍️ Aide-moi à rédiger un email",
    "💡 Explique l'IA simplement",
    "🔧 Débogue mon code",
    "🌍 Traduis un texte",
    "📊 Analyse des données",
    "🎨 Idées créatives",
]

# ============================================================================
# HELPERS
# ============================================================================
def new_chat():
    cid = f"chat_{int(time.time()*1000)}"
    st.session_state.conversations[cid] = {
        "title": "Nouvelle discussion",
        "messages": [],
        "created": datetime.now()
    }
    st.session_state.current_id = cid
    st.session_state.messages = []

def save_current():
    cid = st.session_state.current_id
    if not cid: return
    conv = st.session_state.conversations.get(cid)
    if not conv: return
    conv["messages"] = st.session_state.messages.copy()
    if st.session_state.messages:
        first = st.session_state.messages[0]["content"]
        conv["title"] = first[:44] + ("…" if len(first) > 44 else "")

def build_api_messages():
    api = [{"role": "system", "content": SYSTEM}]
    for m in st.session_state.messages:
        if m.get("image"):
            api.append({"role": "user", "content": [
                {"type": "text", "text": m["content"]},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{m['image']}"}}
            ]})
        else:
            api.append({"role": m["role"], "content": m["content"]})
    return api

def speak_text(text):
    clean = re.sub(r'[●#*`]', ' ', text)
    st.components.v1.html(
        f"""<script>
        speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance({json.dumps(clean)});
        u.lang = navigator.language || 'fr-FR';
        speechSynthesis.speak(u);
        </script>""", height=0
    )

if not st.session_state.current_id:
    new_chat()

# ============================================================================
# TOPBAR + DRAWER HTML
# ============================================================================
paris_time = datetime.now(pytz.timezone("Europe/Paris")).strftime("%H:%M")

conv_items_html = ""
for cid, conv in sorted(st.session_state.conversations.items(), key=lambda x: x[1]["created"], reverse=True):
    active = "active" if cid == st.session_state.current_id else ""
    t = conv["title"].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    conv_items_html += f'<div class="conv-item {active}" onclick="selectConv(\'{cid}\')">{t}</div>\n'

st.markdown(f"""
<div class="topbar">
  <div class="topbar-left">
    <button class="menu-btn" onclick="toggleDrawer()" title="Menu (Ctrl+B)">☰</button>
    <span class="topbar-title">✦ ALUETOO AI</span>
  </div>
  <div>
    <div class="status-badge">
      <div class="status-dot-green"></div>
      <span>En ligne &nbsp;·&nbsp; {paris_time}</span>
    </div>
  </div>
</div>

<div id="sidebar-overlay" onclick="closeDrawer()"></div>
<div id="sidebar-drawer">
  <div class="drawer-logo">✦ ALUETOO AI</div>
  <div class="drawer-sub">Créé par Léo Ciach</div>
  <button class="drawer-new-btn" onclick="triggerNewChat()">＋&nbsp; Nouvelle discussion</button>
  <input class="drawer-search" type="text" placeholder="🔍 Rechercher…" oninput="filterConvs(this.value)">
  <div class="drawer-divider"></div>
  <div id="conv-list">{conv_items_html}</div>
  <div class="drawer-footer">
    ALUETOO AI &nbsp;·&nbsp; Créé par Léo Ciach<br>
    <span style="opacity:0.5">v2.0 Pro · Powered by Groq</span>
  </div>
</div>

<script>
function toggleDrawer() {{
    document.getElementById('sidebar-drawer').classList.toggle('open');
    document.getElementById('sidebar-overlay').classList.toggle('open');
}}
function closeDrawer() {{
    document.getElementById('sidebar-drawer').classList.remove('open');
    document.getElementById('sidebar-overlay').classList.remove('open');
}}
function triggerNewChat() {{
    closeDrawer();
    // find hidden new-chat button and click
    const btns = window.parent.document.querySelectorAll('button');
    btns.forEach(b => {{ if(b.getAttribute('data-action')==='new-chat') b.click(); }});
}}
function selectConv(cid) {{
    closeDrawer();
    const inp = window.parent.document.querySelector('[data-conv-select="true"]');
    if(inp) {{ inp.value = cid; inp.dispatchEvent(new Event('input',{{bubbles:true}})); }}
}}
function filterConvs(q) {{
    document.querySelectorAll('.conv-item').forEach(el => {{
        el.style.display = el.textContent.toLowerCase().includes(q.toLowerCase()) ? '' : 'none';
    }});
}}
document.addEventListener('keydown', e => {{
    if((e.ctrlKey||e.metaKey) && e.key==='b') {{ e.preventDefault(); toggleDrawer(); }}
}});
</script>
""", unsafe_allow_html=True)

# ============================================================================
# CONTRÔLES CACHÉS
# ============================================================================
c1, c2 = st.columns([1, 20])
with c1:
    if st.button("＋", key="hidden_new_chat"):
        new_chat()
        st.rerun()

# ============================================================================
# MESSAGES
# ============================================================================
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

if not st.session_state.messages:
    # Construire les chips sans inline onclick pour eviter les conflits de guillemets
    sug_chips = "".join(
        f'<div class="sug-chip" data-idx="{i}">{s}</div>'
        for i, s in enumerate(SUGGESTIONS)
    )
    # Passer les textes via JSON dans une variable JS globale
    sug_json = json.dumps(SUGGESTIONS)
    hero_html = (
        '<div class="hero">' +
        '<div class="hero-title">ALUETOO AI</div>' +
        '<div class="hero-sub">Compute · Données · Algorithmes · Éthique</div>' +
        '<div class="hero-author">Créé par Léo Ciach</div>' +
        '<div class="suggestions">' + sug_chips + '</div>' +
        '</div>' +
        '<script>' +
        'var SUGS = ' + sug_json + ';' +
        'document.querySelectorAll(".sug-chip").forEach(function(c){' +
        '  c.addEventListener("click",function(){' +
        '    var t=SUGS[parseInt(this.getAttribute("data-idx"))];' +
        '    var ta=window.parent.document.querySelector('
        + repr('[data-testid="stChatInput"] textarea') +
        ');' +
        '    if(ta){var s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,"value").set;' +
        '    s.call(ta,t);ta.dispatchEvent(new Event("input",{bubbles:true}));ta.focus();}' +
        '  });' +
        '});' +
        '</script>'
    )
    st.markdown(hero_html, unsafe_allow_html=True)

for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-row-user"><div class="bubble-user">{msg["content"]}</div></div>',
            unsafe_allow_html=True
        )
        if msg.get("image"):
            c1, c2, c3 = st.columns([2, 3, 2])
            with c2:
                st.image(base64.b64decode(msg["image"]), use_container_width=True)
    else:
        st.markdown(
            f'<div class="msg-row-ai"><div class="bubble-ai">{msg["content"]}</div></div>',
            unsafe_allow_html=True
        )
        tc1, tc2, tc3, tc4, _ = st.columns([1, 1, 1, 1, 7])
        with tc1:
            if st.button("📋", key=f"copy_{idx}", help="Copier"):
                st.toast("✓ Copié !")
        with tc2:
            if st.button("🔊", key=f"tts_{idx}", help="Lire"):
                speak_text(msg["content"])
        with tc3:
            if st.button("🔄", key=f"regen_{idx}", help="Régénérer"):
                st.session_state.messages = st.session_state.messages[:idx]
                st.rerun()
        with tc4:
            if st.button("👍", key=f"like_{idx}", help="Bien"):
                st.toast("✓ Merci !")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# BARRE DE SAISIE FIXE
# ============================================================================

# On construit le HTML en concatenant des strings simples (pas de f-string)
# pour eviter tout conflit avec les accolades du CSS/JS

_bar = []
_bar.append('<div class="input-bar-wrapper">')
_bar.append('  <div class="input-bar-inner">')

if st.session_state.uploaded_b64:
    _bar.append('  <div class="img-preview-bar">')
    _bar.append('    <img src="data:image/jpeg;base64,' + st.session_state.uploaded_b64 + '" alt="preview">')
    _name = st.session_state.uploaded_name or ""
    _bar.append('    <span style="font-size:12px;color:rgba(255,255,255,0.35)">&#128206; ' + _name + '</span>')
    _bar.append('  </div>')

_bar.append('  <div class="bar-actions">')
_bar.append('    <div class="bar-left">')
_bar.append('      <button class="action-btn" id="mic-btn" onclick="toggleMic()">&#127908; Dicter</button>')
_bar.append('      <button class="action-btn" onclick="triggerFileUpload()">&#128206; Image</button>')
if st.session_state.generating:
    _bar.append('      <button class="stop-btn" onclick="clickStop()">&#9209; Arr&#234;ter</button>')
_bar.append('    </div>')
_bar.append('    <div class="bar-hint">&#8984;&#8629; envoyer &nbsp;&middot;&nbsp; Ctrl+B menu</div>')
_bar.append('  </div>')
_bar.append('  </div>')
_bar.append('</div>')
_bar.append("""<script>
var _recog=null,_isRec=false;
function toggleMic(){
  var btn=document.getElementById('mic-btn');
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){alert('Dictee non supportee, utilisez Chrome.');return;}
  if(_isRec){_recog&&_recog.stop();return;}
  _recog=new SR();_recog.lang=navigator.language||'fr-FR';
  _recog.continuous=false;_recog.interimResults=false;
  _recog.start();_isRec=true;
  btn.classList.add('recording');btn.textContent='Arreter';
  _recog.onresult=function(e){
    var t=e.results[0][0].transcript;
    var ta=window.parent.document.querySelector('[data-testid="stChatInput"] textarea');
    if(ta){
      var s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
      s.call(ta,(ta.value?ta.value+' ':'')+t);
      ta.dispatchEvent(new Event('input',{bubbles:true}));
    }
  };
  _recog.onerror=_recog.onend=function(){
    _isRec=false;btn.classList.remove('recording');btn.textContent='Dicter';
  };
}
function triggerFileUpload(){
  var inp=window.parent.document.querySelector('input[type="file"]');
  if(inp)inp.click();
}
function clickStop(){
  var btns=window.parent.document.querySelectorAll('button');
  for(var i=0;i<btns.length;i++){
    if(btns[i].innerText.trim()==='stop'){btns[i].click();break;}
  }
}
document.addEventListener('keydown',function(e){
  if((e.ctrlKey||e.metaKey)&&e.key==='m'){e.preventDefault();toggleMic();}
});
</script>""")

st.markdown("\n".join(_bar), unsafe_allow_html=True)

# Bouton stop caché
cs, _ = st.columns([1, 20])
with cs:
    if st.button("⏹", key="hidden_stop"):
        st.session_state.stop_gen = True
        st.rerun()

# Upload
uploaded_file = st.file_uploader("", type=["png","jpg","jpeg","gif","webp"], label_visibility="collapsed")
if uploaded_file:
    st.session_state.uploaded_b64 = base64.b64encode(uploaded_file.read()).decode()
    st.session_state.uploaded_name = uploaded_file.name
    st.rerun()

# Retirer image
if st.session_state.uploaded_b64:
    if st.button("✕ Retirer l'image", key="remove_img"):
        st.session_state.uploaded_b64 = None
        st.session_state.uploaded_name = None
        st.rerun()

# ============================================================================
# INPUT + GÉNÉRATION
# ============================================================================
if prompt := st.chat_input("Message à ALUETOO…"):
    user_msg = {"role": "user", "content": prompt}
    if st.session_state.uploaded_b64:
        user_msg["image"] = st.session_state.uploaded_b64

    st.session_state.messages.append(user_msg)
    save_current()

    st.markdown(
        f'<div class="msg-row-user"><div class="bubble-user">{prompt}</div></div>',
        unsafe_allow_html=True
    )
    if user_msg.get("image"):
        c1, c2, c3 = st.columns([2, 3, 2])
        with c2:
            st.image(base64.b64decode(user_msg["image"]), use_container_width=True)

    status_ph = st.empty()
    status_ph.markdown("""
    <div class="status-pill">
        <div class="thinking-dots"><span></span><span></span><span></span></div>
        ALUETOO réfléchit…
    </div>""", unsafe_allow_html=True)

    model = (
        "meta-llama/llama-4-scout-17b-16e-instruct"
        if user_msg.get("image") else "llama-3.3-70b-versatile"
    )

    st.session_state.generating = True
    st.session_state.stop_gen = False
    placeholder = st.empty()
    full = ""

    try:
        stream = client.chat.completions.create(
            model=model, messages=build_api_messages(),
            stream=True, temperature=0.7, max_tokens=2048
        )
        for chunk in stream:
            if st.session_state.stop_gen: break
            delta = chunk.choices[0].delta.content
            if delta:
                full += delta
                status_ph.markdown("""
                <div class="status-pill">
                    <div class="thinking-dots"><span></span><span></span><span></span></div>
                    Génération…
                </div>""", unsafe_allow_html=True)
                placeholder.markdown(
                    f'<div class="msg-row-ai"><div class="bubble-ai">{full}<span style="opacity:0.3">▌</span></div></div>',
                    unsafe_allow_html=True
                )

        placeholder.markdown(
            f'<div class="msg-row-ai"><div class="bubble-ai">{full}</div></div>',
            unsafe_allow_html=True
        )
        status_ph.empty()
        st.session_state.messages.append({"role": "assistant", "content": full})
        save_current()

        if st.session_state.auto_speak and full:
            speak_text(full)

    except Exception as e:
        status_ph.empty()
        st.error(f"Erreur API : {e}")
    finally:
        st.session_state.generating = False
        st.session_state.uploaded_b64 = None
        st.session_state.uploaded_name = None
        st.rerun()

