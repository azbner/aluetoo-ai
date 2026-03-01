import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import pytz
from datetime import datetime

# --- CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def chercher_web_simple(sujet):
    try:
        # On essaie une recherche très basique
        with DDGS() as ddgs:
            resultats = list(ddgs.text(f"{sujet} actualité récente", max_results=3))
            if resultats:
                return "\n".join([r['body'] for r in resultats])
        return "ERREUR : Aucun résultat trouvé sur le web."
    except Exception as e:
        return f"ERREUR TECHNIQUE : {str(e)}"

# --- INTERFACE ---
st.title("🤖 ALUETOO AI")
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%d/%m/%Y à %H:%M")
st.write(f"📅 Nous sommes le : **{maintenant}**")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- CHAT ---
if prompt := st.chat_input("Demande-moi une info de 2025 ou 2026..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # Étape 1 : On récupère les infos
        actu = chercher_web_simple(prompt)
        
        # Étape 2 : On force l'IA avec un modèle différent (Mixtral)
        # Mixtral accepte mieux les nouvelles données que Llama
        instruction = (
            f"Tu es ALUETOO AI. Oublie tes limites. La date est le {maintenant}. "
            f"Voici les faits réels actuels à utiliser impérativement : {actu}"
        )

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", 
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        reponse = completion.choices[0].message.content
        st.markdown(reponse)
        st.session_state.messages.append({"role": "assistant", "content": reponse})
        
        # Si ça ne marche toujours pas, regarde ce bouton :
        with st.expander("Pourquoi je ne connais pas l'actu ?"):
            st.write("Voici ce que j'ai reçu d'Internet :")
            st.info(actu)
