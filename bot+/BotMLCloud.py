"""
Bot de Trading con Machine Learning Simplificado para Binance - Versión Cloud
Optimizado para ejecución 24/7 en Google Cloud VM
Usa algoritmos propios para predicción de precios sin dependencias problemáticas
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

def log_event(text, log_file="ml_btc_trading_log.txt"):
    """Log con timestamp y identificación ML"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] [ML-BOT] {text}\n")
    print(f"[{timestamp}] [ML-BOT] {text}")

# Configuración de claves API de Binance
API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'

# Parámetros de trading
SYMBOL = 'BTCUSDT'  # Bitcoin/USDT para ML
INTERVAL = '1m'
QUANTITY = 0.0001   # 0.0001 BTC = ~$6-7 USD por trade
INITIAL_BALANCE = 100.0

# Parámetros de ML simplificado
LOOKBACK_PERIOD = 30
MIN_CONFIDENCE = 0.65

# Parámetros de gestión de riesgo para BTC
BASE_STOP_LOSS = 0.003      # 0.3% stop loss (más conservador para BTC)
BASE_TAKE_PROFIT = 0.008    # 0.8% take profit (ajustado para BTC)
MAX_POSITION_SIZE = 0.3

client = Client(API_KEY, API_SECRET)

class CloudMLBot:
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
        log_event("Bot ML recibió señal de cierre, cerrando posiciones...")
        if self.current_position:
            try:
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                self.close_position(current_price, "Bot detenido - shutdown")
            except Exception as e:
                log_event(f"Error cerrando posición en shutdown: {e}")
        
        self.print_final_statistics()
        log_event("Bot ML Cloud detenido limpiamente")
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
        """Algoritmo ML simplificado mejorado"""
        df = self.get_market_data(SYMBOL, INTERVAL, limit=60)
        if df is None:
            return None, 0
        
        df = self.calculate_advanced_features(df)
        
        # Obtener últimos valores
        latest_data = df.iloc[-1]
        prev_data = df.iloc[-2] if len(df) > 1 else latest_data
        
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
        
        # Algoritmo ML mejorado con más factores
        prediction_score = 0
        confidence_factors = []
        
        # Factor 1: Convergencia de medias móviles (peso: 25%)
        if not np.isnan(ma_5) and not np.isnan(ma_10) and not np.isnan(ma_20):
            # Tendencia alcista: MA5 > MA10 > MA20
            if ma_5 > ma_10 > ma_20:
                ma_strength = (ma_5 - ma_20) / ma_20
                prediction_score += ma_strength * 0.25
                confidence_factors.append(min(ma_strength * 5, 1))
            # Tendencia bajista: MA5 < MA10 < MA20
            elif ma_5 < ma_10 < ma_20:
                ma_weakness = (ma_20 - ma_5) / ma_20
                prediction_score -= ma_weakness * 0.25
                confidence_factors.append(min(ma_weakness * 5, 1))
        
        # Factor 2: RSI con zonas mejoradas (peso: 20%)
        if not np.isnan(rsi):
            if rsi < 25:  # Sobreventa extrema
                prediction_score += 0.20
                confidence_factors.append(0.9)
            elif rsi < 35:  # Sobreventa
                prediction_score += 0.15
                confidence_factors.append(0.7)
            elif rsi > 75:  # Sobrecompra extrema
                prediction_score -= 0.20
                confidence_factors.append(0.9)
            elif rsi > 65:  # Sobrecompra
                prediction_score -= 0.15
                confidence_factors.append(0.7)
            else:  # Zona neutral
                rsi_factor = (rsi - 50) / 50
                prediction_score += rsi_factor * 0.10
                confidence_factors.append(abs(rsi_factor) * 0.5)
        
        # Factor 3: MACD con divergencia (peso: 20%)
        if not np.isnan(macd) and not np.isnan(macd_signal):
            macd_diff = macd - macd_signal
            if macd > 0 and macd_diff > 0:  # Señal alcista fuerte
                prediction_score += 0.15
                confidence_factors.append(0.8)
            elif macd < 0 and macd_diff < 0:  # Señal bajista fuerte
                prediction_score -= 0.15
                confidence_factors.append(0.8)
            else:
                macd_factor = np.tanh(macd_diff * 1000)
                prediction_score += macd_factor * 0.10
                confidence_factors.append(abs(macd_factor) * 0.6)
        
        # Factor 4: Bollinger Bands con squeeze detection (peso: 15%)
        if not np.isnan(bb_position):
            bb_width = (latest_data['bb_upper'] - latest_data['bb_lower']) / latest_data['bb_middle']
            
            if bb_width < 0.02:  # Bollinger Squeeze
                if bb_position < 0.3:
                    prediction_score += 0.12  # Probable breakout alcista
                    confidence_factors.append(0.75)
                elif bb_position > 0.7:
                    prediction_score -= 0.12  # Probable breakout bajista
                    confidence_factors.append(0.75)
            else:
                if bb_position < 0.15:  # Cerca del límite inferior
                    prediction_score += 0.10
                    confidence_factors.append(0.7)
                elif bb_position > 0.85:  # Cerca del límite superior
                    prediction_score -= 0.10
                    confidence_factors.append(0.7)
        
        # Factor 5: Momentum con aceleración (peso: 10%)
        if not np.isnan(momentum):
            momentum_factor = np.tanh(momentum * 10)
            prediction_score += momentum_factor * 0.10
            confidence_factors.append(abs(momentum_factor) * 0.8)
        
        # Factor 6: Volume confirmation mejorado (peso: 10%)
        if not np.isnan(volume_ratio):
            if volume_ratio > 1.5:  # Volumen alto
                volume_strength = min((volume_ratio - 1) / 2, 1)
                if prediction_score > 0:
                    prediction_score += volume_strength * 0.08
                else:
                    prediction_score -= volume_strength * 0.08
                confidence_factors.append(volume_strength)
            elif volume_ratio < 0.5:  # Volumen muy bajo
                confidence_factors.append(0.3)  # Reduce confianza
        
        # Calcular confianza final
        if confidence_factors:
            base_confidence = np.mean(confidence_factors)
            consistency = 1 - np.std(confidence_factors)  # Más consistencia = más confianza
            confidence = min(base_confidence * consistency * 1.5, 1.0)
        else:
            confidence = 0
        
        # Guardar en historial para análisis
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
        
        # Mantener solo últimas 100 predicciones
        if len(self.predictions_history) > 100:
            self.predictions_history.pop(0)
        
        return prediction_score, confidence
    
    def adaptive_risk_management(self, current_price):
        """Gestión de riesgo adaptativa mejorada"""
        df = self.get_market_data(SYMBOL, INTERVAL, limit=50)
        if df is None:
            return BASE_STOP_LOSS, BASE_TAKE_PROFIT
        
        # Calcular volatilidad usando múltiples métodos
        returns = df['close'].pct_change().dropna()
        volatility_std = returns.std()
        volatility_range = (df['high'] - df['low']).mean() / df['close'].mean()
        
        # Volatilidad combinada
        combined_volatility = (volatility_std + volatility_range) / 2
        
        # Ajustar parámetros basado en volatilidad y tiempo en posición
        volatility_multiplier = 1 + (combined_volatility * 8)
        
        dynamic_stop = BASE_STOP_LOSS * volatility_multiplier
        dynamic_take_profit = BASE_TAKE_PROFIT * (1 + combined_volatility * 4)
        
        # Límites adaptativos
        dynamic_stop = max(0.003, min(dynamic_stop, 0.03))
        dynamic_take_profit = max(0.008, min(dynamic_take_profit, 0.05))
        
        return dynamic_stop, dynamic_take_profit
    
    def execute_ml_strategy(self, prediction, confidence, current_price):
        """Ejecuta estrategia ML con lógica mejorada"""
        stop_loss_pct, take_profit_pct = self.adaptive_risk_management(current_price)
        
        # Umbral dinámico basado en volatilidad
        df = self.get_market_data(SYMBOL, INTERVAL, limit=20)
        if df is not None:
            recent_volatility = df['close'].pct_change().std()
            prediction_threshold = max(0.015, min(0.025, recent_volatility * 100))
        else:
            prediction_threshold = 0.02
        
        # Señal de compra con confianza alta
        if prediction > prediction_threshold and confidence > MIN_CONFIDENCE and not self.current_position:
            position_size = min(QUANTITY, self.balance * MAX_POSITION_SIZE / current_price)
            
            log_event(f"🟢 COMPRA ML BTC - Pred: +{prediction*100:.2f}% | Conf: {confidence*100:.1f}% | Precio: ${current_price:.2f}")
            log_event(f"   📊 SL: ${current_price * (1 - stop_loss_pct):.2f} | TP: ${current_price * (1 + take_profit_pct):.2f}")
            
            self.current_position = {
                'type': 'LONG',
                'entry_price': current_price,
                'quantity': position_size,
                'stop_loss': current_price * (1 - stop_loss_pct),
                'take_profit': current_price * (1 + take_profit_pct),
                'entry_time': datetime.datetime.now(),
                'prediction': prediction,
                'confidence': confidence
            }
            
        # Señal de venta
        elif prediction < -prediction_threshold and confidence > MIN_CONFIDENCE and self.current_position:
            log_event(f"🔴 Señal ML de venta BTC - Pred: {prediction*100:.2f}% | Conf: {confidence*100:.1f}%")
            self.close_position(current_price, "Señal ML de venta")
            
        # Gestión de posición
        elif self.current_position:
            self.manage_position(current_price)
    
    def manage_position(self, current_price):
        """Gestiona posición con trailing stop mejorado"""
        position = self.current_position
        
        if position['type'] == 'LONG':
            time_in_position = datetime.datetime.now() - position['entry_time']
            hours_in_position = time_in_position.total_seconds() / 3600
            
            # Stop Loss
            if current_price <= position['stop_loss']:
                self.close_position(current_price, "Stop Loss")
                
            # Take Profit
            elif current_price >= position['take_profit']:
                self.close_position(current_price, "Take Profit")
                
            # Trailing Stop dinámico
            elif current_price > position['entry_price'] * 1.005:  # +0.5%
                trailing_pct = 0.004 if hours_in_position < 1 else 0.003  # Más conservador con el tiempo
                new_stop = current_price * (1 - trailing_pct)
                if new_stop > position['stop_loss']:
                    position['stop_loss'] = new_stop
                    log_event(f"🔄 Trailing Stop actualizado: {new_stop:.6f}")
            
            # Stop Loss por tiempo (24 horas máximo)
            elif hours_in_position > 24:
                log_event(f"⏰ Cerrando posición por tiempo límite (24h)")
                self.close_position(current_price, "Tiempo límite")
    
    def close_position(self, current_price, reason):
        """Cierra posición con logging detallado"""
        if not self.current_position:
            return
        
        position = self.current_position
        profit_loss = (current_price - position['entry_price']) * position['quantity']
        profit_pct = (current_price / position['entry_price'] - 1) * 100
        time_in_position = datetime.datetime.now() - position['entry_time']
        
        self.balance += profit_loss
        self.total_profit += profit_loss
        self.total_trades += 1
        
        if profit_loss > 0:
            self.winning_trades += 1
            log_event(f"✅ VENTA EXITOSA BTC - {reason} | P&L: +${profit_loss:.2f} USD (+{profit_pct:.2f}%) | Tiempo: {time_in_position}")
        else:
            log_event(f"❌ PÉRDIDA BTC - {reason} | P&L: ${profit_loss:.2f} USD ({profit_pct:.2f}%) | Tiempo: {time_in_position}")
        
        log_event(f"💰 Balance actualizado: ${self.balance:.2f} USD | Predicción original: {position.get('prediction', 0)*100:.2f}%")
        
        self.current_position = None
    
    def print_periodic_statistics(self):
        """Imprime estadísticas periódicas"""
        runtime = datetime.datetime.now() - self.start_time
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        roi = ((self.balance / INITIAL_BALANCE - 1) * 100)
        
        log_event(f"📊 [ESTADÍSTICAS ML] Runtime: {runtime} | Balance: {self.balance:.2f} USDT | ROI: {roi:+.2f}% | Trades: {self.total_trades} | Win Rate: {win_rate:.1f}%")
        
        if len(self.predictions_history) >= 10:
            recent_predictions = [p['prediction'] for p in self.predictions_history[-10:]]
            recent_confidence = [p['confidence'] for p in self.predictions_history[-10:]]
            avg_prediction = np.mean(recent_predictions)
            avg_confidence = np.mean(recent_confidence)
            log_event(f"🧠 [ML STATS] Tendencia promedio: {avg_prediction:+.4f} | Confianza promedio: {avg_confidence*100:.1f}%")
    
    def print_final_statistics(self):
        """Imprime estadísticas finales"""
        runtime = datetime.datetime.now() - self.start_time
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        roi = ((self.balance / INITIAL_BALANCE - 1) * 100)
        
        log_event("=" * 60)
        log_event("🤖 ESTADÍSTICAS FINALES DEL BOT ML")
        log_event("=" * 60)
        log_event(f"⏱️  Tiempo de ejecución: {runtime}")
        log_event(f"💰 Balance inicial: {INITIAL_BALANCE:.2f} USDT")
        log_event(f"💰 Balance final: {self.balance:.2f} USDT")
        log_event(f"📈 ROI total: {roi:+.2f}%")
        log_event(f"🔄 Trades ejecutados: {self.total_trades}")
        log_event(f"✅ Trades ganadores: {self.winning_trades}")
        log_event(f"📊 Tasa de éxito: {win_rate:.1f}%")
        if self.total_trades > 0:
            log_event(f"💵 Ganancia promedio por trade: {self.total_profit/self.total_trades:.6f} USDT")
        log_event(f"🧠 Predicciones generadas: {len(self.predictions_history)}")
        log_event("=" * 60)
    
    def heartbeat(self):
        """Envía heartbeat cada hora"""
        now = datetime.datetime.now()
        if (now - self.last_heartbeat).total_seconds() > 3600:  # 1 hora
            self.last_heartbeat = now
            runtime = now - self.start_time
            log_event(f"💓 [HEARTBEAT] Bot ML ejecutándose hace {runtime} | Balance: {self.balance:.2f} USDT")
    
    def run_cloud_ml_bot(self):
        """Ejecuta bot ML optimizado para cloud"""
        log_event("🚀 Iniciando Bot ML BTC en Google Cloud")
        log_event(f"💰 Balance inicial: ${self.balance:.2f} USD")
        log_event(f"🎯 Par de trading: {SYMBOL}")
        log_event(f"₿ Cantidad por trade: {QUANTITY} BTC (~${QUANTITY * 65000:.2f} USD aprox)")
        log_event(f"🧠 Confianza mínima: {MIN_CONFIDENCE*100}%")
        log_event(f"🛡️  Stop Loss base: {BASE_STOP_LOSS*100}%")
        log_event(f"🎯 Take Profit base: {BASE_TAKE_PROFIT*100}%")
        
        iteration = 0
        
        while True:
            try:
                iteration += 1
                
                # Heartbeat periódico
                self.heartbeat()
                
                # Obtener precio actual
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                
                # Generar predicción ML
                prediction, confidence = self.enhanced_ml_prediction()
                
                if prediction is not None:
                    # Log cada 10 iteraciones o si hay alta confianza
                    if iteration % 10 == 0 or confidence > 0.4:
                        log_event(f"[{iteration}] Precio BTC: ${current_price:.2f} | Pred: {prediction:+.4f} | Conf: {confidence*100:.1f}%")
                    
                    if self.current_position:
                        time_in_pos = datetime.datetime.now() - self.current_position['entry_time']
                        if iteration % 20 == 0:  # Log posición cada 20 iteraciones
                            log_event(f"📍 Posición BTC activa: {self.current_position['type']} desde ${self.current_position['entry_price']:.2f} | Tiempo: {time_in_pos}")
                    
                    # Ejecutar estrategia ML
                    self.execute_ml_strategy(prediction, confidence, current_price)
                
                # Estadísticas cada 100 iteraciones (50 minutos aprox)
                if iteration % 100 == 0:
                    self.print_periodic_statistics()
                
                # Esperar 30 segundos
                time.sleep(30)
                
            except KeyboardInterrupt:
                log_event("🛑 Bot ML detenido manualmente")
                break
            except Exception as e:
                log_event(f"❌ Error en bot ML: {e}")
                time.sleep(60)  # Esperar más tiempo en caso de error
        
        # Cleanup final
        if self.current_position:
            try:
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                self.close_position(current_price, "Bot detenido")
            except Exception as e:
                log_event(f"Error cerrando posición final: {e}")
        
        self.print_final_statistics()

if __name__ == "__main__":
    bot = CloudMLBot()
    bot.run_cloud_ml_bot()