"""
Bot de Trading con Machine Learning para Binance
Versión mejorada que utiliza Random Forest para predecir precios
Incluye análisis técnico avanzado y gestión de riesgo inteligente
"""

import datetime
import numpy as np
import pandas as pd
from binance.client import Client
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def log_event(text):
    with open("ml_trading_log.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")

# Configuración de claves API de Binance
API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'

# Parámetros de trading mejorados
SYMBOL = 'SHIBUSDT'
INTERVAL = '1m'
QUANTITY = 0.001
INITIAL_BALANCE = 100.0  # Balance inicial en USDT para simulación

# Parámetros de Machine Learning
LOOKBACK_PERIOD = 50  # Número de velas históricas para entrenar
PREDICTION_HORIZON = 1  # Predecir 1 vela hacia adelante
MIN_CONFIDENCE = 0.65  # Confianza mínima para ejecutar trades

# Parámetros de gestión de riesgo inteligente
DYNAMIC_STOP_LOSS = True  # Stop loss dinámico basado en volatilidad
BASE_STOP_LOSS = 0.005  # 0.5% stop loss base
BASE_TAKE_PROFIT = 0.015  # 1.5% take profit base
MAX_POSITION_SIZE = 0.3  # Máximo 30% del balance en una posición

client = Client(API_KEY, API_SECRET)

