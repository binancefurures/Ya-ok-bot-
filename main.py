import requests
import time
import os

# === VARIABLES DE ENTORNO ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        response = requests.post(url, data=data)
        print(f"Telegram status: {response.status_code} -> {response.text}")
        if response.status_code != 200:
            print("Error enviando mensaje:", response.text)
    except Exception as e:
        print("Error al conectar con Telegram:", e)

def obtener_pares_futuros():
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
        data = response.json()
        if "symbols" not in data:
            print("⚠️ La respuesta no contiene 'symbols'. Respuesta completa:")
            print(data)
            return []
        return [s["symbol"] for s in data["symbols"] if s["contractType"] == "PERPETUAL"]
    except Exception as e:
        print("❌ Error al consultar pares futuros:", e)
        return []

def obtener_subidas_destacadas(pares_futuros, ya_alertados):
    try:
        response = requests.get("https://fapi.binance.com/fapi/v1/ticker/24hr")
        data = response.json()
        if not isinstance(data, list):
            print("⚠️ La respuesta no es una lista:")
            print(data)
            return []
        destacados = []
        for d in data:
            symbol = d.get("symbol")
            change_percent = float(d.get("priceChangePercent", 0))
            if symbol in pares_futuros and change_percent > 30:
                if symbol not in ya_alertados:
                    destacados.append({
                        "symbol": symbol,
                        "percent": change_percent,
                        "price": d.get("lastPrice")
                    })
        return destacados
    except Exception as e:
        print("❌ Error al consultar subidas destacadas:", e)
        return []

# === INICIO DEL BOT ===
print("📡 Bot activo - esperando nuevos listados o subidas de +30%...")
enviar_telegram("🤖 Bot de alertas Binance Futures ACTIVADO 🚀")

pares_anteriores = set(obtener_pares_futuros())
pares_alertados_subida = set()

while True:
    time.sleep(120)  # cada 2 minutos

    # Verificar nuevos listados
    pares_actuales = set(obtener_pares_futuros())
    nuevos = pares_actuales - pares_anteriores

    for nuevo in nuevos:
        mensaje = f"🚨 NUEVO LISTADO EN BINANCE FUTURES:\n➡️ {nuevo}\n📈 ¡Revisa ahora antes del FOMO! 🔥"
        print(mensaje)
        enviar_telegram(mensaje)

    if nuevos:
        pares_anteriores = pares_actuales

    # Verificar subidas destacadas
    subidas = obtener_subidas_destacadas(pares_actuales, pares_alertados_subida)

    for subida in subidas:
        mensaje = (
            f"🚀 SUBIDA DESTACADA EN BINANCE FUTURES\n\n"
            f"Par: {subida['symbol']}\n"
            f"Cambio 24h: +{subida['percent']:.2f}%\n"
            f"Precio actual: ${subida['price']}\n"
            f"📊 ¡Revisa el gráfico ya!"
        )
        print(mensaje)
        enviar_telegram(mensaje)
        pares_alertados_subida.add(subida["symbol"])