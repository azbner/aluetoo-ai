import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
import pytz
from datetime import datetime

# --- CONFIGURATION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def chercher_web(query):
    try:
        with DDGS() as ddgs:
            # On simplifie la recherche au maximum
            results = list(ddgs.text(query, max_results=3))
            if not results:
                return "AUCUN RÉSULTAT TROUVÉ SUR LE WEB."
            return "\n".join([f"- {r['body']}" for r in results])
    except Exception as e:
        return f"ERREUR TECHNIQUE RECHERCHE : {str(e)}"

st.title("🤖 ALUETOO AI - DEBUG MODE")

# --- TEST DE RECHERCHE IMMÉDIAT ---
question = st.text_input("Pose ta question ici :")

if question:
    # 1. On force l'affichage de la recherche pour voir si ça marche
    st.subheader("🌐 Ce que l'IA trouve sur Internet :")
    resultats_bruts = chercher_web(question)
    st.info(resultats_bruts) # Ça va afficher un bloc bleu avec les infos

    # 2. On demande à l'IA de répondre
    st.subheader("💬 Réponse de l'IA :")
    
    tz = pytz.timezone('Europe/Brussels')
    heure = datetime.now(tz).strftime("%H:%M")
    
    prompt_systeme = f"Tu es ALUETOO AI. Il est {heure}. Utilise ces infos : {resultats_bruts}"
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt_systeme},
            {"role": "user", "content": question}
        ]
    )
    
    st.write(completion.choices[0].message.content)
