import requests
import json

API_BASE = "https://api.laliga.com/api/v3"
TEAMS_URL = f"{API_BASE}/teams"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def obtener_equipos():
    resp = requests.get(TEAMS_URL, headers=HEADERS)
    resp.raise_for_status()
    equipos = resp.json().get("data", [])
    return equipos

def obtener_plantilla(id_equipo):
    url = f"{API_BASE}/teams/{id_equipo}/players"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    jugadores = resp.json().get("data", [])
    return jugadores

def main():
    equipos = obtener_equipos()
    print(f"Se han encontrado {len(equipos)} equipos.\n")

    for equipo in equipos:
        nombre_equipo = equipo.get("name", "Desconocido")
        id_equipo = equipo.get("id")
        print(f"📋 {nombre_equipo} (ID: {id_equipo})")

        try:
            plantilla = obtener_plantilla(id_equipo)
            for jugador in plantilla:
                print(f"  - {jugador.get('name', 'Sin nombre')}")
        except Exception as e:
            print(f"  ❌ Error obteniendo plantilla: {e}")

        print("")

if __name__ == "__main__":
    main()
