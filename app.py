import streamlit as st
from groq import Groq
import time
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. STYLE CSS (DÉGRADÉ GÉANT ET FONDU) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14;
    }

    /* Animation de fondu pour l'écriture */
    @keyframes ghostFade {
        from { opacity: 0; filter: blur(4px); transform: translateY(5px); }
        to { opacity: 1; filter: blur(0px); transform: translateY(0px); }
    }

    /* LE CHAT : DÉGRADÉ ARC-EN-CIEL CONTINU */
    .assistant-response {
        font-weight: bold;
        background: linear-gradient(to right, #ff4b4b, #af40ff, #00d4ff, #4bff80, #ff4b4b);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline;
        font-size: 18px;
    }

    .word-fade {
        display: inline;
        animation: ghostFade 0.8s ease-out forwards;
    }

    /* HEADER EN DÉGRADÉ */
    .header-container {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .main-title {
        font-size: 48px;
        font-weight: 800;
        color: white;
    }

    .full-gradient {
        font-weight: bold;
        background: linear-gradient(left, #ff4b4b, #af40ff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 26px;
        display: block;
        line-height: 1.4;
    }

    /* BARRE DE TEXTE PILULE */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 2px solid #30363d !important;
        background-color: #161b22 !important;
        padding: 8px !important;
    }

    div[data-testid="stChatInput"] textarea {
        border-radius: 50px !important;
        padding-left: 25px !important;
    }

    /* Bulles de chat */
    .stChatMessage {
        border-radius: 30px !important;
        border: 1px solid #1f2328;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE HORAIRE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
format_heure = maintenant.strftime("%H:%M")

if 5 <= maintenant.hour < 18:
    salutation = "Bonjour"
else:
    salutation = "Bonsoir"

# --- 4. HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">🤖 ALUETOO AI</div>
        <div class="full-gradient">
            {salutation} !<br>
            Intelligence 2026 (Mise à jour design le 1 mars) • {format_heure}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 5. GESTION DES MESSAGES ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            st.markdown(f'<div class="assistant-response">{m["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(m["content"])

# --- 6. RÉPONSE AVEC DÉGRADÉ ÉTENDU ---
if prompt := st.chat_input("Pose ta question..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        ctx = f"Tu es ALUETOO AI. Date : {format_heure}. Tu es en 2026."

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": ctx}] + st.session_state.messages,
            stream=True 
        )

        display_html = '<div class="assistant-response">'
        for chunk in completion:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                full_response += text
                # Chaque mot est enveloppé pour le fondu, mais le dégradé est sur le conteneur parent
                display_html += f'<span class="word-fade">{text}</span>'
                placeholder.markdown(display_html + '</div>', unsafe_allow_html=True)
                time.sleep(0.05)
        
        placeholder.markdown(f'<div class="assistant-response">{full_response}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
