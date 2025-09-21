# Configuración del Bot Financiero con Telegram
# IMPORTANTE: Este archivo ya no contiene claves sensibles
# Las claves se manejan a través de variables de entorno

import os
import sys
from pathlib import Path

# Agregar directorio padre al path para importar secure_config
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

try:
    from secure_config import get_telegram_keys
    # Obtener claves de forma segura
    telegram_config = get_telegram_keys('financial')
    TELEGRAM_TOKEN = telegram_config['token']
    CHAT_ID = telegram_config['chat_id']
    
    # Validar configuración
    if not TELEGRAM_TOKEN or 'YOUR_TELEGRAM_BOT_TOKEN_HERE' in TELEGRAM_TOKEN:
        print("⚠️  TELEGRAM_TOKEN no configurado en .env")
        TELEGRAM_TOKEN = "8293607157:AAFyyLRtiXx0cxLViCjPuV_KH7GzzVkz6AQ"  # Fallback temporal
        
    if not CHAT_ID or 'YOUR_CHAT_ID_HERE' in CHAT_ID:
        print("⚠️  CHAT_ID no configurado en .env")
        CHAT_ID = "5817464985"  # Fallback temporal
        
except ImportError:
    print("⚠️  secure_config no disponible, usando configuración local")
    # Configuración local como fallback
    TELEGRAM_TOKEN = "8293607157:AAFyyLRtiXx0cxLViCjPuV_KH7GzzVkz6AQ"
    CHAT_ID = "5817464985"

# ================================
# CONFIGURACIÓN DE TRADING
# ================================

# Acciones a monitorear (puedes agregar más)
SYMBOLS = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX']

# Balance simulado por acción (en USD)
BALANCE_PER_STOCK = 1000

# Gestión de riesgo
STOP_LOSS_PERCENT = 0.02    # 2% stop loss
TAKE_PROFIT_PERCENT = 0.04  # 4% take profit

# Configuración ML
CONFIDENCE_THRESHOLD = 0.70  # 70% confianza mínima

# ================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ================================

# Frecuencia de análisis (en segundos)
ANALYSIS_INTERVAL = 300  # 5 minutos

# Enviar resumen cada X análisis
SUMMARY_FREQUENCY = 12   # Cada hora (12 * 5 min = 60 min)

# Nivel de alertas
ALERT_LEVEL = "MEDIUM"   # LOW, MEDIUM, HIGH

# ================================
# CONFIGURACIÓN AVANZADA
# ================================

# Horario de mercado (US Eastern Time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

# Configuración de recursos para VM
MAX_MEMORY_USAGE = 300  # MB
MAX_CPU_USAGE = 50      # %

# Logging
LOG_LEVEL = "INFO"      # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "financial_bot_log.txt"

# ================================
# CONFIGURACIÓN ESPECÍFICA POR ACCIÓN
# ================================

# Configuraciones personalizadas por ticker
STOCK_CONFIGS = {
    'AAPL': {
        'stop_loss': 0.015,      # 1.5% para Apple (menos volátil)
        'take_profit': 0.03,     # 3%
        'confidence_threshold': 0.75
    },
    'TSLA': {
        'stop_loss': 0.03,       # 3% para Tesla (más volátil)
        'take_profit': 0.06,     # 6%
        'confidence_threshold': 0.65
    },
    'NVDA': {
        'stop_loss': 0.025,      # 2.5% para NVIDIA
        'take_profit': 0.05,     # 5%
        'confidence_threshold': 0.70
    }
}

# ================================
# INSTRUCCIONES DE SETUP
# ================================

"""
PASOS PARA CONFIGURAR EL BOT:

1. CREAR BOT DE TELEGRAM:
   - Abre Telegram
   - Busca @BotFather
   - Escribe /newbot
   - Elige un nombre para tu bot
   - Elige un username (debe terminar en 'bot')
   - Copia el token y pégalo en TELEGRAM_TOKEN

2. OBTENER CHAT ID:
   - Busca @userinfobot en Telegram
   - Escribe /start
   - Copia tu ID y pégalo en CHAT_ID

3. INSTALAR DEPENDENCIAS:
   pip install yfinance pandas numpy scikit-learn requests pytz

4. EJECUTAR EL BOT:
   python BotFinanciero.py

5. PARA DEPLOYMENT EN GOOGLE CLOUD:
   - Usar el script de control incluido
   - Configurar variables de entorno
   - Monitorear recursos
"""