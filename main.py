import asyncio
from playwright.async_api import async_playwright
from telegram import Bot
import json
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

URL = "https://www.laliga.com/clubes/sevilla-fc/plantilla"
DATA_FILE = "jugadores.json"

bot = Bot(token=TELEGRAM_TOKEN)

async def obtener_nombres_jugadores():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, wait_until="networkidle")
        await page.wait_for_timeout(5000)
        jugadores = await page.locator("div.player-name").all_inner_texts()
        await browser.close()
        return sorted(set(j.strip() for j in jugadores if j.strip()))

def cargar_jugadores_previos():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def guardar_jugadores(jugadores):
    with open(DATA_FILE, "w") as f:
        json.dump(jugadores, f, indent=2)

async def enviar_mensaje(mensaje):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensaje)

async def main():
    jugadores_actuales = await obtener_nombres_jugadores()
    jugadores_previos = cargar_jugadores_previos()

    nuevos = list(set(jugadores_actuales) - set(jugadores_previos))
    desaparecidos = list(set(jugadores_previos) - set(jugadores_actuales))

    if nuevos or desaparecidos:
        mensaje = "📢 Cambios en la plantilla del Sevilla FC:\n"
        if nuevos:
            mensaje += "\n🆕 Nuevos jugadores:\n" + "\n".join(f"🔴 {j}" for j in nuevos)
        if desaparecidos:
            mensaje += "\n\n❌ Jugadores que ya no están:\n" + "\n".join(f"⚪ {j}" for j in desaparecidos)
        await enviar_mensaje(mensaje)
    else:
        print("Sin cambios detectados.")

    guardar_jugadores(jugadores_actuales)

asyncio.run(main())