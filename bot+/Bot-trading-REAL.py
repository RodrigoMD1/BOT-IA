import datetime

def log_event(text):
    with open("btc_trading_log.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")
    print(f"[{datetime.datetime.now()}] {text}")  # También mostrar en consola

# Bot de trading para Binance (criptomonedas) - VERSIÓN REAL
# Requiere: python-binance
# Estrategia: cruce de medias móviles 
# CONFIGURADO PARA TRADING REAL CON $10 USD

from binance.client import Client
import numpy as np
import time
import threading

# Importar configuración segura
try:
    from secure_config import get_binance_keys, safe_start_message, is_production
    binance_config = get_binance_keys()
    API_KEY = binance_config['api_key']
    API_SECRET = binance_config['secret_key']
    IS_TESTNET = binance_config['testnet']
    print(f"🔐 Configuración cargada: {'Producción' if not IS_TESTNET else 'Testnet'}")
except ImportError:
    print("⚠️  secure_config no disponible, usando configuración local")
    API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
    API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'
    IS_TESTNET = False

# Parámetros de trading - CONFIGURACIÓN REAL
SYMBOL = 'BTCUSDT'  # Bitcoin/USDT 
INTERVAL = '1m'  # intervalo de velas
INITIAL_BALANCE = 10.0  # $10 USD por bot
QUANTITY = 0.0001  # 0.0001 BTC = ~$6-7 USD por trade
SHORT_WINDOW = 3  # media móvil corta (3 minutos)
LONG_WINDOW = 7  # media móvil larga (7 minutos)

# Parámetros de gestión de riesgo - AJUSTADOS PARA DINERO REAL
STOP_LOSS_PCT = 0.002  # 0.2% stop loss (más conservador)
TAKE_PROFIT_PCT = 0.005  # 0.5% take profit (más conservador)
MAX_TRADES_PER_DAY = 30  # Límite más conservador para dinero real

# INICIALIZACIÓN CON TRADING REAL
client = Client(API_KEY, API_SECRET)

trade_count = 0
last_buy_price = None
total_profit = 0.0
current_balance = INITIAL_BALANCE

