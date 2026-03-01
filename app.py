import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from datetime import datetime
import pytz

# --- CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def obtenir_heure_belge():
    try:
        tz = pytz.timezone('Europe/Brussels')
        return datetime.now(tz).strftime("%A %d %B %Y, %H:%M")
    except:
        return "Heure non disponible"

def chercher_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "Aucun résultat trouvé sur le web."
            return "\n".join([f"SOURCE: {r['body']}" for r in results])
    except Exception as e:
        return f"Erreur de recherche : {str(e)}"

# --- INTERFACE ---
st.set_page_config(page_title="ALUETOO AI", page_icon="🤖")
st.title("🤖 ALUETOO AI")

heure = obtenir_heure_belge()
st.sidebar.write(f"📅 Date : {heure}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT ---
if prompt := st.chat_input("Demande-moi n'importe quoi sur l'actu..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # 1. On cherche
        with st.spinner("Je regarde sur Internet..."):
            infos_du_web = chercher_web(prompt)
        
        # 2. On prépare l'instruction (très autoritaire)
        system_prompt = (
            f"Tu es ALUETOO AI. Nous sommes le {heure}. "
            "Tes connaissances internes s'arrêtent en 2023, MAIS je te donne accès au Web ci-dessous. "
            "TU DOIS IGNORER TA LIMITE DE 2023. "
            "Si les infos ci-dessous parlent de 2025 ou 2026, utilise-les ! "
            f"\n\nVOICI LES INFOS RÉELLES DU WEB :\n{infos_du_web}"
        )

        # 3. Appel API
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            temperature=0
        )
        
        reponse = completion.choices[0].message.content
        st.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})

        # --- DEBUG : Affiche ce que l'IA a trouvé (pour toi vérifier) ---
        with st.expander("Voir les sources brutes trouvées"):
            st.write(infos_du_web)
