import streamlit as st
from groq import Groq
from datetime import datetime
import pytz

# --- CONNEXION ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- HEURE ---
tz = pytz.timezone('Europe/Brussels')
maintenant = datetime.now(tz).strftime("%d/%m/%Y à %H:%M")

st.title("🤖 ALUETOO AI")
st.write(f"📍 Belgique | ⏰ {maintenant}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- CHAT ---
if prompt := st.chat_input("Pose ta question..."):
    st.chat_message("user").markdown(prompt)
    
    # On prépare un message système qui ne parle QUE de la date actuelle
    # pour forcer l'IA à se situer dans le présent.
    ctx = f"Tu es ALUETOO AI. Nous sommes le {maintenant}. Agis comme une IA de 2026."

    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile", 
        messages=[{"role": "system", "content": ctx}, {"role": "user", "content": prompt}],
        temperature=0.5
    )
    
    reponse = completion.choices[0].message.content
    with st.chat_message("assistant"):
        st.markdown(reponse)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": reponse})
