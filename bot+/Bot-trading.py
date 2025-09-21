import datetime

def log_event(text):
    with open("btc_trading_log.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")
    print(f"[{datetime.datetime.now()}] {text}")  # También mostrar en consola

# Bot de trading para Binance (criptomonedas)
# Requiere: python-binance
# Estrategia: cruce de medias móviles (ejemplo)
# NOTA: Usa tus propias claves API de Binance

from binance.client import Client
import numpy as np
import time
import threading
# import tkinter as tk  # Comentado para uso futuro en PC
# from tkinter import scrolledtext  # Comentado para uso futuro en PC

# Importar configuración segura
try:
    from secure_config import get_binance_keys
    binance_config = get_binance_keys()
    API_KEY = binance_config['api_key']
    API_SECRET = binance_config['secret_key']
    IS_TESTNET = binance_config['testnet']
    print(f"🔐 Bot básico - Configuración cargada: {'Producción' if not IS_TESTNET else 'Testnet'}")
except ImportError:
    print("⚠️  secure_config no disponible, usando configuración local")
    # Mantener claves actuales como fallback
    API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
    API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'
    IS_TESTNET = True  # Por seguridad, asumir testnet si no hay config segura

# Parámetros de trading
SYMBOL = 'BTCUSDT'  # Bitcoin/USDT para mejores ganancias visibles
INTERVAL = '1m'  # intervalo de velas
QUANTITY = 0.0001  # 0.0001 BTC = ~$6-7 USD por trade
SHORT_WINDOW = 3  # media móvil corta (3 minutos)
LONG_WINDOW = 7  # media móvil larga (7 minutos)

# Parámetros de gestión de riesgo
STOP_LOSS_PCT = 0.003  # 0.3% stop loss (ajustado para BTC)
TAKE_PROFIT_PCT = 0.006  # 0.6% take profit (ajustado para BTC)
MAX_TRADES_PER_DAY = 50  # Límite diario más razonable

client = Client(API_KEY, API_SECRET)

trade_count = 0
last_buy_price = None

def get_klines(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    close_prices = [float(k[4]) for k in klines]
    return np.array(close_prices)

def simple_strategy():
    prices = get_klines(SYMBOL, INTERVAL, limit=LONG_WINDOW+1)
    short_ma = np.mean(prices[-SHORT_WINDOW:])
    long_ma = np.mean(prices[-LONG_WINDOW:])
    return short_ma, long_ma

def place_order(side, quantity):
    try:
        order = client.create_order(
            symbol=SYMBOL,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        print(f"Orden {side} ejecutada: {order['fills'][0]['price']}")
    except Exception as e:
        print(f"Error al ejecutar orden: {e}")

def run_bot_console():
    global trade_count, last_buy_price
    print("Bot de trading en modo consola (sin interfaz gráfica)")
    total_profit = 0.0
    while trade_count < MAX_TRADES_PER_DAY:
        short_ma, long_ma = simple_strategy()
        current_price = get_klines(SYMBOL, INTERVAL, limit=1)[-1]
        print(f"Precio actual BTC: ${current_price:.2f}")
        print(f"MA corta: ${short_ma:.2f}, MA larga: ${long_ma:.2f}")
        
        # Estrategia: compra si la corta > larga, vende si la corta < larga
        if short_ma > long_ma and last_buy_price is None:
            print(f"COMPRA BTC a ${current_price:.2f}")
            log_event(f"COMPRA BTC a ${current_price:.2f}")
            last_buy_price = current_price
            trade_count += 1
        elif last_buy_price:
            if current_price <= last_buy_price * (1 - STOP_LOSS_PCT):
                print(f"STOP LOSS activado. Venta BTC a ${current_price:.2f}")
                log_event(f"STOP LOSS activado. Venta BTC a ${current_price:.2f}")
                profit = (current_price - last_buy_price) * QUANTITY
                total_profit += profit
                log_event(f"Ganancia/Pérdida: ${profit:.2f} USD | Acumulado: ${total_profit:.2f} USD")
                last_buy_price = None
                trade_count += 1
            elif current_price >= last_buy_price * (1 + TAKE_PROFIT_PCT):
                print(f"TAKE PROFIT activado. Venta BTC a ${current_price:.2f}")
                log_event(f"TAKE PROFIT activado. Venta BTC a ${current_price:.2f}")
                profit = (current_price - last_buy_price) * QUANTITY
                total_profit += profit
                log_event(f"Ganancia/Pérdida: ${profit:.2f} USD | Acumulado: ${total_profit:.2f} USD")
                last_buy_price = None
                trade_count += 1
            elif short_ma < long_ma:
                print(f"VENTA BTC por cruce a ${current_price:.2f}")
                log_event(f"VENTA BTC por cruce a ${current_price:.2f}")
                profit = (current_price - last_buy_price) * QUANTITY
                total_profit += profit
                log_event(f"Ganancia/Pérdida: ${profit:.2f} USD | Acumulado: ${total_profit:.2f} USD")
                last_buy_price = None
                trade_count += 1
            else:
                print("Sin señal clara o esperando gestión de riesgo")
        else:
            print("Sin señal clara")
        time.sleep(60)  # Esperar 60 segundos entre iteraciones para BTC
    print(f"Bot BTC detenido. Ganancia/Pérdida total: ${total_profit:.2f} USD")
    log_event(f"Bot BTC detenido. Ganancia/Pérdida total: ${total_profit:.2f} USD")

# ------------------ GUÍA DE USO ------------------
'''
GUÍA RÁPIDA PARA USAR EL BOT DE TRADING BINANCE

1. Instala las dependencias:
   pip install python-binance numpy

2. Coloca tus claves API de Binance en las variables API_KEY y API_SECRET.

3. (Opcional) Ajusta los parámetros de gestión de riesgo:
   - STOP_LOSS_PCT: porcentaje de stop loss (ej: 0.02 para 2%)
   - TAKE_PROFIT_PCT: porcentaje de take profit (ej: 0.04 para 4%)
   - MAX_TRADES_PER_DAY: máximo de operaciones por día

4. Ejecuta el bot:
   python Bot-trading.py

5. El bot imprime señales y gestiona el riesgo automáticamente.
   Para operar con dinero real, descomenta las líneas de place_order.

¡Recuerda que operar con criptomonedas implica riesgos! Usa el bot bajo tu propia responsabilidad.
'''

if __name__ == "__main__":
    # --- Para uso en VM (consola) ---
    run_bot_console()
    # --- Para uso en PC con interfaz gráfica, descomentar estas líneas ---
    # root = tk.Tk()
    # app = TradingBotGUI(root)
    # root.mainloop()
