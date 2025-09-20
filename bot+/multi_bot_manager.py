"""
🤖 GESTOR MULTI-BOT UNIVERSAL 🤖
=================================
Sistema para gestionar múltiples bots en diferentes mercados
"""

import json
import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class MarketType(Enum):
    CRYPTO = "cryptocurrency"
    STOCKS = "stocks"
    FOREX = "forex"
    COMMODITIES = "commodities"
    INDICES = "indices"

class BotStrategy(Enum):
    BASIC_MA = "basic_moving_average"
    ML_ENHANCED = "machine_learning"
    SCALPING = "scalping"
    SWING = "swing_trading"
    ARBITRAGE = "arbitrage"

@dataclass
class BotConfig:
    """Configuración de un bot individual"""
    bot_id: str
    name: str
    market_type: MarketType
    strategy: BotStrategy
    symbol: str
    exchange: str
    vm_instance: str
    log_file: str
    active: bool = True
    risk_level: float = 0.01  # 1% por defecto
    
class MultiBotManager:
    def __init__(self):
        self.bots: Dict[str, BotConfig] = {}
        self.market_configs = {
            MarketType.CRYPTO: {
                'exchanges': ['binance', 'coinbase', 'kraken'],
                'symbols': ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOGEUSDT'],
                'api_requirements': ['binance-python', 'ccxt']
            },
            MarketType.STOCKS: {
                'exchanges': ['alpaca', 'yahoo', 'iex'],
                'symbols': ['AAPL', 'GOOGL', 'TSLA', 'AMZN', 'MSFT'],
                'api_requirements': ['yfinance', 'alpaca-trade-api']
            },
            MarketType.FOREX: {
                'exchanges': ['oanda', 'fxcm'],
                'symbols': ['EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD'],
                'api_requirements': ['oandapyV20', 'fxcmpy']
            },
            MarketType.COMMODITIES: {
                'exchanges': ['yahoo', 'alpha_vantage'],
                'symbols': ['GC=F', 'SI=F', 'CL=F', 'NG=F'],  # Oro, Plata, Petróleo, Gas
                'api_requirements': ['yfinance', 'alpha_vantage']
            }
        }
    
    def create_bot_portfolio(self, portfolio_name: str):
        """Crear un portafolio diversificado de bots"""
        portfolio = {
            'name': portfolio_name,
            'created_at': datetime.datetime.now().isoformat(),
            'bots': []
        }
        
        # Bot 1: Bitcoin Básico
        portfolio['bots'].append({
            'bot_id': 'btc_basic_001',
            'name': 'Bitcoin Bot Básico',
            'market_type': MarketType.CRYPTO.value,
            'strategy': BotStrategy.BASIC_MA.value,
            'symbol': 'BTCUSDT',
            'exchange': 'binance',
            'vm_instance': 'crypto-vm-1',
            'risk_level': 0.005  # 0.5% más conservador para BTC
        })
        
        # Bot 2: Ethereum ML
        portfolio['bots'].append({
            'bot_id': 'eth_ml_001',
            'name': 'Ethereum Bot ML',
            'market_type': MarketType.CRYPTO.value,
            'strategy': BotStrategy.ML_ENHANCED.value,
            'symbol': 'ETHUSDT',
            'exchange': 'binance',
            'vm_instance': 'crypto-vm-1',
            'risk_level': 0.01
        })
        
        # Bot 3: Apple Stocks
        portfolio['bots'].append({
            'bot_id': 'aapl_ml_001',
            'name': 'Apple Stock Bot',
            'market_type': MarketType.STOCKS.value,
            'strategy': BotStrategy.ML_ENHANCED.value,
            'symbol': 'AAPL',
            'exchange': 'alpaca',
            'vm_instance': 'stocks-vm-1',
            'risk_level': 0.02  # 2% para acciones (más volátil)
        })
        
        # Bot 4: Tesla Swing Trading
        portfolio['bots'].append({
            'bot_id': 'tsla_swing_001',
            'name': 'Tesla Swing Bot',
            'market_type': MarketType.STOCKS.value,
            'strategy': BotStrategy.SWING.value,
            'symbol': 'TSLA',
            'exchange': 'alpaca',
            'vm_instance': 'stocks-vm-1',
            'risk_level': 0.03  # 3% para swing trading
        })
        
        # Bot 5: Oro Commodities
        portfolio['bots'].append({
            'bot_id': 'gold_basic_001',
            'name': 'Gold Trading Bot',
            'market_type': MarketType.COMMODITIES.value,
            'strategy': BotStrategy.BASIC_MA.value,
            'symbol': 'GC=F',
            'exchange': 'yahoo',
            'vm_instance': 'commodities-vm-1',
            'risk_level': 0.015  # 1.5% para oro
        })
        
        # Bot 6: EUR/USD Forex
        portfolio['bots'].append({
            'bot_id': 'eurusd_scalp_001',
            'name': 'EUR/USD Scalping Bot',
            'market_type': MarketType.FOREX.value,
            'strategy': BotStrategy.SCALPING.value,
            'symbol': 'EUR/USD',
            'exchange': 'oanda',
            'vm_instance': 'forex-vm-1',
            'risk_level': 0.005  # 0.5% para scalping forex
        })
        
        return portfolio
    
    def generate_deployment_plan(self, portfolio):
        """Generar plan de despliegue para el portafolio"""
        plan = {
            'vm_instances': {},
            'api_keys_needed': set(),
            'dependencies': set()
        }
        
        for bot in portfolio['bots']:
            vm = bot['vm_instance']
            if vm not in plan['vm_instances']:
                plan['vm_instances'][vm] = {
                    'bots': [],
                    'market_types': set(),
                    'exchanges': set()
                }
            
            plan['vm_instances'][vm]['bots'].append(bot)
            plan['vm_instances'][vm]['market_types'].add(bot['market_type'])
            plan['vm_instances'][vm]['exchanges'].add(bot['exchange'])
            
            # Agregar API keys necesarias
            market_type = MarketType(bot['market_type'])
            if market_type in self.market_configs:
                plan['api_keys_needed'].add(bot['exchange'])
                plan['dependencies'].update(self.market_configs[market_type]['api_requirements'])
        
        # Convertir sets a listas para JSON
        for vm_data in plan['vm_instances'].values():
            vm_data['market_types'] = list(vm_data['market_types'])
            vm_data['exchanges'] = list(vm_data['exchanges'])
        
        plan['api_keys_needed'] = list(plan['api_keys_needed'])
        plan['dependencies'] = list(plan['dependencies'])
        
        return plan
    
    def create_vm_setup_script(self, vm_name: str, vm_data: dict):
        """Crear script de setup para una VM específica"""
        script = f"""#!/bin/bash
# Setup script para {vm_name}
# Configuración automática de bots multi-mercado

echo "🚀 Configurando {vm_name}..."

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y pip
sudo apt install python3 python3-pip python3-venv -y

# Crear entorno virtual
python3 -m venv botenv
source botenv/bin/activate

# Instalar dependencias base
pip install pandas numpy requests python-dotenv

# Instalar dependencias específicas por mercado
"""
        
        # Agregar dependencias específicas
        for dep in vm_data.get('dependencies', []):
            script += f"pip install {dep}\n"
        
        script += f"""
# Crear directorios
mkdir -p logs configs bots

# Configurar variables de entorno
cat > .env << EOF
# API Keys para {vm_name}
"""
        
        # Agregar placeholders para API keys
        for exchange in vm_data.get('exchanges', []):
            if exchange == 'binance':
                script += """BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET_KEY=your_binance_secret_key_here
"""
            elif exchange == 'alpaca':
                script += """ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
"""
            elif exchange == 'oanda':
                script += """OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
"""
        
        script += """EOF

echo "✅ Setup completado para {vm_name}"
echo "📝 No olvides configurar las API keys en .env"
echo "🤖 Bots configurados en esta VM:"
"""
        
        for bot in vm_data.get('bots', []):
            script += f'echo "   - {bot["name"]} ({bot["symbol"]})"' + "\n"
        
        return script
    
    def save_portfolio(self, portfolio, filename: str):
        """Guardar portafolio en archivo JSON"""
        with open(filename, 'w') as f:
            json.dump(portfolio, f, indent=2, default=str)
        print(f"💾 Portafolio guardado en {filename}")
    
    def load_portfolio(self, filename: str):
        """Cargar portafolio desde archivo JSON"""
        with open(filename, 'r') as f:
            portfolio = json.load(f)
        print(f"📂 Portafolio cargado desde {filename}")
        return portfolio

