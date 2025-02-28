import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

# 🚀 Configuration de l'application
title = "AstraMed - Votre Assistant IA Médical"
primary_color = "#1A237E"  # Bleu marine
secondary_color = "#90CAF9"  # Bleu ciel
HOST = "http://127.0.0.1:8181"  # API locale

# Fonction pour charger une animation Lottie
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# 🏥 Animation d'accueil
lottie_medical = load_lottie_url("")

# 🎨 CSS Personnalisé
st.markdown(f"""
    <style>
    .stSidebar {{background-color: {secondary_color};}}
    .stButton > button {{
        background-color: {primary_color};
        color: white;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        background-color: #283593;
    }}
    .chat-message {{
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0px;
    }}
    .chat-message.user {{background-color: #E3F2FD;}}
    .chat-message.bot {{background-color: #F3E5F5;}}
    .big-font {{font-size: 2.5rem !important; color: {primary_color};}}
    </style>
    """, unsafe_allow_html=True)

# 📌 Initialisation de la navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'

if st.session_state.page == 'home':
    st.markdown(f"<h1 class='big-font' style='text-align:center;'>{title}</h1>", unsafe_allow_html=True)
    if lottie_medical:
        st_lottie(lottie_medical, height=350)
   
    st.markdown("### 🌟 Fonctionnalités")
    st.write("✅ Réponses médicales basées sur l'IA")
    st.write("✅ Recherche d'informations fiables avec source")
    st.write("✅ Traduction automatique FR ↔ EN")
    st.write("✅ Gestion de l'historique de conversation")

    if st.button("🩺 Commencer la consultation"):
        st.session_state.page = 'chat'
        st.rerun()

elif st.session_state.page == 'chat':
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = 'home'
        st.rerun()
   
    st.title("💬 AstraMed - Chatbot Médical IA")
   
    with st.sidebar:
        st.markdown("### ⚙️ Paramètres")
        temperature = st.slider("Créativité des réponses", 0.0, 1.0, 0.3, 0.1)
        similarity_threshold = st.slider("Seuil de similarité RAG", 0.0, 1.0, 0.50, 0.05)
        language = st.selectbox("Langue", ["Francais", "English", "Arabic"])
   
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider aujourd’hui ?"}]
   
    for message in st.session_state.messages:
        avatar = "🏥" if message["role"] == "assistant" else "👤"
        st.chat_message(message["role"], avatar=avatar).write(message["content"])
   
    if question := st.chat_input("Posez votre question ici..."):
        st.session_state["messages"].append({"role": "user", "content": question})
        st.chat_message("user", avatar="👤").write(question)
       
        with st.spinner("🏥 Recherche des sources les plus pertinentes..."):
            response = requests.post(
                f"{HOST}/answer",
                json={
                    "question": question,
                    "temperature": temperature,
                    "similarity_threshold": similarity_threshold,
                    "language": language,
                    "session_id": "test-session"
                },
                timeout=30
            )
           
            if response.status_code == 200:
                response_data = response.json()
                similar_answers = response_data.get("answers", [])[:3]  # Prendre les 3 meilleures réponses
                generated_response = response_data.get("generated_response", "Erreur lors de la reformulation.")

                if not similar_answers:
                    st.error("❌ Aucune source pertinente trouvée.")
                else:
                    st.markdown("### 📚 **Sources les plus pertinentes :**")
                    for i, answer_data in enumerate(similar_answers):
                        source = answer_data.get("metadata", {}).get("source", "Inconnue")
                        similarity_score = answer_data.get("metadata", {}).get("similarity_score", "N/A")
                        st.write(f"🏥 **Source {i+1}:** {source} (Similarité: {similarity_score})")

                    # 📌 **Affichage des réponses des 3 sources**
                    st.markdown("### 📄 **Réponses des 3 sources sélectionnées :**")
                    for i, answer_data in enumerate(similar_answers):
                        st.write(f"🔹 **Réponse {i+1} :** {answer_data.get('message', 'Réponse non disponible.')}")

                    # 📌 **Affichage de la réponse générée à partir des sources**
                    st.markdown("### 🤖 **Réponse Générée :**")
                    st.chat_message("assistant", avatar="🏥").write(generated_response)
                    # 📌 Ajout du feedback utilisateur après la réponse générée
                    st.markdown("### 📝 **Votre avis compte !**")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Bonne réponse"):
                            feedback_data = {
                                "session_id": "test-session",
                                "question": question,
                                "rating": 1,
                                "comments": ""
                                }
                            response = requests.post(f"{HOST}/feedback", json=feedback_data)
                            if response.status_code == 200:
                                st.success("✅ Merci pour votre feedback !")

                    with col2:
                        if st.button("👎 Mauvaise réponse"):
                            comments = st.text_input("Pourquoi la réponse n'est pas satisfaisante ? (optionnel)")
                            if st.button("📤 Envoyer Feedback"):
                                feedback_data = {
                                    "session_id": "test-session",
                                    "question": question,
                                    "rating": 0,
                                    "comments": comments
                                }
                                response = requests.post(f"{HOST}/feedback", json=feedback_data)
                                if response.status_code == 200:
                                    st.success("✅ Feedback enregistré, merci !")


            else:
                st.error(f"❌ Erreur : {response.status_code} - {response.text}")



