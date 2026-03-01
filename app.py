import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION DE L'IA ---
# Remplace par ta clé API Groq (celle qui commence par gsk_...)
try:
    client = Groq(api_key="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")
except Exception as e:
    st.error(f"Erreur de configuration de la clé : {e}")

# --- 2. PARAMÈTRES PERSONNALISÉS ---
NOM_IA = "ALUETOO AI"
CREATEUR = "LEO CIACH"

st.set_page_config(page_title=NOM_IA, page_icon="🤖", layout="centered")

# Design stylé (Sombre et Vert)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stTextInput>div>div>input { color: white; }
    h1 { color: #00FFAA; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. INTERFACE DU SITE ---
st.title(f"🤖 {NOM_IA}")
st.write(f"### Bienvenue dans mon AI extremement rapide")
st.caption(f"Propulsé par ALUETOO_1.1 | Créé par **{CREATEUR}**")
st.divider()

# --- 4. GESTION DE LA MÉMOIRE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": f"Tu es {NOM_IA}, une IA surpuissante créée par {CREATEUR}. Tu es polie, serviable et tu réponds toujours en français."
        }
    ]

# Affichage de la discussion
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 5. ZONE DE CHAT (L'ACTION) ---
if prompt := st.chat_input("Message ALUETOO AI..."):
    # Ajouter le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse de l'IA (Correction du modèle ici)
    with st.chat_message("assistant"):
        with st.spinner("ALUETOO réfléchit..."):
            try:
                # Utilisation du modèle 3.3 qui fonctionne (70b-versatile)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages,
                )
                
                response = completion.choices[0].message.content
                st.markdown(response)
                
                # Sauvegarde la réponse dans l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Oups ! Une erreur est survenue : {e}")

# --- 6. BARRE LATÉRALE ---
with st.sidebar:
    st.header("Paramètres")
    if st.button("🗑️ Effacer la discussion"):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()
    st.info(f"Version : 2.0 (Stable)")
