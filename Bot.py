import discord
from discord.ext import commands
from google.cloud import dialogflow_v2 as dialogflow
import os
import uuid
from dotenv import load_dotenv
import logging
from keep_alive import keep_alive
# Garder le bot en vie

logging.basicConfig(level=logging.INFO)
logging.info("Bot démarré avec succès.")

# Charger les variables d'environnement
load_dotenv()

# Récupérer le token depuis les variables d'environnement
token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    print("Erreur : DISCORD_BOT_TOKEN non défini dans le fichier .env")
    exit()

# Charger les identifiants Dialogflow
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "dialogflow_key.json"
DIALOGFLOW_PROJECT_ID = "slimeru-daub"
LANGUAGE_CODE = "fr"

# Discord setup
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Fonction de requête Dialogflow
def detect_intent_texts(project_id, session_id, text, language_code):
    try:
        session_client = dialogflow.SessionsClient()
        session = session_client.session_path(project_id, session_id)

        text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)

        response = session_client.detect_intent(request={"session": session, "query_input": query_input})
        return response.query_result.fulfillment_text
    except Exception as e:
        print(f"Erreur lors de la requête Dialogflow : {e}")
        return None

@bot.event
async def on_ready():
    print(f'Bot connecté en tant que {bot.user}')

CHANNEL_IDS = [
    759668011371462702, 
    1275561641588691016,
    # Ajoutez d'autres IDs de canaux ici, par exemple:
]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Vérifie si le message est dans un des canaux autorisés
    if CHANNEL_IDS and message.channel.id not in CHANNEL_IDS:
        return

    try:
        # Traite le message avec Dialogflow
        session_id = str(uuid.uuid4())  # Génère un ID de session unique
        response = detect_intent_texts(DIALOGFLOW_PROJECT_ID, session_id, message.content, LANGUAGE_CODE)
        if response:
            await message.channel.send(response)
    except Exception as e:
        print(f"Erreur lors du traitement du message : {e}")

# Lancer le bot
keep_alive()
bot.run(token)