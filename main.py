import requests
import json
from datetime import datetime
from telegram import Bot
import os

# Configuración desde variables de entorno (GitHub Secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL = "https://api.laliga.com/api/v3/teams/133/players"  # Sevilla FC

JUGADORES_FILE = "jugadores.json"

def obtener_plantilla():
    """Descarga la plantilla actual del Sevilla FC desde la API de LaLiga"""
    resp = requests.get(URL)
    resp.raise_for_status()
    data = resp.json()
    jugadores = [jugador["shortName"] for jugador in data.get("players", [])]
    return sorted(jugadores)

def cargar_jugadores():
    """Carga la lista de jugadores desde el archivo local"""
    if os.path.exists(JUGADORES_FILE):
        with open(JUGADORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_jugadores(jugadores):
    """Guarda la lista de jugadores en el archivo local"""
    with open(JUGADORES_FILE, "w", encoding="utf-8") as f:
        json.dump(jugadores, f, ensure_ascii=False, indent=2)

def enviar_mensaje(texto):
    """Envía un mensaje a Telegram"""
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

def main():
    plantilla_actual = obtener_plantilla()
    plantilla_guardada = cargar_jugadores()

    if not plantilla_guardada:
        guardar_jugadores(plantilla_actual)
        enviar_mensaje("📋 Plantilla inicial guardada:\n" + "\n".join(plantilla_actual))
        return

    nuevos = [j for j in plantilla_actual if j not in plantilla_guardada]
    desaparecidos = [j for j in plantilla_guardada if j not in plantilla_actual]

    if nuevos or desaparecidos:
        mensaje = f"📢 Cambios detectados ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n"
        if nuevos:
            mensaje += "\n🆕 Nuevos jugadores:\n" + "\n".join(f"➕ {j}" for j in nuevos)
        if desaparecidos:
            mensaje += "\n❌ Jugadores que ya no están:\n" + "\n".join(f"➖ {j}" for j in desaparecidos)
        enviar_mensaje(mensaje)
        guardar_jugadores(plantilla_actual)
    else:
        enviar_mensaje(f"🔍 Revisión completada ({datetime.now().strftime('%d/%m/%Y %H:%M')})\nNo se han detectado cambios.")

if __name__ == "__main__":
    main()
