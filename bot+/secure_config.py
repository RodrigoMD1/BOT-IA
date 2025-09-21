#!/usr/bin/env python3
"""
Módulo de Configuración Segura
Maneja las variables de entorno de forma segura para todos los bots
"""

import os
import sys
from pathlib import Path

# Intentar importar python-dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv no instalado. Instala con: pip install python-dotenv")
    load_dotenv = None

class SecureConfig:
    """Clase para manejar configuración segura"""
    
    def __init__(self):
        self.load_environment()
        self.validate_required_vars()
    
    def load_environment(self):
        """Cargar variables de entorno"""
        # Buscar archivo .env
        env_path = Path(__file__).parent / '.env'
        
        if load_dotenv and env_path.exists():
            load_dotenv(env_path)
            print("✅ Variables de entorno cargadas desde .env")
        elif env_path.exists():
            print("⚠️  Archivo .env encontrado pero python-dotenv no disponible")
            print("💡 Las variables se cargarán del sistema")
        else:
            print("⚠️  Archivo .env no encontrado, usando variables del sistema")
    
    def get_env_var(self, var_name, default=None, required=False):
        """Obtener variable de entorno de forma segura"""
        value = os.getenv(var_name, default)
        
        if required and not value:
            raise ValueError(f"❌ Variable requerida no encontrada: {var_name}")
        
        # No mostrar valores sensibles en logs
        if any(keyword in var_name.lower() for keyword in ['key', 'secret', 'token', 'password']):
            display_value = f"{value[:8]}..." if value else "No configurada"
        else:
            display_value = value or "No configurada"
            
        print(f"🔧 {var_name}: {display_value}")
        return value
    
    def validate_required_vars(self):
        """Validar que las variables críticas estén configuradas"""
        required_vars = []
        warnings = []
        
        # Verificar configuración de ambiente
        environment = self.get_env_var('ENVIRONMENT', 'TESTNET')
        
        if environment == 'PRODUCTION':
            required_vars.extend([
                'BINANCE_API_KEY_PROD',
                'BINANCE_SECRET_KEY_PROD'
            ])
        else:
            warnings.append("🟡 Ejecutando en modo TESTNET")
        
        # Verificar variables opcionales pero recomendadas
        telegram_token = self.get_env_var('TELEGRAM_TOKEN_FINANCIAL')
        if not telegram_token or 'YOUR_TELEGRAM_BOT_TOKEN_HERE' in telegram_token:
            warnings.append("🟡 Token de Telegram no configurado correctamente")
        
        # Mostrar advertencias
        for warning in warnings:
            print(warning)
        
        return len(required_vars) == 0 or all(os.getenv(var) for var in required_vars)

    # Métodos específicos para cada tipo de configuración
    def get_binance_config(self):
        """Obtener configuración de Binance"""
        environment = self.get_env_var('ENVIRONMENT', 'TESTNET')
        
        if environment == 'PRODUCTION':
            return {
                'api_key': self.get_env_var('BINANCE_API_KEY_PROD', required=True),
                'secret_key': self.get_env_var('BINANCE_SECRET_KEY_PROD', required=True),
                'testnet': False
            }
        else:
            return {
                'api_key': self.get_env_var('BINANCE_API_KEY_TESTNET', 'demo_key'),
                'secret_key': self.get_env_var('BINANCE_SECRET_KEY_TESTNET', 'demo_secret'),
                'testnet': True
            }
    
    def get_telegram_config(self, bot_type='financial'):
        """Obtener configuración de Telegram"""
        if bot_type == 'financial':
            return {
                'token': self.get_env_var('TELEGRAM_TOKEN_FINANCIAL'),
                'chat_id': self.get_env_var('TELEGRAM_CHAT_ID')
            }
        else:
            return {
                'token': self.get_env_var('TELEGRAM_TOKEN_CRYPTO'),
                'chat_id': self.get_env_var('TELEGRAM_CHAT_ID_CRYPTO', 
                                          self.get_env_var('TELEGRAM_CHAT_ID'))
            }
    
    def get_trading_config(self):
        """Obtener configuración de trading"""
        return {
            'initial_balance_crypto': float(self.get_env_var('INITIAL_BALANCE_CRYPTO', '20.0')),
            'balance_per_bot': float(self.get_env_var('BALANCE_PER_BOT', '10.0')),
            'balance_per_stock': float(self.get_env_var('BALANCE_PER_STOCK', '1000.0')),
            'max_daily_trades': int(self.get_env_var('MAX_DAILY_TRADES', '50')),
            'max_position_size': float(self.get_env_var('MAX_POSITION_SIZE', '0.1')),
            'stop_loss_limit': float(self.get_env_var('STOP_LOSS_LIMIT', '0.05'))
        }
    
    def get_gcp_config(self):
        """Obtener configuración de Google Cloud"""
        return {
            'project_id': self.get_env_var('GCP_PROJECT_ID', 'galvanized-env-376523'),
            'zone': self.get_env_var('GCP_ZONE', 'asia-southeast1-a'),
            'vm_crypto': self.get_env_var('GCP_VM_CRYPTO', 'bot-trading-asia'),
            'vm_ml': self.get_env_var('GCP_VM_ML', 'bot-trading-ml')
        }

# Instancia global para fácil acceso
config = SecureConfig()

# Funciones de conveniencia
def get_binance_keys():
    """Función simple para obtener claves de Binance"""
    return config.get_binance_config()

def get_telegram_keys(bot_type='financial'):
    """Función simple para obtener claves de Telegram"""
    return config.get_telegram_config(bot_type)

def is_production():
    """Verificar si estamos en producción"""
    return config.get_env_var('ENVIRONMENT', 'TESTNET').upper() == 'PRODUCTION'

def safe_start_message():
    """Mensaje seguro de inicio"""
    environment = config.get_env_var('ENVIRONMENT', 'TESTNET')
    binance_config = config.get_binance_config()
    
    print("🤖 Configuración de seguridad cargada:")
    print(f"🌍 Ambiente: {environment}")
    print(f"🔐 Binance: {'Producción' if not binance_config['testnet'] else 'Testnet'}")
    
    if environment == 'PRODUCTION':
        print("⚠️  ¡EJECUTANDO EN PRODUCCIÓN! Verificar configuración")
        return input("¿Continuar? (yes/no): ").lower() == 'yes'
    
    return True

if __name__ == "__main__":
    print("🔒 Probando configuración segura...")
    
    # Probar todas las configuraciones
    print("\n📡 Configuración Binance:")
    binance = config.get_binance_config()
    
    print("\n📱 Configuración Telegram:")
    telegram = config.get_telegram_config()
    
    print("\n💰 Configuración Trading:")
    trading = config.get_trading_config()
    
    print("\n☁️  Configuración GCP:")
    gcp = config.get_gcp_config()
    
    print("\n✅ Configuración completada correctamente!")