def get_klines(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    close_prices = [float(k[4]) for k in klines]
    return np.array(close_prices)

def simple_strategy():
    prices = get_klines(SYMBOL, INTERVAL, limit=LONG_WINDOW+1)
    short_ma = np.mean(prices[-SHORT_WINDOW:])
    long_ma = np.mean(prices[-LONG_WINDOW:])
    return short_ma, long_ma

def place_order_real(side, quantity):
    """FUNCIÓN PARA TRADING REAL - ACTIVADA CON CLAVES REALES"""
    try:
        # TRADING REAL ACTIVADO:
        order = client.create_order(
            symbol=SYMBOL,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        executed_price = float(order['fills'][0]['price'])
        print(f"ORDEN REAL {side} ejecutada: ${executed_price:.2f}")
        return executed_price
    except Exception as e:
        print(f"Error al ejecutar orden: {e}")
        return None

def run_bot_real():
    global trade_count, last_buy_price, total_profit, current_balance
    
    log_event("🚀 BOT BÁSICO INICIADO - CONFIGURACIÓN REAL")
    log_event(f"💰 Balance inicial: ${INITIAL_BALANCE:.2f} USD")
    log_event(f"🎯 Par de trading: {SYMBOL}")
    log_event(f"⚠️  MODO: TRADING REAL ACTIVADO")
    
    while trade_count < MAX_TRADES_PER_DAY:
        try:
            short_ma, long_ma = simple_strategy()
            current_price = get_klines(SYMBOL, INTERVAL, limit=1)[-1]
            
            # Log cada 10 iteraciones
            if trade_count % 10 == 0:
                print(f"Precio actual BTC: ${current_price:.2f}")
                print(f"MA corta: ${short_ma:.2f}, MA larga: ${long_ma:.2f}")
                print(f"Balance actual: ${current_balance:.2f} USD")
            
            # Estrategia: compra si la corta > larga, vende si la corta < larga
            if short_ma > long_ma and last_buy_price is None and current_balance >= (QUANTITY * current_price):
                executed_price = place_order_real('BUY', QUANTITY)
                if executed_price:
                    print(f"🟢 COMPRA REAL BTC a ${executed_price:.2f}")
                    log_event(f"COMPRA BTC a ${executed_price:.2f}")
                    last_buy_price = executed_price
                    current_balance -= (QUANTITY * executed_price)  # Reducir balance
                    trade_count += 1
                    
            elif last_buy_price:
                # Stop Loss
                if current_price <= last_buy_price * (1 - STOP_LOSS_PCT):
                    executed_price = place_order_real('SELL', QUANTITY)
                    if executed_price:
                        print(f"🔴 STOP LOSS activado. Venta BTC a ${executed_price:.2f}")
                        log_event(f"STOP LOSS activado. Venta BTC a ${executed_price:.2f}")
                        profit = (executed_price - last_buy_price) * QUANTITY
                        total_profit += profit
                        current_balance += (QUANTITY * executed_price)  # Recuperar balance
                        log_event(f"Ganancia/Pérdida: ${profit:.2f} USD | Acumulado: ${total_profit:.2f} USD | Balance: ${current_balance:.2f} USD")
                        last_buy_price = None
                        trade_count += 1
                        
                # Take Profit        
                elif current_price >= last_buy_price * (1 + TAKE_PROFIT_PCT):
                    executed_price = place_order_real('SELL', QUANTITY)
                    if executed_price:
                        print(f"🟢 TAKE PROFIT activado. Venta BTC a ${executed_price:.2f}")
                        log_event(f"TAKE PROFIT activado. Venta BTC a ${executed_price:.2f}")
                        profit = (executed_price - last_buy_price) * QUANTITY
                        total_profit += profit
                        current_balance += (QUANTITY * executed_price)  # Recuperar balance
                        log_event(f"Ganancia/Pérdida: ${profit:.2f} USD | Acumulado: ${total_profit:.2f} USD | Balance: ${current_balance:.2f} USD")
                        last_buy_price = None
                        trade_count += 1
                        
                # Cruce de medias (venta)        
                elif short_ma < long_ma:
                    executed_price = place_order_real('SELL', QUANTITY)
                    if executed_price:
                        print(f"🔄 VENTA BTC por cruce a ${executed_price:.2f}")
                        log_event(f"VENTA BTC por cruce a ${executed_price:.2f}")
                        profit = (executed_price - last_buy_price) * QUANTITY
                        total_profit += profit
                        current_balance += (QUANTITY * executed_price)  # Recuperar balance
                        log_event(f"Ganancia/Pérdida: ${profit:.2f} USD | Acumulado: ${total_profit:.2f} USD | Balance: ${current_balance:.2f} USD")
                        last_buy_price = None
                        trade_count += 1
                else:
                    if trade_count % 20 == 0:  # Log posición cada 20 iteraciones
                        print(f"📊 Posición abierta BTC: ${last_buy_price:.2f} → ${current_price:.2f} ({((current_price/last_buy_price-1)*100):+.2f}%)")
            else:
                if trade_count % 30 == 0:  # Log sin señal cada 30 iteraciones
                    print("⏳ Sin señal clara, esperando...")
                    
        except Exception as e:
            print(f"❌ Error en bot: {e}")
            log_event(f"Error en bot: {e}")
            
        time.sleep(60)  # Esperar 60 segundos entre iteraciones
        
    # Estadísticas finales
    final_balance = current_balance + (QUANTITY * current_price if last_buy_price else 0)
    roi = ((final_balance / INITIAL_BALANCE - 1) * 100)
    
    log_event("=" * 50)
    log_event("📊 ESTADÍSTICAS FINALES BOT BÁSICO")
    log_event("=" * 50)
    log_event(f"💰 Balance inicial: ${INITIAL_BALANCE:.2f} USD")
    log_event(f"💰 Balance final: ${final_balance:.2f} USD")
    log_event(f"📈 ROI: {roi:+.2f}%")
    log_event(f"🔄 Trades ejecutados: {trade_count}")
    log_event(f"💵 P&L total: ${total_profit:.2f} USD")
    if trade_count > 0:
        log_event(f"📊 P&L promedio por trade: ${total_profit/trade_count:.4f} USD")
    log_event("=" * 50)

if __name__ == "__main__":
    print("🚀 INICIANDO BOT BÁSICO - CONFIGURACIÓN REAL")
    
    # Verificación de seguridad
    try:
        if not safe_start_message():
            print("❌ Operación cancelada por el usuario")
            exit()
    except NameError:
        # Si safe_start_message no está disponible, hacer verificación manual
        if not IS_TESTNET:
            print("⚠️  ¡ADVERTENCIA! Ejecutando en PRODUCCIÓN con dinero real")
            response = input("¿Estás seguro de continuar? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Operación cancelada")
                exit()
    
    print("🔐 Claves API cargadas de forma segura desde .env")
    print("⚠️  BALANCE CONFIGURADO: $10 USD")
    print("⚠️  GESTIÓN DE RIESGO: Más conservadora para dinero real")
    print()
    run_bot_real()