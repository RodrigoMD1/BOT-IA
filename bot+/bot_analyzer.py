"""
🤖 ANALIZADOR COMPARATIVO DE BOTS DE TRADING 🤖
==============================================
Analiza y compara el rendimiento de Bot Básico vs Bot ML
Ejecutar desde tu PC con los logs copiados de las VMs
"""

import re
import datetime
from datetime import datetime as dt
import json

class TradingBotAnalyzer:
    def __init__(self):
        self.basic_bot_data = {
            'trades': [],
            'total_profit': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.ml_bot_data = {
            'trades': [],
            'total_profit': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'predictions': [],
            'confidence_levels': [],
            'start_time': None,
            'end_time': None
        }
    
    def parse_basic_bot_log(self, log_content):
        """Analiza el log del bot básico"""
        print("🔵 Analizando Bot Básico...")
        
        lines = log_content.strip().split('\n')
        
        for line in lines:
            # Extraer timestamp
            timestamp_match = re.search(r'\[([\d-]+\s[\d:]+)\]', line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    timestamp = dt.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    if not self.basic_bot_data['start_time']:
                        self.basic_bot_data['start_time'] = timestamp
                    self.basic_bot_data['end_time'] = timestamp
                except:
                    pass
            
            # Detectar compras
            if 'COMPRA' in line and ('agresiva' in line or 'BÁSICA' in line):
                price_match = re.search(r'(\d+\.\d+)', line)
                if price_match:
                    price = float(price_match.group(1))
                    self.basic_bot_data['trades'].append({
                        'type': 'BUY',
                        'price': price,
                        'timestamp': timestamp if 'timestamp' in locals() else None
                    })
            
            # Detectar ventas con P&L
            if any(keyword in line for keyword in ['STOP LOSS', 'TAKE PROFIT', 'VENTA']):
                # Buscar ganancia/pérdida
                profit_match = re.search(r'P&L[:\s]+([+-]?\d+\.\d+)', line)
                if not profit_match:
                    profit_match = re.search(r'Ganancia/Pérdida[:\s]+([+-]?\d+\.\d+)', line)
                
                if profit_match:
                    profit = float(profit_match.group(1))
                    self.basic_bot_data['total_profit'] += profit
                    self.basic_bot_data['total_trades'] += 1
                    
                    if profit > 0:
                        self.basic_bot_data['winning_trades'] += 1
                    else:
                        self.basic_bot_data['losing_trades'] += 1
                    
                    # Detectar tipo de venta
                    trade_type = 'SELL'
                    if 'STOP LOSS' in line:
                        trade_type = 'STOP_LOSS'
                    elif 'TAKE PROFIT' in line:
                        trade_type = 'TAKE_PROFIT'
                    
                    price_match = re.search(r'(\d+\.\d+)', line)
                    price = float(price_match.group(1)) if price_match else 0
                    
                    self.basic_bot_data['trades'].append({
                        'type': trade_type,
                        'price': price,
                        'profit': profit,
                        'timestamp': timestamp if 'timestamp' in locals() else None
                    })
    
    def parse_ml_bot_log(self, log_content):
        """Analiza el log del bot ML"""
        print("🟣 Analizando Bot ML...")
        
        lines = log_content.strip().split('\n')
        
        for line in lines:
            # Extraer timestamp
            timestamp_match = re.search(r'\[([\d-]+\s[\d:]+)\]', line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    timestamp = dt.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    if not self.ml_bot_data['start_time']:
                        self.ml_bot_data['start_time'] = timestamp
                    self.ml_bot_data['end_time'] = timestamp
                except:
                    pass
            
            # Detectar predicciones y confianza
            pred_match = re.search(r'Pred[:\s]+([+-]?\d+\.\d+).*Conf[:\s]+(\d+\.\d+)%', line)
            if pred_match:
                prediction = float(pred_match.group(1))
                confidence = float(pred_match.group(2))
                self.ml_bot_data['predictions'].append(prediction)
                self.ml_bot_data['confidence_levels'].append(confidence)
            
            # Detectar compras ML
            if 'COMPRA ML' in line:
                price_match = re.search(r'(\d+\.\d+)', line)
                conf_match = re.search(r'Conf[:\s]+(\d+\.\d+)%', line)
                
                if price_match:
                    price = float(price_match.group(1))
                    confidence = float(conf_match.group(1)) if conf_match else 0
                    
                    self.ml_bot_data['trades'].append({
                        'type': 'BUY',
                        'price': price,
                        'confidence': confidence,
                        'timestamp': timestamp if 'timestamp' in locals() else None
                    })
            
            # Detectar ventas ML con P&L
            if any(keyword in line for keyword in ['STOP LOSS ML', 'TAKE PROFIT ML']):
                profit_match = re.search(r'P&L[:\s]+([+-]?\d+\.\d+)', line)
                
                if profit_match:
                    profit = float(profit_match.group(1))
                    self.ml_bot_data['total_profit'] += profit
                    self.ml_bot_data['total_trades'] += 1
                    
                    if profit > 0:
                        self.ml_bot_data['winning_trades'] += 1
                    else:
                        self.ml_bot_data['losing_trades'] += 1
                    
                    trade_type = 'STOP_LOSS' if 'STOP LOSS' in line else 'TAKE_PROFIT'
                    price_match = re.search(r'(\d+\.\d+)', line)
                    price = float(price_match.group(1)) if price_match else 0
                    
                    self.ml_bot_data['trades'].append({
                        'type': trade_type,
                        'price': price,
                        'profit': profit,
                        'timestamp': timestamp if 'timestamp' in locals() else None
                    })
    
    def calculate_statistics(self):
        """Calcula estadísticas detalladas"""
        print("\n📊 Calculando estadísticas...")
        
        stats = {
            'basic_bot': {},
            'ml_bot': {},
            'comparison': {}
        }
        
        # Estadísticas Bot Básico
        basic = self.basic_bot_data
        if basic['total_trades'] > 0:
            stats['basic_bot'] = {
                'total_trades': basic['total_trades'],
                'winning_trades': basic['winning_trades'],
                'losing_trades': basic['losing_trades'],
                'win_rate': (basic['winning_trades'] / basic['total_trades']) * 100,
                'total_profit': basic['total_profit'],
                'avg_profit_per_trade': basic['total_profit'] / basic['total_trades'],
                'runtime_hours': self._calculate_runtime(basic['start_time'], basic['end_time'])
            }
        
        # Estadísticas Bot ML
        ml = self.ml_bot_data
        if ml['total_trades'] > 0:
            avg_confidence = sum(ml['confidence_levels']) / len(ml['confidence_levels']) if ml['confidence_levels'] else 0
            stats['ml_bot'] = {
                'total_trades': ml['total_trades'],
                'winning_trades': ml['winning_trades'],
                'losing_trades': ml['losing_trades'],
                'win_rate': (ml['winning_trades'] / ml['total_trades']) * 100,
                'total_profit': ml['total_profit'],
                'avg_profit_per_trade': ml['total_profit'] / ml['total_trades'],
                'avg_confidence': avg_confidence,
                'total_predictions': len(ml['predictions']),
                'runtime_hours': self._calculate_runtime(ml['start_time'], ml['end_time'])
            }
        
        # Comparación
        if basic['total_trades'] > 0 and ml['total_trades'] > 0:
            stats['comparison'] = {
                'more_active': 'Basic' if basic['total_trades'] > ml['total_trades'] else 'ML',
                'better_win_rate': 'Basic' if stats['basic_bot']['win_rate'] > stats['ml_bot']['win_rate'] else 'ML',
                'more_profitable': 'Basic' if basic['total_profit'] > ml['total_profit'] else 'ML',
                'profit_difference': abs(basic['total_profit'] - ml['total_profit']),
                'trade_frequency_basic': basic['total_trades'] / stats['basic_bot']['runtime_hours'] if stats['basic_bot']['runtime_hours'] > 0 else 0,
                'trade_frequency_ml': ml['total_trades'] / stats['ml_bot']['runtime_hours'] if stats['ml_bot']['runtime_hours'] > 0 else 0
            }
        
        return stats
    
    def _calculate_runtime(self, start_time, end_time):
        """Calcula el tiempo de ejecución en horas"""
        if start_time and end_time:
            delta = end_time - start_time
            return delta.total_seconds() / 3600
        return 0
    
    def generate_report(self, stats):
        """Genera reporte detallado"""
        report = []
        report.append("🤖 REPORTE COMPARATIVO DE BOTS DE TRADING")
        report.append("=" * 50)
        report.append(f"📅 Fecha de análisis: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Bot Básico
        if 'basic_bot' in stats and stats['basic_bot']:
            basic = stats['basic_bot']
            report.append("🔵 BOT BÁSICO (Medias Móviles)")
            report.append("-" * 30)
            report.append(f"📊 Trades totales: {basic['total_trades']}")
            report.append(f"✅ Trades ganadores: {basic['winning_trades']}")
            report.append(f"❌ Trades perdedores: {basic['losing_trades']}")
            report.append(f"🎯 Tasa de éxito: {basic['win_rate']:.1f}%")
            report.append(f"💰 Ganancia total: {basic['total_profit']:.6f} USDT")
            report.append(f"📈 Ganancia promedio: {basic['avg_profit_per_trade']:.6f} USDT")
            report.append(f"⏱️  Tiempo ejecutándose: {basic['runtime_hours']:.1f} horas")
            report.append("")
        
        # Bot ML
        if 'ml_bot' in stats and stats['ml_bot']:
            ml = stats['ml_bot']
            report.append("🟣 BOT ML (Machine Learning)")
            report.append("-" * 30)
            report.append(f"📊 Trades totales: {ml['total_trades']}")
            report.append(f"✅ Trades ganadores: {ml['winning_trades']}")
            report.append(f"❌ Trades perdedores: {ml['losing_trades']}")
            report.append(f"🎯 Tasa de éxito: {ml['win_rate']:.1f}%")
            report.append(f"💰 Ganancia total: {ml['total_profit']:.6f} USDT")
            report.append(f"📈 Ganancia promedio: {ml['avg_profit_per_trade']:.6f} USDT")
            report.append(f"🧠 Confianza promedio: {ml['avg_confidence']:.1f}%")
            report.append(f"🔮 Predicciones generadas: {ml['total_predictions']}")
            report.append(f"⏱️  Tiempo ejecutándose: {ml['runtime_hours']:.1f} horas")
            report.append("")
        
        # Comparación
        if 'comparison' in stats and stats['comparison']:
            comp = stats['comparison']
            report.append("🏆 COMPARACIÓN DIRECTA")
            report.append("-" * 20)
            report.append(f"🔄 Más activo: Bot {comp['more_active']}")
            report.append(f"🎯 Mejor tasa de éxito: Bot {comp['better_win_rate']}")
            report.append(f"💰 Más rentable: Bot {comp['more_profitable']}")
            report.append(f"💵 Diferencia de ganancia: {comp['profit_difference']:.6f} USDT")
            report.append(f"⚡ Frecuencia Basic: {comp['trade_frequency_basic']:.2f} trades/hora")
            report.append(f"⚡ Frecuencia ML: {comp['trade_frequency_ml']:.2f} trades/hora")
            report.append("")
        
        # Recomendaciones
        report.append("💡 RECOMENDACIONES")
        report.append("-" * 18)
        
        if 'comparison' in stats and stats['comparison']:
            if stats['comparison']['more_profitable'] == 'ML':
                report.append("🟣 El Bot ML mostró mejor rendimiento general")
                report.append("   ✅ Considera usar estrategia ML para futuras operaciones")
                report.append("   ✅ La selectividad del ML fue efectiva")
            else:
                report.append("🔵 El Bot Básico mostró mejor rendimiento")
                report.append("   ✅ La estrategia simple fue más efectiva en este período")
                report.append("   ✅ Mayor frecuencia de trading compensó la menor precisión")
            
            if 'ml_bot' in stats and stats['ml_bot']:
                if stats['ml_bot']['win_rate'] > 60:
                    report.append("   🧠 El ML muestra buen potencial, considera ajustar confianza mínima")
                
        else:
            report.append("⚠️  Necesitas más datos para una comparación definitiva")
            report.append("   📊 Ejecuta los bots por al menos 24 horas")
        
        return "\n".join(report)
    
    def save_report(self, report_text):
        """Guarda el reporte en archivo"""
        filename = f"trading_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"📄 Reporte guardado en: {filename}")
        return filename

def main():
    analyzer = TradingBotAnalyzer()
    
    print("🤖 ANALIZADOR DE BOTS DE TRADING")
    print("=" * 40)
    print()
    
    # Solicitar logs del Bot Básico
    print("📋 PASO 1: Pega el log del Bot Básico")
    print("Copia el contenido de 'trading_log.txt' de tu VM original:")
    print("(Presiona Enter al final y luego escribe 'FIN' en una línea para terminar)")
    print()
    
    basic_log_lines = []
    while True:
        line = input()
        if line.strip() == 'FIN':
            break
        basic_log_lines.append(line)
    
    basic_log_content = '\n'.join(basic_log_lines)
    
    if basic_log_content.strip():
        analyzer.parse_basic_bot_log(basic_log_content)
        print("✅ Log del Bot Básico procesado")
    else:
        print("⚠️ No se proporcionó log del Bot Básico")
    
    print()
    
    # Solicitar logs del Bot ML
    print("📋 PASO 2: Pega el log del Bot ML")
    print("Copia el contenido de 'ml_bot_log.txt' de tu VM nueva:")
    print("(Presiona Enter al final y luego escribe 'FIN' en una línea para terminar)")
    print()
    
    ml_log_lines = []
    while True:
        line = input()
        if line.strip() == 'FIN':
            break
        ml_log_lines.append(line)
    
    ml_log_content = '\n'.join(ml_log_lines)
    
    if ml_log_content.strip():
        analyzer.parse_ml_bot_log(ml_log_content)
        print("✅ Log del Bot ML procesado")
    else:
        print("⚠️ No se proporcionó log del Bot ML")
    
    print()
    
    # Generar análisis
    if basic_log_content.strip() or ml_log_content.strip():
        stats = analyzer.calculate_statistics()
        report = analyzer.generate_report(stats)
        
        print(report)
        print()
        
        # Preguntar si guardar
        save = input("💾 ¿Guardar reporte en archivo? (s/n): ").lower()
        if save == 's':
            filename = analyzer.save_report(report)
            print(f"✅ Análisis completo guardado en {filename}")
    else:
        print("❌ No se proporcionaron logs para analizar")

if __name__ == "__main__":
    main()