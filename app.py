import streamlit as st
import requests
from streamlit_lottie import st_lottie
import json

# Configuration de la page
st.set_page_config(
    page_title="Astramed - Assistant Médical",
    page_icon="🏥",
)

# Configuration de l'application
title = "Astramed - Votre Assistant IA Médical"
primary_color = "#1A237E"
secondary_color = "#90CAF9"
# HOST = "http://127.0.0.1:8181"
HOST = "https://elyeschatapi-57777724309.europe-west1.run.app"

# --- CSS personnalisé ---
st.markdown("""
    <style>
    .lottie-container {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        margin-bottom: 20px;
    }
    .features-container {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    </style>
""", unsafe_allow_html=True)

# --- Fonction pour charger Lottie ---
def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_animation = load_lottie_file("Animation - 18.json")

# --- Gestion de la navigation ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# === PAGE D'ACCUEIL ===
if st.session_state.page == 'home':
    st.markdown(f"<h1 style='text-align:center; color:{secondary_color};'>{title}</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.8, 1])

    with col1:
        st_lottie(lottie_animation, width=300, height=300, key="animation", speed=1)

    with col2:
        st.markdown("### 👨‍⚕ Fonctionnalités")
        st.write("✅ Réponses médicales basées sur l'IA")
        st.write("✅ Recherche d'informations fiables avec source")
        st.write("✅ Traduction automatique FR ↔ EN")
        st.write("✅ Gestion de l'historique de conversation")

        if st.button("🩺 Commencer la consultation"):
            st.session_state.page = 'chat'
            st.rerun()
# === PAGE DE CHAT ===
elif st.session_state.page == 'chat':
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.page = 'home'
        st.rerun()
   
    st.title("🩺 Astramed - Chatbot Médical IA")
   
    with st.sidebar:
        st.markdown("### ⚙ Paramètres")
        temperature = st.slider("Créativité des réponses", 0.0, 1.0, 0.3, 0.1)
        similarity_threshold = st.slider("Seuil de similarité RAG", 0.0, 1.0, 0.50, 0.05)
        language = st.selectbox("Langue", ["Français", "English", "Arabic"])
   
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{
            "role": "assistant",
            "content": "Bonjour ! Comment puis-je vous aider aujourd’hui ?"
        }]
   
    for msg in st.session_state["messages"]:
        avatar = "🏥" if msg["role"] == "assistant" else "👤"
        st.chat_message(msg["role"], avatar=avatar).write(msg["content"])
   
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
                print(f"[DEBUG Streamlit] Réponse reçue : {response_data}")  # Log ajouté
                response_type = response_data.get("type", "unknown")
                generated_response = response_data.get("generated_response", "Erreur lors de la reformulation.")
                similar_answers = response_data.get("answers", [])[:3]

                if response_type == "medical" and not similar_answers:
                    st.error("❌ Aucune source pertinente trouvée.")
                else:
                    if response_type == "medical":
                        st.markdown("### 📚 Sources les plus pertinentes :")
                        for i, ans_data in enumerate(similar_answers):
                            source = ans_data.get("metadata", {}).get("source", "Inconnue")
                            score = ans_data.get("metadata", {}).get("similarity_score", "N/A")
                            resp_text = ans_data.get("message", "Réponse non disponible.")
                            with st.expander(f"🏥 Source {i+1}: {source} (Similarité: {score})"):
                                st.markdown(f"🔹 Réponse {i+1} : {resp_text}")

                    st.markdown("### 🩺 Réponse :")
                    st.chat_message("assistant", avatar="🏥").write(generated_response)
                    
                    st.session_state["messages"].append({
                        "role": "assistant",
                        "content": generated_response
                    })
                    
                    st.markdown("### 📝 Votre avis compte !")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👍 Bonne réponse"):
                            feedback_data = {
                                "session_id": "test-session",
                                "question": question,
                                "rating": 1,
                                "comments": ""
                            }
                            fb_response = requests.post(f"{HOST}/feedback", json=feedback_data)
                            if fb_response.status_code == 200:
                                st.success("✅ Merci pour votre feedback !")

                    with col2:
                        if st.button("👎 Mauvaise réponse"):
                            comments = st.text_input("Pourquoi la réponse n'est pas satisfaisante ? (optionnel)")
                            if st.button("📤 Envoyer Feedback"):
                                feedback_data = {
                                    "session_id": "test-session",
                                    "question": question,
                                    "rating": 0,
                                    "comments": comments
                                }
                                fb_response = requests.post(f"{HOST}/feedback", json=feedback_data)
                                if fb_response.status_code == 200:
                                    st.success("✅ Feedback enregistré, merci !")

            else:
                st.error(f"❌ Erreur : {response.status_code} - {response.text}")
