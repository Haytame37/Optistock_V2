import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class OptiBot:
    """
    Classe utilitaire pour gérer les interactions avec Google Gemini.
    Adaptative selon le rôle de l'utilisateur.
    """
    def __init__(self, role="public"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "VOTRE_CLE_ICI":
            self.model = None
            return
            
        genai.configure(api_key=api_key)
        
        # Configuration du modèle
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 1024,
        }
        
        # Définition de la personnalité selon le rôle
        if role == "owner":
            system_instruction = (
                "Tu es OptiBot, l'assistant exclusif des Propriétaires d'entrepôts sur OptiStock. "
                "Tu dois les conseiller sur la gestion de leurs entrepôts, la tarification, "
                "l'interprétation des données IoT de leurs capteurs, et l'acceptation des chercheurs. "
                "Ton ton est professionnel, direct et orienté rentabilité et gestion."
            )
        elif role == "researcher":
            system_instruction = (
                "Tu es OptiBot, l'assistant scientifique des Chercheurs sur OptiStock. "
                "Tu dois les aider à analyser des conditions de stockage et trouver des entrepôts, "
                "MAIS ATTENTION: Tu ne peux travailler QUE sur les produits officiellement supportés par OptiStock "
                "(qui te seront fournis dans le contexte). Si l'utilisateur mentionne un produit non supporté "
                "(comme la 'pomme de terre' ou autre), tu DOIS IMPÉRATIVEMENT répondre EXACTEMENT par : "
                "\"Pour ce produit, on ne peut pas te trouver un entrepôt idéal côté environnement.\" "
                "N'invente jamais de paramètres pour les produits non supportés. "
                "Ton ton est analytique, scientifique et précis."
            )
        elif role == "admin":
            system_instruction = (
                "Tu es OptiBot, l'assistant de l'Administrateur système OptiStock. "
                "Tu fournis des résumés sur l'état du système, la gestion des utilisateurs, "
                "et les logs de sécurité. Ton ton est technique et concis."
            )
        else: # public
            system_instruction = (
                "Tu es OptiBot, le guide d'accueil public du site OptiStock Solutions. "
                "Ton rôle est d'accueillir les visiteurs, d'expliquer les services (location d'entrepôts intelligents avec IoT), "
                "et de les encourager à s'inscrire comme Propriétaire ou Chercheur. "
                "Ne donne aucune donnée confidentielle. Sois chaleureux, commercial et très accueillant."
            )
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config,
            system_instruction=system_instruction
        )

    def get_response(self, user_input, app_history=None, context_data=""):
        """
        Envoie un message à Gemini en tenant compte de l'historique complet de la conversation
        et de données de contexte invisibles.
        """
        if not self.model:
            return "Désolé, ma clé API n'est pas encore configurée. Veuillez ajouter votre GEMINI_API_KEY dans le fichier .env."
        
        try:
            # 1. Formatage de l'historique pour Gemini
            gemini_history = []
            if app_history:
                for msg in app_history:
                    # Gemini utilise 'user' et 'model' (Streamlit utilise 'assistant')
                    msg_role = "model" if msg["role"] == "assistant" else "user"
                    gemini_history.append({"role": msg_role, "parts": [msg["content"]]})
            
            # 2. Démarrage de la session avec la mémoire
            self.chat_session = self.model.start_chat(history=gemini_history)
            
            # 3. Préparation du prompt final avec le contexte (invisible pour l'utilisateur)
            final_prompt = user_input
            if context_data:
                final_prompt = f"{context_data}\n\nQUESTION DE L'UTILISATEUR : {user_input}"
            
            # 4. Envoi du nouveau message
            response = self.chat_session.send_message(final_prompt)
            return response.text
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and "quota" in error_str.lower():
                return "⏳ Le quota gratuit de l'API Google Gemini a été temporairement atteint (trop de messages envoyés d'un coup). Veuillez patienter une minute avant de poser votre prochaine question !"
            return f"Une erreur est survenue lors de la communication avec l'IA : {error_str}"
