"""
Bot de Trading con Machine Learning Simplificado para Binance
Versión compatible sin dependencias problemáticas
Usa algoritmos propios para predicción de precios
"""

import datetime
import numpy as np
import pandas as pd
from binance.client import Client
import time
import warnings
warnings.filterwarnings('ignore')

def log_event(text):
    with open("simple_ml_trading_log.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")

# Configuración de claves API de Binance
API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'

# Parámetros de trading
SYMBOL = 'SHIBUSDT'
INTERVAL = '1m'
QUANTITY = 0.001
INITIAL_BALANCE = 100.0

# Parámetros de ML simplificado
LOOKBACK_PERIOD = 30
MIN_CONFIDENCE = 0.65

# Parámetros de gestión de riesgo
BASE_STOP_LOSS = 0.005
BASE_TAKE_PROFIT = 0.015
MAX_POSITION_SIZE = 0.3

client = Client(API_KEY, API_SECRET)

class SimplifiedMLBot:
    def __init__(self):
        self.historical_prices = []
        self.historical_volumes = []
        self.predictions_history = []
        self.balance = INITIAL_BALANCE
        self.current_position = None
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        
    def get_market_data(self, symbol, interval, limit=100):
        """Obtiene datos del mercado"""
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
            log_event(f"Error obteniendo datos: {e}")
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
    
    def simple_ml_prediction(self):
        """Algoritmo ML simplificado propio"""
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
        rsi = latest_data['rsi']
        macd = latest_data['macd']
        macd_signal = latest_data['macd_signal']
        bb_position = latest_data['bb_position']
        momentum = latest_data['momentum']
        volume_ratio = latest_data['volume_ratio']
        
        # Algoritmo ML simplificado (Weighted Score Prediction)
        prediction_score = 0
        confidence_factors = []
        
        # Factor 1: Tendencia de medias móviles (peso: 25%)
        if ma_5 > ma_10:
            ma_trend = (ma_5 - ma_10) / ma_10
            prediction_score += ma_trend * 0.25
            confidence_factors.append(abs(ma_trend))
        
        # Factor 2: RSI momentum (peso: 20%)
        if 30 <= rsi <= 70:  # Zona normal
            rsi_factor = (rsi - 50) / 50  # Normalizar entre -1 y 1
            prediction_score += rsi_factor * 0.20
            confidence_factors.append(abs(rsi_factor))
        elif rsi < 30:  # Sobreventa
            prediction_score += 0.15
            confidence_factors.append(0.8)
        elif rsi > 70:  # Sobrecompra
            prediction_score -= 0.15
            confidence_factors.append(0.8)
        
        # Factor 3: MACD signal (peso: 20%)
        if not np.isnan(macd) and not np.isnan(macd_signal):
            macd_diff = macd - macd_signal
            macd_factor = np.tanh(macd_diff * 1000)  # Normalizar
            prediction_score += macd_factor * 0.20
            confidence_factors.append(abs(macd_factor))
        
        # Factor 4: Bollinger Bands position (peso: 15%)
        if not np.isnan(bb_position):
            if bb_position < 0.2:  # Cerca del límite inferior
                prediction_score += 0.10
                confidence_factors.append(0.7)
            elif bb_position > 0.8:  # Cerca del límite superior
                prediction_score -= 0.10
                confidence_factors.append(0.7)
            else:
                bb_factor = (bb_position - 0.5) * 0.15
                prediction_score += bb_factor
                confidence_factors.append(abs(bb_factor))
        
        # Factor 5: Momentum (peso: 10%)
        if not np.isnan(momentum):
            momentum_factor = np.tanh(momentum * 10)
            prediction_score += momentum_factor * 0.10
            confidence_factors.append(abs(momentum_factor))
        
        # Factor 6: Volume confirmation (peso: 10%)
        if not np.isnan(volume_ratio) and volume_ratio > 1:
            volume_factor = min(volume_ratio - 1, 1) * 0.10
            if prediction_score > 0:
                prediction_score += volume_factor
            else:
                prediction_score -= volume_factor
            confidence_factors.append(volume_factor)
        
        # Calcular confianza
        if confidence_factors:
            confidence = np.mean(confidence_factors)
            confidence = min(confidence * 2, 1.0)  # Amplificar pero limitar a 1
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
            'bb_position': bb_position
        })
        
        # Mantener solo últimas 50 predicciones
        if len(self.predictions_history) > 50:
            self.predictions_history.pop(0)
        
        return prediction_score, confidence
    
    def adaptive_risk_management(self, current_price):
        """Gestión de riesgo adaptativa"""
        df = self.get_market_data(SYMBOL, INTERVAL, limit=30)
        if df is None:
            return BASE_STOP_LOSS, BASE_TAKE_PROFIT
        
        # Calcular volatilidad reciente
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Ajustar parámetros
        dynamic_stop = BASE_STOP_LOSS * (1 + volatility * 8)
        dynamic_take_profit = BASE_TAKE_PROFIT * (1 + volatility * 4)
        
        # Limites
        dynamic_stop = max(0.003, min(dynamic_stop, 0.025))  # Entre 0.3% y 2.5%
        dynamic_take_profit = max(0.008, min(dynamic_take_profit, 0.04))  # Entre 0.8% y 4%
        
        return dynamic_stop, dynamic_take_profit
    
    def execute_ml_strategy(self, prediction, confidence, current_price):
        """Ejecuta estrategia basada en ML"""
        stop_loss_pct, take_profit_pct = self.adaptive_risk_management(current_price)
        
        # Señal de compra
        if prediction > 0.02 and confidence > MIN_CONFIDENCE and not self.current_position:
            position_size = min(QUANTITY, self.balance * MAX_POSITION_SIZE / current_price)
            
            print(f"🟢 COMPRA ML SIMPLIFICADA")
            print(f"   Predicción: +{prediction*100:.2f}%")
            print(f"   Confianza: {confidence*100:.1f}%")
            print(f"   Stop Loss: {stop_loss_pct*100:.2f}%")
            print(f"   Take Profit: {take_profit_pct*100:.2f}%")
            
            self.current_position = {
                'type': 'LONG',
                'entry_price': current_price,
                'quantity': position_size,
                'stop_loss': current_price * (1 - stop_loss_pct),
                'take_profit': current_price * (1 + take_profit_pct),
                'entry_time': datetime.datetime.now()
            }
            
            log_event(f"COMPRA ML - Precio: {current_price}, Predicción: {prediction:.4f}")
            
        # Señal de venta
        elif prediction < -0.02 and confidence > MIN_CONFIDENCE and self.current_position:
            self.close_position(current_price, "Señal ML de venta")
            
        # Gestión de posición
        elif self.current_position:
            self.manage_position(current_price)
    
    def manage_position(self, current_price):
        """Gestiona posición existente"""
        position = self.current_position
        
        if position['type'] == 'LONG':
            # Stop Loss
            if current_price <= position['stop_loss']:
                self.close_position(current_price, "Stop Loss")
                
            # Take Profit
            elif current_price >= position['take_profit']:
                self.close_position(current_price, "Take Profit")
                
            # Trailing Stop
            elif current_price > position['entry_price'] * 1.008:  # +0.8%
                new_stop = current_price * 0.996  # -0.4%
                if new_stop > position['stop_loss']:
                    position['stop_loss'] = new_stop
                    print(f"🔄 Trailing Stop: {new_stop:.6f}")
    
    def close_position(self, current_price, reason):
        """Cierra posición"""
        if not self.current_position:
            return
        
        position = self.current_position
        profit_loss = (current_price - position['entry_price']) * position['quantity']
        profit_pct = (current_price / position['entry_price'] - 1) * 100
        
        self.balance += profit_loss
        self.total_profit += profit_loss
        self.total_trades += 1
        
        if profit_loss > 0:
            self.winning_trades += 1
            print(f"🟢 VENTA EXITOSA - {reason}")
        else:
            print(f"🔴 PÉRDIDA - {reason}")
        
        print(f"   P&L: {profit_loss:.6f} USDT ({profit_pct:+.2f}%)")
        print(f"   Balance: {self.balance:.2f} USDT")
        
        log_event(f"VENTA - {reason} - P&L: {profit_loss:.6f}")
        self.current_position = None
    
    def print_ml_statistics(self):
        """Imprime estadísticas ML"""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        print(f"\n🤖 ESTADÍSTICAS ML SIMPLIFICADA:")
        print(f"   Balance: {self.balance:.2f} USDT")
        print(f"   ROI: {((self.balance/INITIAL_BALANCE-1)*100):+.2f}%")
        print(f"   Trades: {self.total_trades}")
        print(f"   Win Rate: {win_rate:.1f}%")
        print(f"   Predicciones guardadas: {len(self.predictions_history)}")
        
        if len(self.predictions_history) >= 5:
            recent_predictions = [p['prediction'] for p in self.predictions_history[-5:]]
            avg_prediction = np.mean(recent_predictions)
            print(f"   Tendencia ML: {avg_prediction:+.4f}")
    
    def run_simple_ml_bot(self):
        """Ejecuta bot ML simplificado"""
        print("🤖 Bot de Trading ML Simplificado Iniciado")
        print(f"💰 Balance: {self.balance:.2f} USDT")
        print(f"🎯 Par: {SYMBOL}")
        print(f"🧠 Algoritmo: ML Propio Simplificado")
        
        log_event("Bot ML simplificado iniciado")
        iteration = 0
        
        while True:
            try:
                iteration += 1
                
                # Precio actual
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                
                # Predicción ML
                prediction, confidence = self.simple_ml_prediction()
                
                if prediction is not None:
                    print(f"\n--- Iteración {iteration} ---")
                    print(f"💲 Precio: {current_price:.6f}")
                    print(f"🤖 Predicción ML: {prediction:+.4f}")
                    print(f"📊 Confianza: {confidence*100:.1f}%")
                    
                    if self.current_position:
                        print(f"📍 Posición: {self.current_position['type']} desde {self.current_position['entry_price']:.6f}")
                    
                    # Ejecutar estrategia
                    self.execute_ml_strategy(prediction, confidence, current_price)
                
                # Estadísticas cada 10 iteraciones
                if iteration % 10 == 0:
                    self.print_ml_statistics()
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot ML detenido")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                log_event(f"Error: {e}")
                time.sleep(10)
        
        # Cerrar posición si existe
        if self.current_position:
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            current_price = float(ticker['price'])
            self.close_position(current_price, "Bot detenido")
        
        self.print_ml_statistics()
        log_event("Bot ML simplificado detenido")

if __name__ == "__main__":
    bot = SimplifiedMLBot()
    bot.run_simple_ml_bot()