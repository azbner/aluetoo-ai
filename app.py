import streamlit as st
from groq import Groq
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. DESIGN PERSONNALISÉ (CSS) ---
st.markdown("""
    <style>
    /* Animation de fondu pour les messages */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Style des bulles de chat arrondies */
    .stChatMessage {
        border-radius: 25px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
        animation: fadeIn 0.5s ease-out;
    }

    /* Arrondir l'input de texte */
    .stChatInputContainer textarea {
        border-radius: 20px !important;
    }

    /* Style pour le titre et le texte */
    h1 {
        color: #FF4B4B;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIQUE TEMPORELLE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%A %d %B %Y à %H:%M")

st.title("🤖 ALUETOO AI")
st.sidebar.markdown(f"### 📍 Infos\n**Lieu:** Belgique\n**Heure:** {maintenant}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage des messages avec animation
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 4. CHAT ET RÉPONSE ---
if prompt := st.chat_input("Écris ton message ici..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Contexte forcé
    ctx = f"Tu es ALUETOO AI. Date : {maintenant}. Ne mentionne JAMAIS 2023. Tu es en 2026."

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "system", "content": ctx}, {"role": "user", "content": prompt}],
        temperature=0.7
    )
    
    reponse = completion.choices[0].message.content
    # Nettoyage automatique du texte
    reponse = reponse.replace("décembre 2023", "2026").replace("2023", "2026")

    with st.chat_message("assistant"):
        st.markdown(reponse)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": reponse})
