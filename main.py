import asyncio
import aiohttp
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot

# Variables de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

ARCHIVO = "plantillas.json"

async def obtener_plantilla(session, url):
    async with session.get(url) as resp:
        html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        nombres = [p.get_text(strip=True) for p in soup.find_all("p", class_="styled__TextRegular-sc-1raci4c-0")]
        return nombres

async def enviar_mensaje(texto):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

async def main():
    async with aiohttp.ClientSession() as session:
        resultados = {}
        for url in URLS:
            equipo = url.split("/")[4].replace("-", " ").title()
            plantilla = await obtener_plantilla(session, url)
            resultados[equipo] = plantilla

        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                anterior = json.load(f)
        else:
            anterior = {}

        cambios = []
        for equipo, plantilla in resultados.items():
            antes = set(anterior.get(equipo, []))
            ahora = set(plantilla)

            nuevos = ahora - antes
            salidos = antes - ahora

            if nuevos:
                cambios.append(f"🆕 {equipo}: {', '.join(nuevos)}")
            if salidos:
                cambios.append(f"❌ {equipo}: {', '.join(salidos)}")

        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)

        if cambios:
            await enviar_mensaje("📢 Cambios detectados:\n" + "\n".join(cambios))
        else:
            await enviar_mensaje(f"🔍 Revisión completada ({datetime.now().strftime('%d/%m/%Y %H:%M')})\nNo se han detectado cambios.")

if __name__ == "__main__":
    asyncio.run(main())
