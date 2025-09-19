import datetime

def log_event(text):
    with open("trading_log.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")

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

# Configuración de claves API (rellena con tus datos)
API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'

# Parámetros de trading
SYMBOL = 'SHIBUSDT'
INTERVAL = '1m'  # intervalo de velas
QUANTITY = 0.001  # cantidad a comprar/vender
SHORT_WINDOW = 2  # media móvil muy corta
LONG_WINDOW = 4  # media móvil corta

# Parámetros de gestión de riesgo
STOP_LOSS_PCT = 0.005  # 0.5% stop loss
TAKE_PROFIT_PCT = 0.01  # 1% take profit
MAX_TRADES_PER_DAY = 99999  # Sin límite práctico

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
        print(f"MA corta: {short_ma:.2f}, MA larga: {long_ma:.2f}, Precio actual: {current_price}")
        # Estrategia agresiva: compra si la corta >= larga, vende si la corta < larga
        if short_ma >= long_ma and last_buy_price is None:
            print(f"COMPRA agresiva a {current_price}")
            log_event(f"COMPRA agresiva a {current_price}")
            last_buy_price = current_price
            trade_count += 1
        elif last_buy_price:
            if current_price <= last_buy_price * (1 - STOP_LOSS_PCT):
                print(f"STOP LOSS activado. Venta a {current_price}")
                log_event(f"STOP LOSS activado. Venta a {current_price}")
                profit = (current_price - last_buy_price) * QUANTITY
                total_profit += profit
                log_event(f"Ganancia/Pérdida: {profit:.6f} USDT | Acumulado: {total_profit:.6f} USDT")
                last_buy_price = None
                trade_count += 1
            elif current_price >= last_buy_price * (1 + TAKE_PROFIT_PCT):
                print(f"TAKE PROFIT activado. Venta a {current_price}")
                log_event(f"TAKE PROFIT activado. Venta a {current_price}")
                profit = (current_price - last_buy_price) * QUANTITY
                total_profit += profit
                log_event(f"Ganancia/Pérdida: {profit:.6f} USDT | Acumulado: {total_profit:.6f} USDT")
                last_buy_price = None
                trade_count += 1
            elif short_ma < long_ma:
                print(f"VENTA agresiva por cruce a {current_price}")
                log_event(f"VENTA agresiva por cruce a {current_price}")
                profit = (current_price - last_buy_price) * QUANTITY
                total_profit += profit
                log_event(f"Ganancia/Pérdida: {profit:.6f} USDT | Acumulado: {total_profit:.6f} USDT")
                last_buy_price = None
                trade_count += 1
            else:
                print("Sin señal clara o esperando gestión de riesgo")
        else:
            print("Sin señal clara")
        time.sleep(30)
    print(f"Bot detenido. Ganancia/Pérdida total: {total_profit:.6f} USDT")
    log_event(f"Bot detenido. Ganancia/Pérdida total: {total_profit:.6f} USDT")

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
