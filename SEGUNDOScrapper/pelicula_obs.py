import os
import requests
import tweepy
from instabot import Bot
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
from io import BytesIO
import json
import socket
import vlc

# Cargar configuración
config = {}
if os.path.exists('config.json'):
    with open('config.json', 'r') as f:
        config = json.load(f)

# Autenticación en Twitter
auth = tweepy.OAuthHandler(config['TWITTER_CONSUMER_KEY'], config['TWITTER_CONSUMER_SECRET'])
auth.set_access_token(config['ACCESS_TOKEN'], config['ACCESS_TOKEN_SECRET'])
twitter_api = tweepy.API(auth)

# Autenticación en Instagram
bot = Bot()
bot.login(username=config['INSTAGRAM_USERNAME'], password=config['INSTAGRAM_PASSWORD'])

# Webhook de Discord
DISCORD_WEBHOOK_URL = config['DISCORD_WEBHOOK_URL']

# Carpeta donde se guardarán los archivos de salida para OBS
OUTPUT_DIR = 'salida_obs'

# Crear el directorio si no existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def obtener_datos_pelicula_o_serie(titulo):
    """Obtiene los datos de la película o serie desde la API de OMDb."""
    url = f"http://www.omdbapi.com/?t={titulo}&apikey={config['OMDB_API_KEY']}"
    response = requests.get(url)
    
    if response.status_code == 200:
        datos = response.json()
        if datos['Response'] == 'True':
            return datos
        else:
            print("Película o serie no encontrada.")
            return None
    else:
        print("Error al conectar con OMDb.")
        return None

# Resto de funciones aquí (guardar_texto, descargar_imagen, publicar_en_discord, etc.)

class MovieEventHandler(FileSystemEventHandler):
    """Clase para manejar eventos de archivos (cambios en VLC)."""
    
    def on_modified(self, event):
        """Acción cuando un archivo se modifica."""
        nombre_contenido = detectar_cambio_vlc()
        if nombre_contenido:
            print(f"Archivo detectado: {nombre_contenido}")
            procesar_contenido(nombre_contenido)

def iniciar_monitoreo():
    """Inicia el monitoreo de VLC."""
    observer = Observer()
    event_handler = MovieEventHandler()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    print("Monitoreo iniciado...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# Ejecutar el monitoreo
if __name__ == "__main__":
    iniciar_monitoreo()
