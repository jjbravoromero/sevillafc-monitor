import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot
import os

# Lista de URLs de plantillas de todos los equipos de LaLiga
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

async def enviar_mensaje(mensaje):
    """Envia un mensaje a Telegram."""
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje)

async def obtener_plantilla(session, url):
    """Obtiene los nombres de jugadores de la plantilla desde la URL dada."""
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, "html.parser")
        jugadores = [jugador.get_text(strip=True) for jugador in soup.select("p.name")]
        return jugadores

async def main():
    async with aiohttp.ClientSession() as session:
        cambios_detectados = []
        for url in URLS:
            plantilla = await obtener_plantilla(session, url)
            equipo = url.split("/")[4].replace("-", " ").title()
            cambios_detectados.append(f"📋 {equipo}: {', '.join(plantilla)}")

        mensaje_final = f"🔍 Revisión completada ({datetime.now().strftime('%d/%m/%Y %H:%M')})\n\n"
        mensaje_final += "\n".join(cambios_detectados)

        await enviar_mensaje(mensaje_final)

if __name__ == "__main__":
    asyncio.run(main())
