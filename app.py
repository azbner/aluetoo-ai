import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. BARRE LATÉRALE (SWITCH) ---
with st.sidebar:
    st.title("⚙️ Réglages")
    active_fondu = st.toggle("Activer l'effet de fondu lent", value=True)
    st.divider()
    st.info("Design ALUETOO AI v2026")

# --- 3. STYLE CSS (CENTRAGE TOTAL ET PILULE) ---
st.markdown(f"""
    <style>
    /* Fond et suppression des marges inutiles */
    .stApp {{ background-color: #0b0e14; }}
    
    /* CENTRAGE DU CONTENU (Le secret est ici) */
    .main .block-container {{
        max-width: 700px !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin: auto !important;
    }}

    /* Animation Ghost stable */
    @keyframes ghostFade {{
        0% {{ opacity: 0; filter: blur(6px); }}
        100% {{ opacity: 1; filter: blur(0px); }}
    }}

    /* Texte du chat agrandi et stable */
    .chat-text {{
        font-size: 20px !important;
        line-height: 1.6;
        color: #e6edf3;
    }}

    .word-fade {{
        display: inline-block;
        animation: ghostFade 1.2s ease-out forwards;
        white-space: pre-wrap;
    }}

    /* HEADER CENTRÉ ET DÉGRADÉ */
    .header-container {{ 
        text-align: center; 
        width: 100%;
        margin-bottom: 40px; 
    }}
    .main-title {{ font-size: 48px; font-weight: 800; color: white; }}
    .full-gradient {{
        font-weight: bold;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 24px;
        display: block;
    }}

    /* BARRE PILULE CENTRÉE */
    div[data-testid="stChatInput"] {{
        border-radius: 50px !important; 
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
        padding: 8px !important;
        width: 100% !important;
    }}
    
    div[data-testid="stChatInput"] textarea {{
        border-radius: 50px !important;
        padding-left: 20px !important;
        font-size: 18px !important;
    }}

    /* Bulles de chat */
    .stChatMessage {{ 
        border-radius: 30px !important; 
        border: 1px solid #1f2328;
    }}

    header, footer {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")
salutation = "Bonjour" if 5 <= maintenant.hour < 18 else "Bonsoir"

# --- 5. HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="full-gradient">
            {salutation} !<br>
            Intelligence 2026 (Mise à jour design le 1 mars) • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 6. GESTION DES MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. RÉPONSE ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(f'<div class="chat-text">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        display_html = '<div class="chat-text">'
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Tu es ALUETOO AI."}] + st.session_state.messages,
            stream=True 
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                
                if active_fondu:
                    display_html += f'<span class="word-fade">{text}</span>'
                    placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                    time.sleep(0.06)
                else:
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
