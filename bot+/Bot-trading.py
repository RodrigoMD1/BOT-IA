# Bot de trading para Binance (criptomonedas)
# Requiere: python-binance
# Estrategia: cruce de medias móviles (ejemplo)
# NOTA: Usa tus propias claves API de Binance

from binance.client import Client
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import scrolledtext

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

class TradingBotGUI:
    def __init__(self, master):
        self.master = master
        master.title("Bot de Trading Binance")
        master.geometry("600x500")

        self.status_label = tk.Label(master, text="Estado del bot:", font=("Arial", 12))
        self.status_label.pack()
        self.status_text = tk.Label(master, text="Esperando...", fg="blue", font=("Arial", 10))
        self.status_text.pack()

        self.risk_label = tk.Label(master, text=f"Gestión de riesgo:\nStop Loss: {STOP_LOSS_PCT*100}% | Take Profit: {TAKE_PROFIT_PCT*100}% | Máx. operaciones/día: {MAX_TRADES_PER_DAY}", font=("Arial", 10))
        self.risk_label.pack()

        self.signal_label = tk.Label(master, text="Última señal:", font=("Arial", 12))
        self.signal_label.pack()
        self.signal_text = tk.Label(master, text="-", fg="green", font=("Arial", 10))
        self.signal_text.pack()

        self.price_label = tk.Label(master, text="Historial de precios:", font=("Arial", 12))
        self.price_label.pack()
        self.price_box = scrolledtext.ScrolledText(master, width=70, height=10)
        self.price_box.pack()

        self.trade_label = tk.Label(master, text="Operaciones ejecutadas:", font=("Arial", 12))
        self.trade_label.pack()
        self.trade_box = scrolledtext.ScrolledText(master, width=70, height=7)
        self.trade_box.pack()

        self.info_label = tk.Label(master, text="Info adicional:", font=("Arial", 12))
        self.info_label.pack()
        self.info_box = scrolledtext.ScrolledText(master, width=70, height=4)
        self.info_box.pack()
        self.info_box.insert(tk.END, f"Símbolo: {SYMBOL}\nIntervalo: {INTERVAL}\nCantidad: {QUANTITY}\nSaldo mínimo recomendado: 10 USDT\n")
        self.info_box.config(state='disabled')

        self.profit_label = tk.Label(master, text="Ganancia/Pérdida acumulada:", font=("Arial", 12))
        self.profit_label.pack()
        self.profit_text = tk.Label(master, text="0 USDT", fg="purple", font=("Arial", 10))
        self.profit_text.pack()
        self.total_profit = 0.0

        self.stop_button = tk.Button(master, text="Detener bot", command=self.stop_bot, bg="red", fg="white")
        self.stop_button.pack(pady=10)

        self.running = True
        self.thread = threading.Thread(target=self.run_bot)
        self.thread.start()

    def stop_bot(self):
        self.running = False
        self.status_text.config(text="Bot detenido.", fg="red")

    def get_balance(self):
        try:
            balance = client.get_asset_balance(asset=SYMBOL[:-4])
            if balance:
                return f"Saldo actual: {balance['free']} {SYMBOL[:-4]}"
            else:
                return "No se pudo obtener el saldo."
        except Exception as e:
            return f"Error al obtener saldo: {e}"

    def get_min_trade(self):
        try:
            info = client.get_symbol_info(SYMBOL)
            min_qty = None
            for f in info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    min_qty = f['minQty']
            return f"Cantidad mínima de operación: {min_qty} {SYMBOL[:-4]}"
        except Exception as e:
            return f"Error al obtener mínimo: {e}"

    def update_info(self):
        saldo = self.get_balance()
        minimo = self.get_min_trade()
        self.info_box.config(state='normal')
        self.info_box.delete('1.0', tk.END)
        self.info_box.insert(tk.END, f"Símbolo: {SYMBOL}\nIntervalo: {INTERVAL}\nCantidad: {QUANTITY}\nSaldo mínimo recomendado: 10 USDT\n{saldo}\n{minimo}\n")
        self.info_box.config(state='disabled')

    def update_profit(self, profit):
        self.total_profit += profit
        self.profit_text.config(text=f"{self.total_profit:.6f} USDT")

    def run_bot(self):
        global trade_count, last_buy_price
        self.status_text.config(text="Bot en ejecución (estrategia agresiva)", fg="blue")
        while self.running and trade_count < MAX_TRADES_PER_DAY:
            short_ma, long_ma = simple_strategy()
            current_price = get_klines(SYMBOL, INTERVAL, limit=1)[-1]
            self.signal_text.config(text=f"MA corta: {short_ma:.2f}, MA larga: {long_ma:.2f}")
            self.price_box.insert(tk.END, f"Precio actual: {current_price}\n")
            self.price_box.see(tk.END)
            # Estrategia agresiva: compra si la corta >= larga, vende si la corta < larga
            if short_ma >= long_ma and last_buy_price is None:
                self.trade_box.insert(tk.END, f"COMPRA agresiva a {current_price}\n")
                last_buy_price = current_price
                trade_count += 1
            elif last_buy_price:
                if current_price <= last_buy_price * (1 - STOP_LOSS_PCT):
                    self.trade_box.insert(tk.END, f"STOP LOSS activado. Venta a {current_price}\n")
                    profit = (current_price - last_buy_price) * QUANTITY
                    self.update_profit(profit)
                    last_buy_price = None
                    trade_count += 1
                elif current_price >= last_buy_price * (1 + TAKE_PROFIT_PCT):
                    self.trade_box.insert(tk.END, f"TAKE PROFIT activado. Venta a {current_price}\n")
                    profit = (current_price - last_buy_price) * QUANTITY
                    self.update_profit(profit)
                    last_buy_price = None
                    trade_count += 1
                elif short_ma < long_ma:
                    self.trade_box.insert(tk.END, f"VENTA agresiva por cruce a {current_price}\n")
                    profit = (current_price - last_buy_price) * QUANTITY
                    self.update_profit(profit)
                    last_buy_price = None
                    trade_count += 1
                else:
                    self.status_text.config(text="Sin señal clara o esperando gestión de riesgo", fg="orange")
            else:
                self.status_text.config(text="Sin señal clara", fg="orange")
            self.trade_box.see(tk.END)
            time.sleep(30)
        self.status_text.config(text="Bot detenido (límite alcanzado)", fg="red")
        self.update_info()

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
    root = tk.Tk()
    app = TradingBotGUI(root)
    root.mainloop()
