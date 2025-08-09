import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot
import os

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

EMOJIS_POSICIONES = {
    "Portero": "🧤",
    "Defensa": "🛡️",
    "Centrocampista": "🎯",
    "Delantero": "⚡",
}

def enviar_mensaje(mensaje):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje, parse_mode="HTML")

async def obtener_plantilla(session, url):
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "html.parser")
        jugadores_html = soup.select("div.player-info")
        jugadores = []
        for jugador in jugadores_html:
            nombre_tag = jugador.select_one("p.name")
            posicion_tag = jugador.select_one("p.position")
            if nombre_tag and posicion_tag:
                nombre = nombre_tag.get_text(strip=True)
                posicion = posicion_tag.get_text(strip=True)
                emoji = EMOJIS_POSICIONES.get(posicion, "•")
                jugadores.append(f"{emoji} {nombre}")
        return jugadores

async def main_async():
    async with aiohttp.ClientSession() as session:
        cambios_detectados = []
        for url in URLS:
            plantilla = await obtener_plantilla(session, url)
            equipo = url.split("/")[4].replace("-", " ").title()
            cambios_detectados.append(f"<b>📋 {equipo}</b>\n" + "\n".join(plantilla) + "\n")

        mensaje_final = f"🔍 <b>Revisión completada</b> ({datetime.now().strftime('%d/%m/%Y %H:%M')})\n\n"
        mensaje_final += "\n".join(cambios_detectados)
        return mensaje_final

def main():
    mensaje_final = asyncio.run(main_async())
    enviar_mensaje(mensaje_final)

if __name__ == "__main__":
    main()
