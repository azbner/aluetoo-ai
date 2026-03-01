import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import pytz
from datetime import datetime

# --- CONFIGURATION GROQ ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def chercher_web(sujet):
    try:
        with DDGS() as ddgs:
            # On cherche de l'actu très récente
            results = list(ddgs.text(f"{sujet} actualité 2025 2026", max_results=3))
            if not results:
                return "Pas d'infos trouvées sur le web pour ce sujet."
            return "\n".join([f"INFO: {r['body']}" for r in results])
    except Exception as e:
        return f"Erreur de connexion : {e}"

# --- INTERFACE ---
st.set_page_config(page_title="ALUETOO AI", page_icon="🌐")
st.title("🤖 ALUETOO AI")

# Heure Belge
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%d/%m/%Y à %H:%M")
st.sidebar.write(f"⏰ Belgique : {maintenant}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIQUE ---
if prompt := st.chat_input("Pose ta question..."):
    # On affiche le message de l'utilisateur
    st.chat_message("user").markdown(prompt)
    
    # Étape 1 : Recherche Web
    with st.spinner("🌍 Accès au Web en cours..."):
        infos_fraiches = chercher_web(prompt)
    
    # Étape 2 : Préparation d'un message système ULTRA-DOMINANT
    # On change de modèle pour le 8b qui obéit mieux aux ordres de 'current events'
    instruction_fatale = (
        f"Tu es ALUETOO AI. NOUS SOMMES LE {maintenant}. "
        "TES CONNAISSANCES NE SONT PAS LIMITÉES. TU AS UN ACCÈS INTERNET COMPLET. "
        f"VOICI LES DONNÉES RÉELLES DE 2025/2026 : \n{infos_fraiches}\n\n"
        "Réponds à l'utilisateur uniquement avec ces infos. Ne parle JAMAIS de 2023."
    )

    # Étape 3 : On envoie seulement le message actuel (pour éviter que l'IA se souvienne qu'elle a dit '2023' juste avant)
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", # Ce modèle est un "soldat", il obéit mieux
            messages=[
                {"role": "system", "content": instruction_forcee},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        reponse = completion.choices[0].message.content
        with st.chat_message("assistant"):
            st.markdown(reponse)
            # Petit debug pour toi
            with st.expander("Vérifier la connexion internet"):
                st.write(infos_fraiches)
    except Exception as e:
        st.error(f"Erreur Groq : {e}")