def main():
    """Ejemplo de uso del gestor multi-bot"""
    manager = MultiBotManager()
    
    print("🤖 GESTOR MULTI-BOT UNIVERSAL")
    print("=" * 40)
    
    # Crear portafolio diversificado
    portfolio = manager.create_bot_portfolio("Portfolio Diversificado")
    
    print(f"📊 Portafolio creado: {portfolio['name']}")
    print(f"🤖 Número de bots: {len(portfolio['bots'])}")
    print()
    
    # Mostrar bots
    for i, bot in enumerate(portfolio['bots'], 1):
        print(f"{i}. {bot['name']}")
        print(f"   💰 Mercado: {bot['market_type']}")
        print(f"   📈 Símbolo: {bot['symbol']}")
        print(f"   🔧 Estrategia: {bot['strategy']}")
        print(f"   ☁️  VM: {bot['vm_instance']}")
        print(f"   ⚠️  Riesgo: {bot['risk_level']*100}%")
        print()
    
    # Generar plan de despliegue
    deployment_plan = manager.generate_deployment_plan(portfolio)
    
    print("🏗️ PLAN DE DESPLIEGUE")
    print("-" * 20)
    print(f"🖥️ VMs necesarias: {len(deployment_plan['vm_instances'])}")
    print(f"🔑 API Keys: {', '.join(deployment_plan['api_keys_needed'])}")
    print(f"📦 Dependencias: {', '.join(deployment_plan['dependencies'])}")
    print()
    
    # Crear scripts de setup
    for vm_name, vm_data in deployment_plan['vm_instances'].items():
        script = manager.create_vm_setup_script(vm_name, vm_data)
        filename = f"setup_{vm_name.replace('-', '_')}.sh"
        with open(filename, 'w') as f:
            f.write(script)
        print(f"📜 Script creado: {filename}")
    
    # Guardar portafolio
    manager.save_portfolio(portfolio, "portfolio_diversificado.json")
    
    print()
    print("🎯 PRÓXIMOS PASOS:")
    print("1. Crear las VMs en Google Cloud")
    print("2. Ejecutar los scripts de setup")
    print("3. Configurar las API keys")
    print("4. Desplegar los bots específicos")
    print("5. Monitorear con el analizador gráfico")

if __name__ == "__main__":
    main()