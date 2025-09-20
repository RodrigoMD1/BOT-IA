"""
Bot de Trading Mejorado para Binance (Versión Sin ML)
Versión simplificada con análisis técnico avanzado
"""

import datetime
import numpy as np
import pandas as pd
from binance.client import Client
import time

def log_event(text):
    with open("advanced_trading_log.txt", "a") as f:
        f.write(f"[{datetime.datetime.now()}] {text}\n")

# Configuración de claves API de Binance
API_KEY = 'ZJ0QB5V5ijovNtHvtVLMdgoxqZS3B521YcoeosI6Po7Ea9INmvc8vIOXY2DUX3Zm'
API_SECRET = 'YWmFXL8aTD6tcD7XTdmCdpBKv30p6bHqzUjktigc95ydTfKDUsAySTUVIJmNRaUo'

# Parámetros de trading mejorados
SYMBOL = 'SHIBUSDT'
INTERVAL = '1m'
QUANTITY = 0.001
INITIAL_BALANCE = 100.0

# Parámetros de gestión de riesgo inteligente
DYNAMIC_STOP_LOSS = True
BASE_STOP_LOSS = 0.005  # 0.5%
BASE_TAKE_PROFIT = 0.015  # 1.5%
MAX_POSITION_SIZE = 0.3  # Máximo 30% del balance

client = Client(API_KEY, API_SECRET)

