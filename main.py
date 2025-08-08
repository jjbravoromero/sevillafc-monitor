import asyncio
import aiohttp
import json
import os
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Lista de URLs a monitorizar
EQUIPOS = {
    "Athletic Club": "https://www.laliga.com/clubes/athletic-club/plantilla",
    "Atlético de Madrid": "https://www.laliga.com/clubes/atletico-de-madrid/plantilla",
    "Osasuna": "https://www.laliga.com/clubes/c-a-osasuna/plantilla",
    "Celta": "https://www.laliga.com/clubes/rc-celta/plantilla",
    "Alavés": "https://www.laliga.com/clubes/d-alaves/plantilla",
    "Elche": "https://www.laliga.com/clubes/elche-c-f/plantilla",
    "FC Barcelona": "https://www.laliga.com/clubes/fc-barcelona/plantilla",
    "Getafe": "https://www.laliga.com/clubes/getafe-cf/plantilla",
    "Girona": "https://www.laliga.com/clubes/girona-fc/plantilla",
    "Levante": "https://www.laliga.com/clubes/levante-ud/plantilla",
    "Rayo Vallecano": "https://www.laliga.com/clubes/rayo-vallecano/plantilla",
    "Espanyol": "https://www.laliga.com/clubes/rcd-espanyol/plantilla",
    "Mallorca": "https://www.laliga.com/clubes/rcd-mallorca/plantilla",
    "Real Betis": "https://www.laliga.com/clubes/real-betis/plantilla",
    "Real Madrid": "https://www.laliga.com/clubes/real-madrid/plantilla",
    "Real Oviedo": "https://www.laliga.com/clubes/real-oviedo/plantilla",
    "Real Sociedad": "https://www.laliga.com/clubes/real-sociedad/plantilla",
    "Sevilla FC": "https://www.laliga.com/clubes/sevilla-fc/plantilla",
    "Valencia CF": "https://www.laliga.com/clubes/valencia-cf/plantilla",
    "Villarreal": "https://www.laliga.com/clubes/villarreal-cf/plantilla",
}

DATA_FILE = "plantillas.json"

async def enviar_mensaje(texto):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

async def obtener_jugadores(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            jugadores = [j.get_text(strip=True) for j in soup.select("span.name")]
            return jugadores

async def main():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            datos_guardados = json.load(f)
    else:
        datos_guardados = {}

    cambios_detectados = []

    for equipo, url in EQUIPOS.items():
        jugadores_actuales = await obtener_jugadores(url)
        jugadores_previos = datos_guardados.get(equipo, [])

        nuevos = sorted(set(jugadores_actuales) - set(jugadores_previos))
        salientes = sorted(set(jugadores_previos) - set(jugadores_actuales))

        if nuevos or salientes:
            mensaje = f"📢 Cambios en {equipo} ({datetime.now().strftime('%d/%m/%Y %H:%M')}):\n"
            if nuevos:
                mensaje += f"🆕 Nuevos: {', '.join(nuevos)}\n"
            if salientes:
                mensaje += f"❌ Bajas: {', '.join(salientes)}\n"
            cambios_detectados.append(mensaje)

        datos_guardados[equipo] = jugadores_actuales

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos_guardados, f, ensure_ascii=False, indent=2)

    if cambios_detectados:
        await enviar_mensaje("\n\n".join(cambios_detectados))
    else:
        await enviar_mensaje(f"🔍 Revisión completada ({datetime.now().strftime('%d/%m/%Y %H:%M')})\nNo se han detectado cambios.")

if __name__ == "__main__":
    asyncio.run(main())
