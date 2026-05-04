import streamlit as st
import json
from groq import Groq
from datetime import datetime
import pytz
import base64
import re
import time

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================
st.set_page_config(page_title="ALUETOO AI Pro", page_icon="✨", layout="wide", initial_sidebar_state="expanded")

# Injection CSS (Style Apple Dark Mode)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600;700&display=swap');
* { font-family: -apple-system, 'SF Pro Display', sans-serif; }
.stApp { background: #000; color: #f5f5f7; }
[data-testid="stHeader"], [data-testid="stFooter"] { display: none; }

.title {
    font-size: 42px; font-weight: 700; text-align: center; margin: 10px 0;
    background: linear-gradient(90deg, #ff3b30, #af52de, #0a84ff, #30d158, #ff3b30);
    background-size: 200%; animation: grad 6s linear infinite;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
@keyframes grad { 0%{background-position:0%} 100%{background-position:200%} }

.msg-user {
    background: linear-gradient(135deg, #0a84ff, #5e5ce6);
    color: white; padding: 12px 16px; border-radius: 18px 18px 4px 18px;
    max-width: 80%; margin-left: auto; margin-bottom: 12px; font-size: 15px;
}
.msg-ai {
    background: #1c1c1e; border: 0.5px solid #2c2c2e; color: #f5f5f7;
    padding: 12px 16px; border-radius: 18px 18px 18px 4px;
    max-width: 80%; margin-right: auto; margin-bottom: 12px; font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALISATION
# ============================================================================
if "GROQ_API_KEY" not in st.secrets:
    st.error("Clé API Groq manquante dans les secrets.")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "conversations" not in st.session_state: st.session_state.conversations = {}
if "current_id" not in st.session_state: st.session_state.current_id = None
if "messages" not in st.session_state: st.session_state.messages = []
if "uploaded_file" not in st.session_state: st.session_state.uploaded_file = None

def new_chat():
    cid = f"chat_{int(time.time())}"
    st.session_state.conversations[cid] = {"title": "Nouvelle discussion", "messages": [], "created": datetime.now()}
    st.session_state.current_id = cid
    st.session_state.messages = []

if not st.session_state.current_id:
    new_chat()

# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.title("✨ ALUETOO Pro")
    if st.button("➕ Nouveau chat", use_container_width=True):
        new_chat()
        st.rerun()
    
    st.divider()
    for cid, conv in sorted(st.session_state.conversations.items(), reverse=True):
        active = " (Actuel)" if cid == st.session_state.current_id else ""
        if st.button(f"{conv['title']}{active}", key=cid, use_container_width=True):
            st.session_state.current_id = cid
            st.session_state.messages = conv["messages"]
            st.rerun()

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================
st.markdown('<div class="title">ALUETOO AI</div>', unsafe_allow_html=True)

# Affichage des messages
for msg in st.session_state.messages:
    role_class = "msg-user" if msg["role"] == "user" else "msg-ai"
    st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

# Zone d'input
if prompt := st.chat_input("Posez votre question..."):
    # 1. Ajouter le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="msg-user">{prompt}</div>', unsafe_allow_html=True)

    # 2. Préparation de la réponse IA
    with st.chat_message("assistant", avatar=None):
        placeholder = st.empty()
        full_response = ""
        
        try:
            # Note: Utilisation d'un modèle valide (Llama 3.3 70B)
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Tu es ALUETOO AI, un assistant premium et concis."},
                    *st.session_state.messages
                ],
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(f'<div class="msg-ai">{full_response}▌</div>', unsafe_allow_html=True)
            
            placeholder.markdown(f'<div class="msg-ai">{full_response}</div>', unsafe_allow_html=True)
            
            # 3. Sauvegarde
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.session_state.conversations[st.session_state.current_id]["messages"] = st.session_state.messages
            
            # Mise à jour du titre si c'est le premier message
            if len(st.session_state.messages) <= 2:
                st.session_state.conversations[st.session_state.current_id]["title"] = prompt[:30] + "..."
                st.rerun()

        except Exception as e:
            st.error(f"Erreur Groq : {e}")
