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
    # Le switch pour activer/désactiver le fondu
    active_fondu = st.toggle("Activer l'effet de fondu lent", value=True)
    st.info("Désactivez pour une écriture instantanée si besoin.")

# --- 3. STYLE CSS (STABILITÉ ET PILULE) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b0e14; }}

    /* Animation Ghost stable */
    @keyframes ghostFade {{
        0% {{ opacity: 0; filter: blur(6px); transform: scale(1.05); }}
        100% {{ opacity: 1; filter: blur(0px); transform: scale(1); }}
    }}

    /* Taille de police fixée à 20px pour éviter le changement de taille */
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

    /* HEADER DÉGRADÉ */
    .header-container {{ text-align: center; margin-bottom: 35px; }}
    .main-title {{ font-size: 48px; font-weight: 800; color: white; }}
    .full-gradient {{
        font-weight: bold;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 24px;
        display: block;
    }}

    /* BARRE PILULE FORCÉE */
    div[data-testid="stChatInput"] {{
        border-radius: 50px !important; 
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
        padding: 8px !important;
    }}
    div[data-testid="stChatInput"] textarea {{
        border-radius: 50px !important;
        padding-left: 20px !important;
        font-size: 18px !important;
    }}

    .stChatMessage {{ border-radius: 30px !important; border: 1px solid #1f2328; }}
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
        # On applique la taille 20px même aux anciens messages
        st.markdown(f'<div class="chat-text">{m["content"]}</div>', unsafe_allow_html=True)

# --- 7. RÉPONSE AVEC OPTION FONDU ---
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
                    # Effet Ghost activé
                    display_html += f'<span class="word-fade">{text}</span>'
                    placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                    time.sleep(0.06)
                else:
                    # Écriture normale sans fondu
                    placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)
        
        # Affichage final (on force la div chat-text pour garder la taille)
        placeholder.markdown(f'<div class="chat-text">{full_response}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
