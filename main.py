import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot
import asyncio

# URLs de todas las plantillas
URLS = [
    "https://www.laliga.com/clubes/athletic-club/plantilla",
    "https://www.laliga.com/clubes/atletico-de-madrid/plantilla",
    "https://www.laliga.com/clubes/c-a-osasuna/plantilla",
    "https://www.laliga.com/clubes/rc-celta/plantilla",
    "https://www.laliga.com/clubes/d-alaves/plantilla",
    "https://www.laliga.com/clubes/elche-c-f/plantilla",
    "https://www.laliga.com/clubes/fc-barcelona/plantilla",
    "https://www.laliga.com/clubes/getafe-cf/plantilla",
    "https://www.laliga.com/clubes/girona-fc/plantilla",
    "https://www.laliga.com/clubes/levante-ud/plantilla",
    "https://www.laliga.com/clubes/rayo-vallecano/plantilla",
    "https://www.laliga.com/clubes/rcd-espanyol/plantilla",
    "https://www.laliga.com/clubes/rcd-mallorca/plantilla",
    "https://www.laliga.com/clubes/real-betis/plantilla",
    "https://www.laliga.com/clubes/real-madrid/plantilla",
    "https://www.laliga.com/clubes/real-oviedo/plantilla",
    "https://www.laliga.com/clubes/real-sociedad/plantilla",
    "https://www.laliga.com/clubes/sevilla-fc/plantilla",
    "https://www.laliga.com/clubes/valencia-cf/plantilla",
    "https://www.laliga.com/clubes/villarreal-cf/plantilla"
]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DATA_FILE = "plantillas_actual.txt"

def obtener_plantilla(url):
    """Descarga y extrae los nombres de los jugadores de una plantilla."""
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        jugadores = []
        for jugador in soup.select("span.player-name"):  # Selector según la web
            nombre = jugador.get_text(strip=True)
            if nombre:
                jugadores.append(nombre)
        return jugadores
    except Exception as e:
        print(f"Error en {url}: {e}")
        return []

def obtener_todas_las_plantillas():
    data = {}
    for url in URLS:
        equipo = url.split("/clubes/")[1].split("/")[0]
        plantilla = obtener_plantilla(url)
        data[equipo] = plantilla
    return data

def guardar_datos(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        for equipo, jugadores in data.items():
            f.write(f"{equipo}:{','.join(jugadores)}\n")

def cargar_datos():
    if not os.path.exists(DATA_FILE):
        return {}
    data = {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        for linea in f:
            equipo, jugadores = linea.strip().split(":")
            data[equipo] = jugadores.split(",")
    return data

async def enviar_mensaje(texto):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

async def main():
    datos_previos = cargar_datos()
    datos_actuales = obtener_todas_las_plantillas()

    cambios = []
    for equipo, plantilla in datos_actuales.items():
        anterior = datos_previos.get(equipo, [])
        if plantilla != anterior:
            cambios.append(f"⚠️ {equipo} ha cambiado su plantilla.")

    guardar_datos(datos_actuales)

    if cambios:
        mensaje = f"🔍 Cambios detectados ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n" + "\n".join(cambios)
    else:
        mensaje = f"✅ Sin cambios en las plantillas ({datetime.now().strftime('%d/%m/%Y %H:%M')})"

    await enviar_mensaje(mensaje)

if __name__ == "__main__":
    asyncio.run(main())
