import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import pytz
from datetime import datetime

# --- 1. CONNEXION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Clé API manquante dans les Secrets.")
    st.stop()

# --- 2. FONCTION DE RECHERCHE ---
def obtenir_infos_du_web(sujet):
    try:
        with DDGS() as ddgs:
            # On cherche les actus les plus récentes
            recherche = list(ddgs.text(sujet, max_results=3))
            if recherche:
                texte_resultat = ""
                for r in recherche:
                    texte_resultat += f"\n- {r['body']}"
                return texte_resultat
            return "Aucune info trouvée sur le web."
    except Exception as e:
        return f"Erreur de connexion internet : {str(e)}"

# --- 3. INTERFACE ---
st.set_page_config(page_title="ALUETOO AI", page_icon="🌐")
st.title("🤖 ALUETOO AI")

# Heure Belge
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz)
date_texte = maintenant.strftime("%d/%m/%Y à %H:%M")

st.sidebar.write(f"📍 Belgique")
st.sidebar.write(f"📅 {date_texte}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage du chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- 4. LOGIQUE ---
if prompt := st.chat_input("Demande-moi l'actu de Dubaï..."):
    # Afficher le message utilisateur
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # ÉTAPE INTERNET : On va chercher les infos
        with st.spinner("Recherche sur Internet en cours..."):
            infos_web = obtenir_infos_du_web(prompt)
        
        # On montre ce qu'on a trouvé (Mode Debug)
        with st.expander("🌐 Sources trouvées sur le Web"):
            st.write(infos_web)

        # INSTRUCTION À L'IA
        contexte_final = (
            f"Tu es ALUETOO AI. Nous sommes le {date_texte}. "
            "IMPORTANT : Ne dis JAMAIS que tu es limité à 2023. "
            f"Voici les informations que je viens de trouver sur Internet pour toi :\n{infos_web}\n\n"
            "Utilise ces informations pour répondre à l'utilisateur."
        )

        # APPEL GROQ
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": contexte_final}] + st.session_state.messages,
            temperature=0.1
        )
        
        reponse = completion.choices[0].message.content
        st.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