class MLTradingBot:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.is_trained = False
        self.historical_data = []
        self.balance = INITIAL_BALANCE
        self.current_position = None
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        
    def get_extended_klines(self, symbol, interval, limit=200):
        """Obtiene datos históricos extendidos para ML"""
        try:
            klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            # Convertir a tipos numéricos
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'quote_volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])
                
            return df
        except Exception as e:
            log_event(f"Error obteniendo datos: {e}")
            return None
    
    def calculate_technical_indicators(self, df):
        """Calcula indicadores técnicos avanzados"""
        # Medias móviles
        df['ma_5'] = df['close'].rolling(window=5).mean()
        df['ma_10'] = df['close'].rolling(window=10).mean()
        df['ma_20'] = df['close'].rolling(window=20).mean()
        
        # RSI (Relative Strength Index)
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
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Volatilidad
        df['volatility'] = df['close'].rolling(window=10).std() / df['close'].rolling(window=10).mean()
        
        # Volume indicators
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        # Price momentum
        df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
        df['momentum_10'] = df['close'] / df['close'].shift(10) - 1
        
        return df
    
    def prepare_features(self, df):
        """Prepara las características para el modelo ML"""
        features = [
            'ma_5', 'ma_10', 'ma_20', 'rsi', 'macd', 'macd_signal', 'macd_histogram',
            'bb_position', 'volatility', 'volume_ratio', 'momentum_5', 'momentum_10'
        ]
        
        # Crear características adicionales (diferencias entre medias móviles)
        df['ma_diff_5_10'] = df['ma_5'] - df['ma_10']
        df['ma_diff_10_20'] = df['ma_10'] - df['ma_20']
        features.extend(['ma_diff_5_10', 'ma_diff_10_20'])
        
        return df[features].dropna()
    
    def create_target_variable(self, df):
        """Crea la variable objetivo (precio futuro)"""
        # Predecir el cambio porcentual en el próximo período
        df['future_return'] = (df['close'].shift(-PREDICTION_HORIZON) / df['close']) - 1
        return df['future_return'].dropna()
    
    def train_model(self):
        """Entrena el modelo de Machine Learning"""
        log_event("Iniciando entrenamiento del modelo ML...")
        print("🤖 Obteniendo datos históricos para entrenamiento...")
        
        # Obtener datos históricos
        df = self.get_extended_klines(SYMBOL, INTERVAL, limit=500)
        if df is None:
            return False
        
        # Calcular indicadores técnicos
        df = self.calculate_technical_indicators(df)
        
        # Preparar características y variable objetivo
        features = self.prepare_features(df)
        target = self.create_target_variable(df)
        
        # Alinear características y objetivo
        min_length = min(len(features), len(target))
        X = features.iloc[:min_length]
        y = target.iloc[:min_length]
        
        if len(X) < LOOKBACK_PERIOD:
            print("❌ No hay suficientes datos para entrenar el modelo")
            return False
        
        # Dividir en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Entrenar modelo
        self.model.fit(X_train, y_train)
        
        # Evaluar modelo
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"✅ Modelo entrenado exitosamente!")
        print(f"📊 MSE: {mse:.6f}")
        print(f"📊 MAE: {mae:.6f}")
        
        log_event(f"Modelo entrenado - MSE: {mse:.6f}, MAE: {mae:.6f}")
        
        # Mostrar importancia de características
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔍 Importancia de características:")
        for _, row in feature_importance.head(5).iterrows():
            print(f"  {row['feature']}: {row['importance']:.4f}")
        
        self.is_trained = True
        return True
    
    def predict_price_movement(self):
        """Predice el movimiento del precio usando ML"""
        if not self.is_trained:
            return None, 0
        
        # Obtener datos recientes
        df = self.get_extended_klines(SYMBOL, INTERVAL, limit=100)
        if df is None:
            return None, 0
        
        # Calcular indicadores técnicos
        df = self.calculate_technical_indicators(df)
        features = self.prepare_features(df)
        
        if len(features) == 0:
            return None, 0
        
        # Predecir
        latest_features = features.iloc[-1:].values
        prediction = self.model.predict(latest_features)[0]
        
        # Calcular confianza basada en la consistencia de predicciones recientes
        recent_predictions = []
        for i in range(min(5, len(features))):
            pred = self.model.predict(features.iloc[-(i+1):-(i)].values)[0]
            recent_predictions.append(pred)
        
        confidence = 1 - (np.std(recent_predictions) / (np.mean(np.abs(recent_predictions)) + 1e-6))
        confidence = max(0, min(1, confidence))
        
        return prediction, confidence
    
    def calculate_dynamic_risk_params(self, current_price):
        """Calcula parámetros de riesgo dinámicos basados en volatilidad"""
        df = self.get_extended_klines(SYMBOL, INTERVAL, limit=50)
        if df is None:
            return BASE_STOP_LOSS, BASE_TAKE_PROFIT
        
        # Calcular volatilidad histórica
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Ajustar stop loss y take profit basado en volatilidad
        dynamic_stop = BASE_STOP_LOSS * (1 + volatility * 10)
        dynamic_take_profit = BASE_TAKE_PROFIT * (1 + volatility * 5)
        
        # Limitar rangos
        dynamic_stop = min(dynamic_stop, 0.02)  # Máximo 2%
        dynamic_take_profit = max(dynamic_take_profit, 0.01)  # Mínimo 1%
        
        return dynamic_stop, dynamic_take_profit
    
    def execute_trade_decision(self, prediction, confidence, current_price):
        """Ejecuta decisiones de trading basadas en ML"""
        # Calcular parámetros de riesgo dinámicos
        stop_loss_pct, take_profit_pct = self.calculate_dynamic_risk_params(current_price)
        
        # Decisión de compra
        if prediction > 0.005 and confidence > MIN_CONFIDENCE and not self.current_position:
            position_size = min(QUANTITY, self.balance * MAX_POSITION_SIZE / current_price)
            
            print(f"🟢 SEÑAL DE COMPRA ML")
            print(f"   Predicción: +{prediction*100:.3f}%")
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
            
            log_event(f"COMPRA ML - Precio: {current_price}, Predicción: {prediction:.4f}, Confianza: {confidence:.2f}")
            
        # Decisión de venta
        elif prediction < -0.005 and confidence > MIN_CONFIDENCE and self.current_position and self.current_position['type'] == 'LONG':
            self.close_position(current_price, "Señal ML de venta")
            
        # Gestión de posición existente
        elif self.current_position:
            self.manage_existing_position(current_price)
    
    def manage_existing_position(self, current_price):
        """Gestiona posiciones existentes"""
        position = self.current_position
        
        if position['type'] == 'LONG':
            # Stop Loss
            if current_price <= position['stop_loss']:
                self.close_position(current_price, "Stop Loss activado")
                
            # Take Profit
            elif current_price >= position['take_profit']:
                self.close_position(current_price, "Take Profit activado")
                
            # Trailing Stop (opcional)
            elif current_price > position['entry_price'] * 1.01:  # Si hay ganancia > 1%
                new_stop = current_price * 0.995  # Trailing stop del 0.5%
                if new_stop > position['stop_loss']:
                    position['stop_loss'] = new_stop
                    print(f"🔄 Trailing Stop actualizado: {new_stop:.6f}")
    
    def close_position(self, current_price, reason):
        """Cierra una posición y calcula P&L"""
        if not self.current_position:
            return
        
        position = self.current_position
        
        if position['type'] == 'LONG':
            profit_loss = (current_price - position['entry_price']) * position['quantity']
            profit_pct = (current_price / position['entry_price'] - 1) * 100
        
        self.balance += profit_loss
        self.total_profit += profit_loss
        self.total_trades += 1
        
        if profit_loss > 0:
            self.winning_trades += 1
            print(f"🟢 VENTA EXITOSA - {reason}")
        else:
            print(f"🔴 VENTA CON PÉRDIDA - {reason}")
        
        print(f"   P&L: {profit_loss:.6f} USDT ({profit_pct:+.2f}%)")
        print(f"   Balance: {self.balance:.2f} USDT")
        
        log_event(f"VENTA - {reason} - P&L: {profit_loss:.6f} USDT, Balance: {self.balance:.2f}")
        
        self.current_position = None
    
    def print_statistics(self):
        """Imprime estadísticas del bot"""
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            avg_profit = self.total_profit / self.total_trades
        else:
            win_rate = 0
            avg_profit = 0
        
        print(f"\n📊 ESTADÍSTICAS DEL BOT ML:")
        print(f"   Balance inicial: {INITIAL_BALANCE:.2f} USDT")
        print(f"   Balance actual: {self.balance:.2f} USDT")
        print(f"   Ganancia total: {self.total_profit:.6f} USDT ({((self.balance/INITIAL_BALANCE-1)*100):+.2f}%)")
        print(f"   Trades totales: {self.total_trades}")
        print(f"   Trades ganadores: {self.winning_trades}")
        print(f"   Tasa de éxito: {win_rate:.1f}%")
        print(f"   Ganancia promedio: {avg_profit:.6f} USDT")
    
    def run_ml_bot(self):
        """Ejecuta el bot principal con ML"""
        print("🚀 Iniciando Bot de Trading con Machine Learning")
        print(f"💰 Balance inicial: {self.balance:.2f} USDT")
        print(f"🎯 Par de trading: {SYMBOL}")
        
        # Entrenar modelo
        if not self.train_model():
            print("❌ Error al entrenar el modelo. Abortando...")
            return
        
        print("\n🔄 Iniciando trading en vivo...")
        log_event("Bot ML iniciado")
        
        iteration = 0
        while True:
            try:
                iteration += 1
                
                # Obtener precio actual
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                
                # Hacer predicción ML
                prediction, confidence = self.predict_price_movement()
                
                if prediction is not None:
                    print(f"\n--- Iteración {iteration} ---")
                    print(f"💲 Precio actual: {current_price:.6f}")
                    print(f"🤖 Predicción ML: {prediction*100:+.3f}%")
                    print(f"📈 Confianza: {confidence*100:.1f}%")
                    
                    if self.current_position:
                        print(f"📍 Posición activa: {self.current_position['type']} desde {self.current_position['entry_price']:.6f}")
                    
                    # Ejecutar decisión de trading
                    self.execute_trade_decision(prediction, confidence, current_price)
                
                # Mostrar estadísticas cada 10 iteraciones
                if iteration % 10 == 0:
                    self.print_statistics()
                
                time.sleep(30)  # Esperar 30 segundos
                
            except KeyboardInterrupt:
                print("\n🛑 Bot detenido por el usuario")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                log_event(f"Error: {e}")
                time.sleep(10)
        
        # Cerrar posición si está abierta
        if self.current_position:
            ticker = client.get_symbol_ticker(symbol=SYMBOL)
            current_price = float(ticker['price'])
            self.close_position(current_price, "Bot detenido")
        
        self.print_statistics()
        log_event("Bot ML detenido")

if __name__ == "__main__":
    # Crear y ejecutar bot
    ml_bot = MLTradingBot()
    ml_bot.run_ml_bot()