class AdvancedTradingBot:
    def __init__(self):
        self.balance = INITIAL_BALANCE
        self.current_position = None
        self.total_trades = 0
        self.winning_trades = 0
        self.total_profit = 0.0
        
    def get_extended_klines(self, symbol, interval, limit=200):
        """Obtiene datos históricos extendidos"""
        try:
            klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'count', 'taker_buy_volume',
                'taker_buy_quote_volume', 'ignore'
            ])
            
            # Convertir a tipos numéricos
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
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
        
        # Volatilidad
        df['volatility'] = df['close'].rolling(window=10).std() / df['close'].rolling(window=10).mean()
        
        # Volume indicators
        df['volume_ma'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        
        return df
    
    def advanced_trading_signal(self):
        """Genera señales de trading usando múltiples indicadores"""
        df = self.get_extended_klines(SYMBOL, INTERVAL, limit=50)
        if df is None:
            return 0, 0  # Sin señal
        
        df = self.calculate_technical_indicators(df)
        
        # Obtener últimos valores
        current_price = df['close'].iloc[-1]
        ma_5 = df['ma_5'].iloc[-1]
        ma_10 = df['ma_10'].iloc[-1]
        ma_20 = df['ma_20'].iloc[-1]
        rsi = df['rsi'].iloc[-1]
        macd = df['macd'].iloc[-1]
        macd_signal = df['macd_signal'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        volume_ratio = df['volume_ratio'].iloc[-1]
        
        # Sistema de puntuación
        buy_score = 0
        sell_score = 0
        
        # Señales de medias móviles
        if ma_5 > ma_10 > ma_20:
            buy_score += 2
        elif ma_5 < ma_10 < ma_20:
            sell_score += 2
        
        # Señales RSI
        if rsi < 30:  # Sobreventa
            buy_score += 3
        elif rsi > 70:  # Sobrecompra
            sell_score += 3
        elif 30 <= rsi <= 50:
            buy_score += 1
        elif 50 <= rsi <= 70:
            sell_score += 1
        
        # Señales MACD
        if macd > macd_signal and macd > 0:
            buy_score += 2
        elif macd < macd_signal and macd < 0:
            sell_score += 2
        
        # Señales Bollinger Bands
        if current_price <= bb_lower:
            buy_score += 2
        elif current_price >= bb_upper:
            sell_score += 2
        
        # Señales de volumen
        if volume_ratio > 1.5:  # Alto volumen
            if buy_score > sell_score:
                buy_score += 1
            else:
                sell_score += 1
        
        # Calcular confianza
        total_score = buy_score + sell_score
        if total_score > 0:
            confidence = max(buy_score, sell_score) / total_score
        else:
            confidence = 0
        
        print(f"📊 Análisis técnico:")
        print(f"   RSI: {rsi:.2f}")
        print(f"   MACD: {macd:.6f} vs Signal: {macd_signal:.6f}")
        print(f"   BB: {bb_lower:.6f} < {current_price:.6f} < {bb_upper:.6f}")
        print(f"   MA: {ma_5:.6f} > {ma_10:.6f} > {ma_20:.6f}")
        print(f"   Volumen ratio: {volume_ratio:.2f}")
        print(f"   Buy Score: {buy_score}, Sell Score: {sell_score}")
        print(f"   Confianza: {confidence:.2f}")
        
        # Retornar señal
        if buy_score > sell_score and confidence > 0.6:
            return 1, confidence  # Señal de compra
        elif sell_score > buy_score and confidence > 0.6:
            return -1, confidence  # Señal de venta
        else:
            return 0, confidence  # Sin señal clara
    
    def calculate_dynamic_risk_params(self, current_price):
        """Calcula parámetros de riesgo dinámicos"""
        df = self.get_extended_klines(SYMBOL, INTERVAL, limit=50)
        if df is None:
            return BASE_STOP_LOSS, BASE_TAKE_PROFIT
        
        # Calcular volatilidad
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()
        
        # Ajustar parámetros basado en volatilidad
        dynamic_stop = BASE_STOP_LOSS * (1 + volatility * 10)
        dynamic_take_profit = BASE_TAKE_PROFIT * (1 + volatility * 5)
        
        # Limitar rangos
        dynamic_stop = min(dynamic_stop, 0.02)  # Máximo 2%
        dynamic_take_profit = max(dynamic_take_profit, 0.01)  # Mínimo 1%
        
        return dynamic_stop, dynamic_take_profit
    
    def execute_trade_decision(self, signal, confidence, current_price):
        """Ejecuta decisiones de trading"""
        stop_loss_pct, take_profit_pct = self.calculate_dynamic_risk_params(current_price)
        
        # Señal de compra
        if signal == 1 and not self.current_position:
            position_size = min(QUANTITY, self.balance * MAX_POSITION_SIZE / current_price)
            
            print(f"🟢 SEÑAL DE COMPRA AVANZADA")
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
            
            log_event(f"COMPRA AVANZADA - Precio: {current_price}, Confianza: {confidence:.2f}")
            
        # Señal de venta
        elif signal == -1 and self.current_position and self.current_position['type'] == 'LONG':
            self.close_position(current_price, "Señal avanzada de venta")
            
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
                
            # Trailing Stop
            elif current_price > position['entry_price'] * 1.01:
                new_stop = current_price * 0.995
                if new_stop > position['stop_loss']:
                    position['stop_loss'] = new_stop
                    print(f"🔄 Trailing Stop: {new_stop:.6f}")
    
    def close_position(self, current_price, reason):
        """Cierra una posición"""
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
            print(f"🔴 VENTA CON PÉRDIDA - {reason}")
        
        print(f"   P&L: {profit_loss:.6f} USDT ({profit_pct:+.2f}%)")
        print(f"   Balance: {self.balance:.2f} USDT")
        
        log_event(f"VENTA - {reason} - P&L: {profit_loss:.6f}")
        self.current_position = None
    
    def print_statistics(self):
        """Imprime estadísticas"""
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            avg_profit = self.total_profit / self.total_trades
        else:
            win_rate = 0
            avg_profit = 0
        
        print(f"\n📊 ESTADÍSTICAS AVANZADAS:")
        print(f"   Balance inicial: {INITIAL_BALANCE:.2f} USDT")
        print(f"   Balance actual: {self.balance:.2f} USDT")
        print(f"   Ganancia total: {self.total_profit:.6f} USDT ({((self.balance/INITIAL_BALANCE-1)*100):+.2f}%)")
        print(f"   Trades totales: {self.total_trades}")
        print(f"   Tasa de éxito: {win_rate:.1f}%")
        print(f"   Ganancia promedio: {avg_profit:.6f} USDT")
    
    def run_advanced_bot(self):
        """Ejecuta el bot avanzado"""
        print("🚀 Bot de Trading Avanzado Iniciado")
        print(f"💰 Balance inicial: {self.balance:.2f} USDT")
        print(f"🎯 Par: {SYMBOL}")
        
        log_event("Bot avanzado iniciado")
        iteration = 0
        
        while True:
            try:
                iteration += 1
                
                # Obtener precio actual
                ticker = client.get_symbol_ticker(symbol=SYMBOL)
                current_price = float(ticker['price'])
                
                # Generar señal de trading
                signal, confidence = self.advanced_trading_signal()
                
                print(f"\n--- Iteración {iteration} ---")
                print(f"💲 Precio actual: {current_price:.6f}")
                
                if signal == 1:
                    print(f"🟢 SEÑAL: COMPRA (Confianza: {confidence:.2f})")
                elif signal == -1:
                    print(f"🔴 SEÑAL: VENTA (Confianza: {confidence:.2f})")
                else:
                    print(f"⚪ SEÑAL: MANTENER (Confianza: {confidence:.2f})")
                
                if self.current_position:
                    print(f"📍 Posición: {self.current_position['type']} desde {self.current_position['entry_price']:.6f}")
                
                # Ejecutar decisión
                self.execute_trade_decision(signal, confidence, current_price)
                
                # Estadísticas cada 10 iteraciones
                if iteration % 10 == 0:
                    self.print_statistics()
                
                time.sleep(30)
                
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
        log_event("Bot avanzado detenido")

if __name__ == "__main__":
    bot = AdvancedTradingBot()
    bot.run_advanced_bot()