"""
Bot de Trading con Machine Learning para Binance - VERSIÓN REAL
Optimizado para ejecución 24/7 en Google Cloud VM
Configurado para trading real con $10 USD
"""

import datetime
import numpy as np
import pandas as pd
from binance.client import Client
import time
import warnings
import os
import signal
import sys
warnings.filterwarnings('ignore')

def log_event(text, log_file="ml_btc_trading_real_log.txt"):
    """Log con timestamp y identificación ML REAL"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] [ML-REAL] {text}\n")
    print(f"[{timestamp}] [ML-REAL] {text}")

# Configuración de claves API de Binance - CLAVES REALES DE PRODUCCIÓN
API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'

# Parámetros de trading - CONFIGURACIÓN REAL
SYMBOL = 'BTCUSDT'  # Bitcoin/USDT para ML
INTERVAL = '1m'
QUANTITY = 0.0001   # 0.0001 BTC = ~$6-7 USD por trade
INITIAL_BALANCE = 10.0  # $10 USD por bot (50% del total de $20)

# Parámetros de ML simplificado - AJUSTADOS PARA DINERO REAL
LOOKBACK_PERIOD = 30
MIN_CONFIDENCE = 0.70  # Aumentado a 70% para dinero real (más conservador)

# Parámetros de gestión de riesgo para DINERO REAL
BASE_STOP_LOSS = 0.002      # 0.2% stop loss (más conservador)
BASE_TAKE_PROFIT = 0.006    # 0.6% take profit (más conservador)
MAX_POSITION_SIZE = 0.8     # Usar máximo 80% del balance

client = Client(API_KEY, API_SECRET)

class RealMLBot:
    def __init__(self):
        self.historical_prices = []
        self.historical_volumes = []
        self.predictions_history = []
        self.balance = INITIAL_BALANCE
        self.current_position = None
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        self.start_time = datetime.datetime.now()
        self.last_heartbeat = datetime.datetime.now()
        
        # Setup signal handlers para shutdown limpio
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Maneja shutdown del bot limpiamente"""
        log_event("Bot ML REAL recibió señal de cierre, cerrando posiciones...")
        if self.current_position:
            try:
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                self.close_position(current_price, "Bot detenido - shutdown")
            except Exception as e:
                log_event(f"Error cerrando posición en shutdown: {e}")
        
        self.print_final_statistics()
        log_event("Bot ML REAL detenido limpiamente")
        sys.exit(0)
        
    def get_market_data(self, symbol, interval, limit=100):
        """Obtiene datos del mercado con retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
                df = pd.DataFrame(klines, columns=[
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                    'taker_buy_quote_volume', 'ignore'
                ])
                
                # Convertir a numérico
                numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col])
                    
                return df
            except Exception as e:
                log_event(f"Error obteniendo datos (intento {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    return None
    
    def calculate_advanced_features(self, df):
        """Calcula características avanzadas para predicción"""
        # Medias móviles
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_10'] = df['close'].rolling(window=10).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12).mean()
        exp2 = df['close'].ewm(span=26).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volatilidad
        df['volatility'] = df['close'].rolling(window=10).std()
        
        # Momentum
        df['momentum'] = df['close'] / df['close'].shift(5) - 1
        
        # Price rate of change
        df['roc'] = df['close'].pct_change(periods=10)
        
        # Volume features
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        return df
    
    def enhanced_ml_prediction(self):
        """Algoritmo ML conservador para dinero real"""
        df = self.get_market_data(SYMBOL, INTERVAL, limit=60)
        if df is None:
            return None, 0
        
        df = self.calculate_advanced_features(df)
        
        # Obtener últimos valores
        latest_data = df.iloc[-1]
        
        current_price = latest_data['close']
        ma_5 = latest_data['ma_5']
        ma_10 = latest_data['ma_10']
        ma_20 = latest_data['ma_20']
        rsi = latest_data['rsi']
        macd = latest_data['macd']
        macd_signal = latest_data['macd_signal']
        bb_position = latest_data['bb_position']
        momentum = latest_data['momentum']
        volume_ratio = latest_data['volume_ratio']
        
        # Algoritmo ML CONSERVADOR para dinero real
        prediction_score = 0
        confidence_factors = []
        
        # Factor 1: Convergencia de medias móviles (peso: 30% - más peso)
        if not np.isnan(ma_5) and not np.isnan(ma_10) and not np.isnan(ma_20):
            if ma_5 > ma_10 > ma_20:
                ma_strength = (ma_5 - ma_20) / ma_20
                prediction_score += ma_strength * 0.30
                confidence_factors.append(min(ma_strength * 4, 1))
            elif ma_5 < ma_10 < ma_20:
                ma_weakness = (ma_20 - ma_5) / ma_20
                prediction_score -= ma_weakness * 0.30
                confidence_factors.append(min(ma_weakness * 4, 1))
        
        # Factor 2: RSI con límites más estrictos (peso: 25%)
        if not np.isnan(rsi):
            if rsi < 20:  # Sobreventa muy extrema
                prediction_score += 0.25
                confidence_factors.append(0.95)
            elif rsi > 80:  # Sobrecompra muy extrema
                prediction_score -= 0.25
                confidence_factors.append(0.95)
            elif 30 < rsi < 70:  # Zona neutral más amplia
                rsi_factor = (rsi - 50) / 50 * 0.5  # Reducido para ser más conservador
                prediction_score += rsi_factor * 0.15
                confidence_factors.append(abs(rsi_factor) * 0.3)
        
        # Factor 3: MACD más estricto (peso: 20%)
        if not np.isnan(macd) and not np.isnan(macd_signal):
            macd_diff = macd - macd_signal
            if macd > 0 and macd_diff > 0 and macd_diff > abs(macd) * 0.1:  # Señal más fuerte
                prediction_score += 0.15
                confidence_factors.append(0.85)
            elif macd < 0 and macd_diff < 0 and abs(macd_diff) > abs(macd) * 0.1:
                prediction_score -= 0.15
                confidence_factors.append(0.85)
        
        # Factor 4: Bollinger Bands conservador (peso: 15%)
        if not np.isnan(bb_position):
            if bb_position < 0.1:  # Muy cerca del límite inferior
                prediction_score += 0.12
                confidence_factors.append(0.8)
            elif bb_position > 0.9:  # Muy cerca del límite superior
                prediction_score -= 0.12
                confidence_factors.append(0.8)
        
        # Factor 5: Volume confirmation más estricto (peso: 10%)
        if not np.isnan(volume_ratio):
            if volume_ratio > 2.0:  # Volumen muy alto
                volume_strength = min((volume_ratio - 1) / 3, 1)
                if prediction_score > 0:
                    prediction_score += volume_strength * 0.08
                else:
                    prediction_score -= volume_strength * 0.08
                confidence_factors.append(volume_strength)
        
        # Calcular confianza CONSERVADORA
        if confidence_factors:
            base_confidence = np.mean(confidence_factors)
            consistency = 1 - np.std(confidence_factors)
            # Reducir confianza para ser más conservador
            confidence = min(base_confidence * consistency * 1.2, 0.95)
        else:
            confidence = 0
        
        # Guardar en historial
        self.predictions_history.append({
            'timestamp': datetime.datetime.now(),
            'price': current_price,
            'prediction': prediction_score,
            'confidence': confidence,
            'rsi': rsi,
            'macd': macd,
            'bb_position': bb_position,
            'volume_ratio': volume_ratio
        })
        
        if len(self.predictions_history) > 100:
            self.predictions_history.pop(0)
        
        return prediction_score, confidence
    
    def place_real_order(self, side, quantity):
        """Ejecutar orden REAL - ACTIVADA CON CLAVES REALES"""
        try:
            # TRADING REAL ACTIVADO:
            order = client.create_order(
                symbol=SYMBOL,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            executed_price = float(order['fills'][0]['price'])
            log_event(f"ORDEN REAL {side} ejecutada: ${executed_price:.2f}")
            return executed_price
            
        except Exception as e:
            log_event(f"Error ejecutando orden {side}: {e}")
            return None
    
    def execute_real_ml_strategy(self, prediction, confidence, current_price):
        """Ejecuta estrategia ML REAL con gestión conservadora"""
        # Umbral más alto para dinero real
        prediction_threshold = 0.025  # 2.5% mínimo
        
        # Verificar balance disponible
        available_balance = self.balance * MAX_POSITION_SIZE
        position_value = QUANTITY * current_price
        
        # Señal de compra con confianza muy alta y balance suficiente
        if (prediction > prediction_threshold and 
            confidence > MIN_CONFIDENCE and 
            not self.current_position and
            available_balance >= position_value):
            
            executed_price = self.place_real_order('BUY', QUANTITY)
            if executed_price:
                stop_loss = executed_price * (1 - BASE_STOP_LOSS)
                take_profit = executed_price * (1 + BASE_TAKE_PROFIT)
                
                log_event(f"🟢 COMPRA ML REAL - Pred: +{prediction*100:.2f}% | Conf: {confidence*100:.1f}% | Precio: ${executed_price:.2f}")
                log_event(f"   📊 SL: ${stop_loss:.2f} | TP: ${take_profit:.2f}")
                
                self.current_position = {
                    'type': 'LONG',
                    'entry_price': executed_price,
                    'quantity': QUANTITY,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'entry_time': datetime.datetime.now(),
                    'prediction': prediction,
                    'confidence': confidence
                }
                self.balance -= position_value
                
        # Gestión de posición existente
        elif self.current_position:
            self.manage_real_position(current_price)
    
    def manage_real_position(self, current_price):
        """Gestiona posición REAL con trailing stop conservador"""
        position = self.current_position
        
        if position['type'] == 'LONG':
            time_in_position = datetime.datetime.now() - position['entry_time']
            hours_in_position = time_in_position.total_seconds() / 3600
            
            # Stop Loss
            if current_price <= position['stop_loss']:
                self.close_real_position(current_price, "Stop Loss")
                
            # Take Profit
            elif current_price >= position['take_profit']:
                self.close_real_position(current_price, "Take Profit")
                
            # Trailing Stop muy conservador
            elif current_price > position['entry_price'] * 1.008:  # Solo si hay +0.8% ganancia
                trailing_pct = 0.003  # 0.3% trailing stop
                new_stop = current_price * (1 - trailing_pct)
                if new_stop > position['stop_loss']:
                    position['stop_loss'] = new_stop
                    log_event(f"🔄 Trailing Stop: ${new_stop:.2f}")
            
            # Stop Loss por tiempo (12 horas máximo para dinero real)
            elif hours_in_position > 12:
                log_event(f"⏰ Cerrando posición por tiempo límite (12h)")
                self.close_real_position(current_price, "Tiempo límite")
    
    def close_real_position(self, current_price, reason):
        """Cierra posición REAL con logging detallado"""
        if not self.current_position:
            return
        
        position = self.current_position
        executed_price = self.place_real_order('SELL', position['quantity'])
        
        if executed_price:
            profit_loss = (executed_price - position['entry_price']) * position['quantity']
            profit_pct = (executed_price / position['entry_price'] - 1) * 100
            time_in_position = datetime.datetime.now() - position['entry_time']
            
            self.balance += (position['quantity'] * executed_price)
            self.total_profit += profit_loss
            self.total_trades += 1
            
            if profit_loss > 0:
                self.winning_trades += 1
                log_event(f"✅ VENTA EXITOSA REAL - {reason} | P&L: +${profit_loss:.4f} USD (+{profit_pct:.2f}%) | Tiempo: {time_in_position}")
            else:
                log_event(f"❌ PÉRDIDA REAL - {reason} | P&L: ${profit_loss:.4f} USD ({profit_pct:.2f}%) | Tiempo: {time_in_position}")
            
            log_event(f"💰 Balance actualizado: ${self.balance:.4f} USD | ROI: {((self.balance/INITIAL_BALANCE-1)*100):+.2f}%")
            
        self.current_position = None
    
    def print_periodic_statistics(self):
        """Estadísticas periódicas para dinero real"""
        runtime = datetime.datetime.now() - self.start_time
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        roi = ((self.balance / INITIAL_BALANCE - 1) * 100)
        
        log_event(f"📊 [STATS REAL] Runtime: {runtime} | Balance: ${self.balance:.4f} USD | ROI: {roi:+.2f}% | Trades: {self.total_trades} | Win Rate: {win_rate:.1f}%")
        
        if len(self.predictions_history) >= 10:
            recent_confidence = [p['confidence'] for p in self.predictions_history[-10:]]
            avg_confidence = np.mean(recent_confidence)
            log_event(f"🧠 [ML REAL] Confianza promedio: {avg_confidence*100:.1f}% | Umbral: {MIN_CONFIDENCE*100}%")
    
    def print_final_statistics(self):
        """Estadísticas finales para dinero real"""
        runtime = datetime.datetime.now() - self.start_time
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        roi = ((self.balance / INITIAL_BALANCE - 1) * 100)
        
        log_event("=" * 60)
        log_event("🤖 ESTADÍSTICAS FINALES DEL BOT ML REAL")
        log_event("=" * 60)
        log_event(f"⏱️  Tiempo de ejecución: {runtime}")
        log_event(f"💰 Balance inicial: ${INITIAL_BALANCE:.2f} USD")
        log_event(f"💰 Balance final: ${self.balance:.4f} USD")
        log_event(f"📈 ROI total: {roi:+.2f}%")
        log_event(f"🔄 Trades ejecutados: {self.total_trades}")
        log_event(f"✅ Trades ganadores: {self.winning_trades}")
        log_event(f"📊 Tasa de éxito: {win_rate:.1f}%")
        if self.total_trades > 0:
            log_event(f"💵 Ganancia promedio por trade: ${self.total_profit/self.total_trades:.6f} USD")
        log_event(f"🧠 Predicciones generadas: {len(self.predictions_history)}")
        log_event("=" * 60)
    
    def run_real_ml_bot(self):
        """Ejecuta bot ML REAL con configuración conservadora"""
        log_event("🚀 Iniciando Bot ML REAL en Google Cloud")
        log_event(f"💰 Balance inicial: ${self.balance:.2f} USD")
        log_event(f"🎯 Par de trading: {SYMBOL}")
        log_event(f"₿ Cantidad por trade: {QUANTITY} BTC (~${QUANTITY * 65000:.2f} USD aprox)")
        log_event(f"🧠 Confianza mínima: {MIN_CONFIDENCE*100}% (CONSERVADOR)")
        log_event(f"🛡️  Stop Loss: {BASE_STOP_LOSS*100}% (CONSERVADOR)")
        log_event(f"🎯 Take Profit: {BASE_TAKE_PROFIT*100}% (CONSERVADOR)")
        log_event(f"⚠️  MODO: TRADING REAL ACTIVADO")
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                
                # Heartbeat cada hora
                now = datetime.datetime.now()
                if (now - self.last_heartbeat).total_seconds() > 3600:
                    self.last_heartbeat = now
                    runtime = now - self.start_time
                    log_event(f"💓 [HEARTBEAT REAL] Bot ML ejecutándose hace {runtime} | Balance: ${self.balance:.4f} USD")
                
                # Obtener precio actual
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                
                # Generar predicción ML
                prediction, confidence = self.enhanced_ml_prediction()
                
                if prediction is not None:
                    # Log cada 15 iteraciones para dinero real
                    if iteration % 15 == 0 or confidence > MIN_CONFIDENCE:
                        log_event(f"[{iteration}] Precio BTC: ${current_price:.2f} | Pred: {prediction:+.4f} | Conf: {confidence*100:.1f}%")
                    
                    if self.current_position:
                        time_in_pos = datetime.datetime.now() - self.current_position['entry_time']
                        if iteration % 30 == 0:
                            log_event(f"📍 Posición REAL activa: {self.current_position['type']} desde ${self.current_position['entry_price']:.2f} | Tiempo: {time_in_pos}")
                    
                    # Ejecutar estrategia ML REAL
                    self.execute_real_ml_strategy(prediction, confidence, current_price)
                
                # Estadísticas cada 150 iteraciones
                if iteration % 150 == 0:
                    self.print_periodic_statistics()
                
                # Esperar más tiempo para dinero real (45 segundos)
                time.sleep(45)
                
            except KeyboardInterrupt:
                log_event("🛑 Bot ML REAL detenido manualmente")
                break
            except Exception as e:
                log_event(f"❌ Error en bot ML REAL: {e}")
                time.sleep(90)  # Esperar más en caso de error
        
        # Cleanup final
        if self.current_position:
            try:
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                self.close_real_position(current_price, "Bot detenido")
            except Exception as e:
                log_event(f"Error cerrando posición final: {e}")
        
        self.print_final_statistics()

if __name__ == "__main__":
    print("🚀 INICIANDO BOT ML REAL")
    print("⚠️  CONFIGURACIÓN: Trading real activado con claves de producción")
    print("⚠️  BALANCE CONFIGURADO: $10 USD (50% del total)")
    print("⚠️  CONFIGURACIÓN: Más conservadora para dinero real")
    print("⚠️  CONFIANZA MÍNIMA: 70% (vs 65% en simulación)")
    print()
    
    bot = RealMLBot()
    bot.run_real_ml_bot()