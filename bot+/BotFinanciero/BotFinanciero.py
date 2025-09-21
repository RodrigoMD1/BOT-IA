#!/usr/bin/env python3
"""
Bot Financiero con Telegram - Trading de Acciones con ML y Notificaciones
Desarrollado por: RodrigoMD1
Fecha: 21 de septiembre de 2025

Funcionalidades:
- Análisis técnico de acciones populares
- Predicciones ML con múltiples indicadores
- Notificaciones automáticas vía Telegram
- Trading optimizado para horarios de mercado
- Gestión avanzada de riesgo
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
import time
import json
import logging
import warnings
from datetime import datetime, timedelta
import pytz
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import threading
import sys
import os

# Configuración para evitar warnings
warnings.filterwarnings('ignore')

# Importar configuración
try:
    from config_financiero import *
except ImportError:
    # Configuración por defecto si no existe el archivo de config
    TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    CHAT_ID = "YOUR_CHAT_ID_HERE"
    SYMBOLS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN']
    BALANCE_PER_STOCK = 1000
    STOP_LOSS_PERCENT = 0.02
    TAKE_PROFIT_PERCENT = 0.04
    CONFIDENCE_THRESHOLD = 0.70
    ANALYSIS_INTERVAL = 300
    SUMMARY_FREQUENCY = 12
    ALERT_LEVEL = "MEDIUM"

class BotFinanciero:
    def __init__(self):
        # Verificar configuración
        if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or CHAT_ID == "YOUR_CHAT_ID_HERE":
            print("❌ ERROR: Debes configurar TELEGRAM_TOKEN y CHAT_ID en config_financiero.py")
            print("📖 Lee las instrucciones en config_financiero.py")
            sys.exit(1)
        
        # Configuración Telegram
        self.telegram_token = TELEGRAM_TOKEN
        self.chat_id = CHAT_ID
        
        # Configuración de trading
        self.symbols = SYMBOLS
        self.balance_per_stock = BALANCE_PER_STOCK
        self.stop_loss_pct = STOP_LOSS_PERCENT
        self.take_profit_pct = TAKE_PROFIT_PERCENT
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        
        # Configuración específica por acción
        self.stock_configs = getattr(sys.modules[__name__], 'STOCK_CONFIGS', {})
        
        # Configuración ML
        self.ml_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_model_trained = False
        
        # Posiciones activas (simuladas)
        self.positions = {}
        
        # Configuración de mercado (NYSE/NASDAQ)
        self.market_timezone = pytz.timezone('US/Eastern')
        
        # Configuración de logging
        self.setup_logging()
        
        # Estado del bot
        self.running = False
        self.analysis_count = 0
        
        # Estadísticas
        self.stats = {
            'total_analyses': 0,
            'trading_signals': 0,
            'successful_predictions': 0,
            'start_time': datetime.now()
        }
        
        self.logger.info("🤖 Bot Financiero inicializado correctamente")
        self.send_telegram_message("🚀 Bot Financiero iniciado - Listo para análisis de acciones!")

    def setup_logging(self):
        """Configurar sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('financial_bot_log.txt', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def send_telegram_message(self, message):
        """Enviar mensaje a Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            if response.status_code != 200:
                self.logger.warning(f"Error enviando mensaje Telegram: {response.status_code}")
        except Exception as e:
            self.logger.error(f"Error en Telegram: {e}")

    def get_stock_config(self, symbol):
        """Obtener configuración específica para una acción"""
        if symbol in self.stock_configs:
            return self.stock_configs[symbol]
        return {
            'stop_loss': self.stop_loss_pct,
            'take_profit': self.take_profit_pct,
            'confidence_threshold': self.confidence_threshold
        }

    def calculate_position_size(self, symbol, price):
        """Calcular tamaño de posición basado en volatilidad"""
        try:
            # Obtener datos para calcular volatilidad
            data = self.get_stock_data(symbol, period="30d")
            if data is None or len(data) < 10:
                return self.balance_per_stock / price
            
            # Calcular volatilidad (desviación estándar de retornos)
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std()
            
            # Ajustar tamaño de posición inversamente a la volatilidad
            volatility_factor = max(0.5, min(2.0, 1.0 / (volatility * 100)))
            adjusted_balance = self.balance_per_stock * volatility_factor
            
            shares = adjusted_balance / price
            
            self.logger.info(f"📊 {symbol} - Volatilidad: {volatility:.4f}, Factor: {volatility_factor:.2f}, Shares: {shares:.2f}")
            
            return shares
            
        except Exception as e:
            self.logger.error(f"Error calculando position size para {symbol}: {e}")
            return self.balance_per_stock / price

    def check_risk_management(self, symbol, entry_price, current_price, position_type):
        """Verificar condiciones de stop-loss y take-profit"""
        config = self.get_stock_config(symbol)
        
        if position_type == 'LONG':
            # Calcular cambio porcentual
            price_change = (current_price - entry_price) / entry_price
            
            # Stop Loss
            if price_change <= -config['stop_loss']:
                return 'STOP_LOSS', f"Stop Loss activado: {price_change:.2%}"
            
            # Take Profit
            if price_change >= config['take_profit']:
                return 'TAKE_PROFIT', f"Take Profit activado: {price_change:.2%}"
        
        elif position_type == 'SHORT':
            # Para posiciones cortas, la lógica se invierte
            price_change = (entry_price - current_price) / entry_price
            
            # Stop Loss (precio sube)
            if price_change <= -config['stop_loss']:
                return 'STOP_LOSS', f"Stop Loss activado: {price_change:.2%}"
            
            # Take Profit (precio baja)
            if price_change >= config['take_profit']:
                return 'TAKE_PROFIT', f"Take Profit activado: {price_change:.2%}"
        
        return 'HOLD', 'Mantener posición'

    def simulate_trade(self, symbol, action, price, confidence):
        """Simular una operación de trading"""
        try:
            config = self.get_stock_config(symbol)
            shares = self.calculate_position_size(symbol, price)
            trade_value = shares * price
            
            trade_id = f"{symbol}_{int(time.time())}"
            
            trade = {
                'id': trade_id,
                'symbol': symbol,
                'action': action,
                'entry_price': price,
                'shares': shares,
                'trade_value': trade_value,
                'confidence': confidence,
                'entry_time': datetime.now(),
                'stop_loss': price * (1 - config['stop_loss']) if action == 'BUY' else price * (1 + config['stop_loss']),
                'take_profit': price * (1 + config['take_profit']) if action == 'BUY' else price * (1 - config['take_profit']),
                'status': 'OPEN'
            }
            
            # Agregar a posiciones activas
            self.positions[trade_id] = trade
            
            # Log y notificación
            self.logger.info(f"💰 Trade simulado: {action} {shares:.2f} shares de {symbol} a ${price:.2f}")
            
            trade_message = f"""
🎯 <b>TRADE SIMULADO</b>

📈 <b>{symbol}</b> - {action}
💰 Precio: ${price:.2f}
📊 Shares: {shares:.2f}
💵 Valor: ${trade_value:.2f}
🧠 Confianza: {confidence:.1%}

🛡️ <b>Gestión de Riesgo:</b>
🔴 Stop Loss: ${trade['stop_loss']:.2f}
🟢 Take Profit: ${trade['take_profit']:.2f}

⏰ {datetime.now().strftime('%H:%M:%S')}
            """
            
            self.send_telegram_message(trade_message)
            self.stats['trading_signals'] += 1
            
            return trade_id
            
        except Exception as e:
            self.logger.error(f"Error simulando trade: {e}")
            return None

    def monitor_positions(self):
        """Monitorear posiciones activas"""
        try:
            if not self.positions:
                return
            
            closed_positions = []
            
            for trade_id, trade in self.positions.items():
                symbol = trade['symbol']
                current_price = self.get_current_price(symbol)
                
                if current_price is None:
                    continue
                
                position_type = 'LONG' if trade['action'] == 'BUY' else 'SHORT'
                risk_status, reason = self.check_risk_management(
                    symbol, trade['entry_price'], current_price, position_type
                )
                
                if risk_status in ['STOP_LOSS', 'TAKE_PROFIT']:
                    # Cerrar posición
                    trade['exit_price'] = current_price
                    trade['exit_time'] = datetime.now()
                    trade['status'] = risk_status
                    
                    # Calcular P&L
                    if trade['action'] == 'BUY':
                        pnl = (current_price - trade['entry_price']) * trade['shares']
                    else:
                        pnl = (trade['entry_price'] - current_price) * trade['shares']
                    
                    trade['pnl'] = pnl
                    pnl_pct = pnl / trade['trade_value'] * 100
                    
                    # Notificación de cierre
                    close_emoji = "🟢" if pnl > 0 else "🔴"
                    
                    close_message = f"""
{close_emoji} <b>POSICIÓN CERRADA</b>

📈 <b>{symbol}</b> - {trade['action']}
💰 Entrada: ${trade['entry_price']:.2f}
💰 Salida: ${current_price:.2f}
📊 P&L: ${pnl:.2f} ({pnl_pct:+.2f}%)
🎯 Razón: {reason}

⏱️ Duración: {str(trade['exit_time'] - trade['entry_time']).split('.')[0]}
                    """
                    
                    self.send_telegram_message(close_message)
                    self.logger.info(f"💰 Posición cerrada: {symbol} - P&L: ${pnl:.2f}")
                    
                    if pnl > 0:
                        self.stats['successful_predictions'] += 1
                    
                    closed_positions.append(trade_id)
            
            # Remover posiciones cerradas
            for trade_id in closed_positions:
                del self.positions[trade_id]
                
        except Exception as e:
            self.logger.error(f"Error monitoreando posiciones: {e}")

    def get_current_price(self, symbol):
        """Obtener precio actual de una acción"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if len(data) > 0:
                return data['Close'].iloc[-1]
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo precio de {symbol}: {e}")
            return None

    def is_market_open(self):
        """Verificar si el mercado está abierto"""
        now = datetime.now(self.market_timezone)
        
        # Verificar si es fin de semana
        if now.weekday() >= 5:  # Sábado = 5, Domingo = 6
            return False
        
        # Horario de mercado: 9:30 AM - 4:00 PM EST
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
        """Verificar si el mercado está abierto"""
        now = datetime.now(self.market_timezone)
        
        # Verificar si es fin de semana
        if now.weekday() >= 5:  # Sábado = 5, Domingo = 6
            return False
        
        # Horario de mercado: 9:30 AM - 4:00 PM EST
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close

    def get_stock_data(self, symbol, period="30d"):
        """Obtener datos históricos de una acción"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            return data
        except Exception as e:
            self.logger.error(f"Error obteniendo datos de {symbol}: {e}")
            return None

    def calculate_technical_indicators(self, data):
        """Calcular indicadores técnicos"""
        if data is None or len(data) < 20:
            return None
        
        indicators = {}
        
        # RSI (Relative Strength Index)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        indicators['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = data['Close'].ewm(span=12).mean()
        exp2 = data['Close'].ewm(span=26).mean()
        indicators['macd'] = exp1 - exp2
        indicators['macd_signal'] = indicators['macd'].ewm(span=9).mean()
        indicators['macd_histogram'] = indicators['macd'] - indicators['macd_signal']
        
        # Bollinger Bands
        sma_20 = data['Close'].rolling(window=20).mean()
        std_20 = data['Close'].rolling(window=20).std()
        indicators['bb_upper'] = sma_20 + (std_20 * 2)
        indicators['bb_lower'] = sma_20 - (std_20 * 2)
        indicators['bb_middle'] = sma_20
        
        # Moving Averages
        indicators['sma_10'] = data['Close'].rolling(window=10).mean()
        indicators['sma_20'] = data['Close'].rolling(window=20).mean()
        indicators['ema_12'] = data['Close'].ewm(span=12).mean()
        
        # Volume indicators
        indicators['volume_sma'] = data['Volume'].rolling(window=20).mean()
        indicators['volume_ratio'] = data['Volume'] / indicators['volume_sma']
        
        # Price momentum
        indicators['momentum'] = data['Close'] / data['Close'].shift(10) - 1
        
        # Support and resistance levels
        indicators['support'] = data['Low'].rolling(window=20).min()
        indicators['resistance'] = data['High'].rolling(window=20).max()
        
        return indicators

    def prepare_ml_features(self, data, indicators):
        """Preparar características para el modelo ML"""
        if indicators is None:
            return None
        
        features = []
        
        # Obtener valores más recientes
        latest_idx = -1
        
        try:
            feature_vector = [
                indicators['rsi'].iloc[latest_idx],
                indicators['macd'].iloc[latest_idx],
                indicators['macd_histogram'].iloc[latest_idx],
                (data['Close'].iloc[latest_idx] - indicators['bb_lower'].iloc[latest_idx]) / 
                (indicators['bb_upper'].iloc[latest_idx] - indicators['bb_lower'].iloc[latest_idx]),
                indicators['volume_ratio'].iloc[latest_idx],
                indicators['momentum'].iloc[latest_idx],
                (data['Close'].iloc[latest_idx] - indicators['sma_10'].iloc[latest_idx]) / indicators['sma_10'].iloc[latest_idx],
                (data['Close'].iloc[latest_idx] - indicators['sma_20'].iloc[latest_idx]) / indicators['sma_20'].iloc[latest_idx],
                (data['Close'].iloc[latest_idx] - indicators['support'].iloc[latest_idx]) / data['Close'].iloc[latest_idx],
                (indicators['resistance'].iloc[latest_idx] - data['Close'].iloc[latest_idx]) / data['Close'].iloc[latest_idx]
            ]
            
            # Verificar que no hay valores NaN
            if any(pd.isna(val) for val in feature_vector):
                return None
                
            return np.array(feature_vector).reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"Error preparando features ML: {e}")
            return None

    def train_ml_model(self):
        """Entrenar modelo ML con datos históricos"""
        try:
            self.logger.info("🧠 Entrenando modelo ML...")
            
            all_features = []
            all_targets = []
            
            for symbol in self.symbols:
                # Obtener más datos históricos para entrenamiento
                data = self.get_stock_data(symbol, period="3mo")
                if data is None or len(data) < 50:
                    continue
                
                indicators = self.calculate_technical_indicators(data)
                if indicators is None:
                    continue
                
                # Crear targets (1 = subida, 0 = bajada) para los próximos 3 días
                future_returns = data['Close'].shift(-3) / data['Close'] - 1
                targets = (future_returns > 0.01).astype(int)  # 1% umbral
                
                # Preparar features para cada día
                for i in range(20, len(data) - 3):  # Evitar NaN y datos futuros
                    try:
                        feature_vector = [
                            indicators['rsi'].iloc[i],
                            indicators['macd'].iloc[i],
                            indicators['macd_histogram'].iloc[i],
                            (data['Close'].iloc[i] - indicators['bb_lower'].iloc[i]) / 
                            (indicators['bb_upper'].iloc[i] - indicators['bb_lower'].iloc[i]),
                            indicators['volume_ratio'].iloc[i],
                            indicators['momentum'].iloc[i],
                            (data['Close'].iloc[i] - indicators['sma_10'].iloc[i]) / indicators['sma_10'].iloc[i],
                            (data['Close'].iloc[i] - indicators['sma_20'].iloc[i]) / indicators['sma_20'].iloc[i],
                            (data['Close'].iloc[i] - indicators['support'].iloc[i]) / data['Close'].iloc[i],
                            (indicators['resistance'].iloc[i] - data['Close'].iloc[i]) / data['Close'].iloc[i]
                        ]
                        
                        if not any(pd.isna(val) for val in feature_vector):
                            all_features.append(feature_vector)
                            all_targets.append(targets.iloc[i])
                            
                    except Exception as e:
                        continue
            
            if len(all_features) < 100:
                self.logger.warning("Insuficientes datos para entrenar ML")
                return False
            
            # Convertir a arrays numpy
            X = np.array(all_features)
            y = np.array(all_targets)
            
            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)
            
            # Entrenar modelo
            self.ml_model.fit(X_scaled, y)
            self.is_model_trained = True
            
            # Calcular accuracy en training set
            train_score = self.ml_model.score(X_scaled, y)
            
            self.logger.info(f"✅ Modelo ML entrenado - Accuracy: {train_score:.2%}")
            self.send_telegram_message(f"🧠 <b>Modelo ML entrenado</b>\n📊 Accuracy: {train_score:.2%}\n📈 Samples: {len(X)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error entrenando modelo ML: {e}")
            return False

    def predict_stock_direction(self, symbol):
        """Predecir dirección de una acción usando ML"""
        if not self.is_model_trained:
            return None, 0.5
        
        try:
            data = self.get_stock_data(symbol, period="30d")
            if data is None:
                return None, 0.5
            
            indicators = self.calculate_technical_indicators(data)
            features = self.prepare_ml_features(data, indicators)
            
            if features is None:
                return None, 0.5
            
            # Normalizar features
            features_scaled = self.scaler.transform(features)
            
            # Predecir
            prediction = self.ml_model.predict(features_scaled)[0]
            confidence = self.ml_model.predict_proba(features_scaled)[0].max()
            
            direction = "BUY" if prediction == 1 else "SELL"
            
            return direction, confidence
            
        except Exception as e:
            self.logger.error(f"Error prediciendo {symbol}: {e}")
            return None, 0.5

    def analyze_stock(self, symbol):
        """Análisis completo de una acción"""
        try:
            data = self.get_stock_data(symbol)
            if data is None:
                return None
            
            current_price = data['Close'].iloc[-1]
            indicators = self.calculate_technical_indicators(data)
            
            if indicators is None:
                return None
            
            # Análisis técnico
            rsi = indicators['rsi'].iloc[-1]
            macd = indicators['macd'].iloc[-1]
            macd_signal = indicators['macd_signal'].iloc[-1]
            bb_position = (current_price - indicators['bb_lower'].iloc[-1]) / (indicators['bb_upper'].iloc[-1] - indicators['bb_lower'].iloc[-1])
            
            # Predicción ML
            ml_direction, ml_confidence = self.predict_stock_direction(symbol)
            
            # Análisis de volumen
            volume_ratio = indicators['volume_ratio'].iloc[-1]
            
            # Señales técnicas
            signals = []
            
            if rsi < 30:
                signals.append("RSI Oversold 📉")
            elif rsi > 70:
                signals.append("RSI Overbought 📈")
            
            if macd > macd_signal:
                signals.append("MACD Bullish 🐂")
            else:
                signals.append("MACD Bearish 🐻")
            
            if bb_position < 0.2:
                signals.append("Near Lower BB 📉")
            elif bb_position > 0.8:
                signals.append("Near Upper BB 📈")
            
            if volume_ratio > 1.5:
                signals.append("High Volume 📊")
            
            analysis = {
                'symbol': symbol,
                'price': current_price,
                'rsi': rsi,
                'macd_signal': "Bullish" if macd > macd_signal else "Bearish",
                'bb_position': bb_position,
                'volume_ratio': volume_ratio,
                'ml_direction': ml_direction,
                'ml_confidence': ml_confidence,
                'signals': signals,
                'timestamp': datetime.now()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analizando {symbol}: {e}")
            return None

    def check_trading_opportunity(self, analysis):
        """Verificar si hay oportunidad de trading"""
        if analysis is None:
            return False, "No analysis available"
        
        # Verificar confianza ML
        if analysis['ml_confidence'] < self.confidence_threshold:
            return False, f"Low ML confidence: {analysis['ml_confidence']:.1%}"
        
        # Verificar si el mercado está abierto
        if not self.is_market_open():
            return False, "Market closed"
        
        # Verificar señales técnicas
        bullish_signals = sum(1 for signal in analysis['signals'] 
                             if any(word in signal for word in ['Bullish', 'Oversold', 'Lower BB']))
        bearish_signals = sum(1 for signal in analysis['signals'] 
                             if any(word in signal for word in ['Bearish', 'Overbought', 'Upper BB']))
        
        # Lógica de trading
        if analysis['ml_direction'] == 'BUY' and bullish_signals >= 2:
            return True, f"BUY signal - ML: {analysis['ml_confidence']:.1%}, Signals: {bullish_signals}"
        elif analysis['ml_direction'] == 'SELL' and bearish_signals >= 2:
            return True, f"SELL signal - ML: {analysis['ml_confidence']:.1%}, Signals: {bearish_signals}"
        
        return False, "No clear signal"

    def format_analysis_message(self, analysis):
        """Formatear análisis para Telegram"""
        if analysis is None:
            return "❌ Error en análisis"
        
        emoji = "🟢" if analysis['ml_direction'] == 'BUY' else "🔴"
        
        message = f"""
{emoji} <b>{analysis['symbol']}</b> - ${analysis['price']:.2f}

🧠 <b>ML Prediction:</b> {analysis['ml_direction']} ({analysis['ml_confidence']:.1%})

📊 <b>Technical Analysis:</b>
• RSI: {analysis['rsi']:.1f}
• MACD: {analysis['macd_signal']}
• BB Position: {analysis['bb_position']:.1%}
• Volume Ratio: {analysis['volume_ratio']:.1f}x

🔍 <b>Signals:</b>
{chr(10).join(f"• {signal}" for signal in analysis['signals'])}

⏰ {analysis['timestamp'].strftime('%H:%M:%S')}
        """
        
        return message.strip()

    def run_analysis_cycle(self):
        """Ejecutar ciclo de análisis"""
        try:
            self.logger.info("🔄 Iniciando ciclo de análisis...")
            self.stats['total_analyses'] += 1
            
            market_open = self.is_market_open()
            if not market_open:
                self.logger.info("📴 Mercado cerrado - Análisis limitado")
            
            # Monitorear posiciones activas primero
            self.monitor_positions()
            
            analyses = []
            trading_opportunities = []
            
            for symbol in self.symbols:
                analysis = self.analyze_stock(symbol)
                if analysis:
                    analyses.append(analysis)
                    
                    # Verificar oportunidades de trading
                    if market_open:
                        has_opportunity, reason = self.check_trading_opportunity(analysis)
                        if has_opportunity:
                            trading_opportunities.append((analysis, reason))
                            
                            # Ejecutar trade simulado si hay señal clara
                            self.simulate_trade(
                                symbol, 
                                analysis['ml_direction'], 
                                analysis['price'], 
                                analysis['ml_confidence']
                            )
                        
                time.sleep(1)  # Evitar rate limiting
            
            # Enviar resumen por Telegram cada hora
            self.analysis_count += 1
            if self.analysis_count % SUMMARY_FREQUENCY == 0:  # Cada X análisis
                self.send_market_summary(analyses, trading_opportunities, market_open)
                self.send_performance_summary()
            
            # Enviar alertas de trading inmediatamente (ya no es necesario, se hace en simulate_trade)
            
            self.logger.info(f"✅ Análisis completado - {len(analyses)} stocks, {len(trading_opportunities)} opportunities, {len(self.positions)} positions active")
            
        except Exception as e:
            self.logger.error(f"Error en ciclo de análisis: {e}")

    def send_performance_summary(self):
        """Enviar resumen de performance del bot"""
        try:
            uptime = datetime.now() - self.stats['start_time']
            
            # Calcular P&L total de posiciones cerradas
            total_pnl = 0
            closed_trades = 0
            
            # Para este ejemplo, usaremos las estadísticas que tenemos
            success_rate = 0
            if self.stats['trading_signals'] > 0:
                success_rate = self.stats['successful_predictions'] / self.stats['trading_signals']
            
            summary = f"""
📊 <b>RESUMEN DE PERFORMANCE</b>

⏱️ <b>Uptime:</b> {str(uptime).split('.')[0]}
🔄 <b>Análisis realizados:</b> {self.stats['total_analyses']}
🎯 <b>Señales de trading:</b> {self.stats['trading_signals']}
✅ <b>Predicciones exitosas:</b> {self.stats['successful_predictions']}
📈 <b>Tasa de éxito:</b> {success_rate:.1%}

💼 <b>Posiciones activas:</b> {len(self.positions)}
            """
            
            if self.positions:
                summary += "\n🔥 <b>Posiciones abiertas:</b>"
                for trade_id, trade in list(self.positions.items())[:3]:  # Mostrar máximo 3
                    current_price = self.get_current_price(trade['symbol'])
                    if current_price:
                        if trade['action'] == 'BUY':
                            pnl = (current_price - trade['entry_price']) * trade['shares']
                        else:
                            pnl = (trade['entry_price'] - current_price) * trade['shares']
                        pnl_pct = pnl / trade['trade_value'] * 100
                        
                        emoji = "🟢" if pnl > 0 else "🔴"
                        summary += f"\n{emoji} {trade['symbol']}: {pnl_pct:+.2f}%"
            
            summary += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
            
            self.send_telegram_message(summary)
            
        except Exception as e:
            self.logger.error(f"Error enviando resumen de performance: {e}")

    def send_market_summary(self, analyses, opportunities, market_open):
        """Enviar resumen del mercado"""
        try:
            status = "🟢 ABIERTO" if market_open else "🔴 CERRADO"
            
            summary = f"""
📈 <b>RESUMEN DE MERCADO</b> - {status}

📊 <b>Análisis de {len(analyses)} acciones:</b>
            """
            
            for analysis in analyses[:5]:  # Mostrar top 5
                direction_emoji = "🟢" if analysis['ml_direction'] == 'BUY' else "🔴"
                summary += f"\n{direction_emoji} {analysis['symbol']}: ${analysis['price']:.2f} ({analysis['ml_confidence']:.0%})"
            
            if opportunities:
                summary += f"\n\n🎯 <b>{len(opportunities)} Oportunidades de Trading:</b>"
                for analysis, reason in opportunities[:3]:  # Top 3 opportunities
                    summary += f"\n• {analysis['symbol']}: {reason}"
            else:
                summary += "\n\n😴 No hay oportunidades de trading claras"
            
            summary += f"\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"
            
            self.send_telegram_message(summary)
            
        except Exception as e:
            self.logger.error(f"Error enviando resumen: {e}")

    def send_trading_alert(self, analysis, reason):
        """Enviar alerta de trading"""
        try:
            emoji = "🚀" if analysis['ml_direction'] == 'BUY' else "⚠️"
            
            alert = f"""
{emoji} <b>TRADING ALERT</b>

{self.format_analysis_message(analysis)}

💡 <b>Razón:</b> {reason}

💰 <b>Sugerencia:</b>
• Entrada: ${analysis['price']:.2f}
• Stop Loss: ${analysis['price'] * (1 - self.stop_loss_pct):.2f} (-{self.stop_loss_pct:.1%})
• Take Profit: ${analysis['price'] * (1 + self.take_profit_pct):.2f} (+{self.take_profit_pct:.1%})
            """
            
            self.send_telegram_message(alert)
            self.logger.info(f"🎯 Trading alert enviada para {analysis['symbol']}")
            
        except Exception as e:
            self.logger.error(f"Error enviando alerta: {e}")

    def start(self):
        """Iniciar el bot"""
        self.logger.info("🚀 Iniciando Bot Financiero...")
        
        # Entrenar modelo ML
        if not self.train_ml_model():
            self.logger.warning("⚠️ Continuando sin modelo ML")
        
        self.running = True
        
        # Mensaje de inicio
        start_message = f"""
🤖 <b>Bot Financiero Iniciado</b>

📈 <b>Acciones monitoreadas:</b>
{', '.join(self.symbols)}

🕐 <b>Horario de mercado:</b> 9:30-16:00 EST
💰 <b>Balance por acción:</b> ${self.balance_per_stock}
🛡️ <b>Stop Loss:</b> {self.stop_loss_pct:.1%}
🎯 <b>Take Profit:</b> {self.take_profit_pct:.1%}
🧠 <b>ML Threshold:</b> {self.confidence_threshold:.0%}

⚡ Análisis cada 5 minutos
📊 Resumen cada hora
        """
        
        self.send_telegram_message(start_message)
        
        try:
            while self.running:
                self.run_analysis_cycle()
                
                # Esperar 5 minutos entre análisis
                for _ in range(300):  # 5 minutos = 300 segundos
                    if not self.running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("🛑 Bot detenido por usuario")
        except Exception as e:
            self.logger.error(f"💥 Error crítico: {e}")
            self.send_telegram_message(f"💥 <b>ERROR CRÍTICO</b>\n{str(e)}")
        finally:
            self.stop()

    def stop(self):
        """Detener el bot"""
        self.running = False
        self.logger.info("🛑 Bot Financiero detenido")
        self.send_telegram_message("🛑 Bot Financiero detenido")

if __name__ == "__main__":
    # Crear e iniciar el bot
    bot = BotFinanciero()
    
    try:
        bot.start()
    except Exception as e:
        print(f"Error iniciando bot: {e}")
        logging.error(f"Error iniciando bot: {e}")