"""
🤖 ANALIZADOR VISUAL DE BOTS DE TRADING 🤖
==========================================
Interfaz gráfica para analizar y comparar bots
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
import datetime
from datetime import datetime as dt
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class TradingBotAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Analizador de Bots de Trading")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Configurar estilo
        self.setup_style()
        
        # Datos de los bots
        self.basic_bot_data = self.init_bot_data()
        self.ml_bot_data = self.init_bot_data()
        
        # Crear interfaz
        self.create_widgets()
        
    def setup_style(self):
        """Configurar estilo visual"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', 
                       font=('Arial', 16, 'bold'),
                       background='#2b2b2b',
                       foreground='#ffffff')
        
        style.configure('Header.TLabel',
                       font=('Arial', 12, 'bold'),
                       background='#2b2b2b',
                       foreground='#4CAF50')
        
        style.configure('Info.TLabel',
                       font=('Arial', 10),
                       background='#2b2b2b',
                       foreground='#ffffff')
        
        style.configure('Custom.TButton',
                       font=('Arial', 10, 'bold'))
    
    def init_bot_data(self):
        """Inicializar estructura de datos del bot"""
        return {
            'trades': [],
            'total_profit': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'start_time': None,
            'end_time': None,
            'predictions': [],
            'confidence_levels': []
        }
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(main_frame, 
                               text="🤖 ANALIZADOR DE BOTS DE TRADING", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Cargar Datos
        self.create_data_tab()
        
        # Pestaña 2: Estadísticas
        self.create_stats_tab()
        
        # Pestaña 3: Gráficos
        self.create_charts_tab()
        
        # Pestaña 4: Reporte
        self.create_report_tab()
    
    def create_data_tab(self):
        """Crear pestaña para cargar datos"""
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="📊 Cargar Datos")
        
        # Frame para Bot Básico
        basic_frame = ttk.LabelFrame(data_frame, text="🔵 Bot Básico", padding=10)
        basic_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(basic_frame, text="Pega aquí el contenido de btc_trading_log.txt:", 
                 style='Header.TLabel').pack(anchor=tk.W)
        
        self.basic_text = scrolledtext.ScrolledText(basic_frame, height=8, 
                                                   bg='#1e1e1e', fg='#ffffff',
                                                   font=('Consolas', 9))
        self.basic_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        basic_btn_frame = ttk.Frame(basic_frame)
        basic_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(basic_btn_frame, text="📁 Cargar desde archivo", 
                  command=lambda: self.load_from_file(self.basic_text),
                  style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(basic_btn_frame, text="🔄 Procesar Log Básico", 
                  command=self.process_basic_log,
                  style='Custom.TButton').pack(side=tk.LEFT)
        
        # Frame para Bot ML
        ml_frame = ttk.LabelFrame(data_frame, text="🟣 Bot ML", padding=10)
        ml_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(ml_frame, text="Pega aquí el contenido de ml_bot_log.txt:", 
                 style='Header.TLabel').pack(anchor=tk.W)
        
        self.ml_text = scrolledtext.ScrolledText(ml_frame, height=8, 
                                               bg='#1e1e1e', fg='#ffffff',
                                               font=('Consolas', 9))
        self.ml_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ml_btn_frame = ttk.Frame(ml_frame)
        ml_btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(ml_btn_frame, text="📁 Cargar desde archivo", 
                  command=lambda: self.load_from_file(self.ml_text),
                  style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(ml_btn_frame, text="🔄 Procesar Log ML", 
                  command=self.process_ml_log,
                  style='Custom.TButton').pack(side=tk.LEFT)
        
        # Botón de análisis completo
        ttk.Button(data_frame, text="📈 ANALIZAR TODO", 
                  command=self.analyze_all,
                  style='Custom.TButton').pack(pady=20)
    
    def create_stats_tab(self):
        """Crear pestaña de estadísticas"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Estadísticas")
        
        # Frame con scroll
        canvas = tk.Canvas(stats_frame, bg='#2b2b2b')
        scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=canvas.yview)
        self.stats_content = ttk.Frame(canvas)
        
        self.stats_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.stats_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Etiqueta inicial
        ttk.Label(self.stats_content, 
                 text="📊 Las estadísticas aparecerán aquí después del análisis", 
                 style='Info.TLabel').pack(pady=50)
    
    def create_charts_tab(self):
        """Crear pestaña de gráficos"""
        self.charts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.charts_frame, text="📈 Gráficos")
        
        ttk.Label(self.charts_frame, 
                 text="📈 Los gráficos aparecerán aquí después del análisis", 
                 style='Info.TLabel').pack(pady=50)
    
    def create_report_tab(self):
        """Crear pestaña de reporte"""
        report_frame = ttk.Frame(self.notebook)
        self.notebook.add(report_frame, text="📄 Reporte")
        
        # Área de texto para el reporte
        self.report_text = scrolledtext.ScrolledText(report_frame, 
                                                    bg='#1e1e1e', fg='#ffffff',
                                                    font=('Consolas', 10))
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones
        btn_frame = ttk.Frame(report_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(btn_frame, text="💾 Guardar Reporte", 
                  command=self.save_report,
                  style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="🔄 Actualizar", 
                  command=self.generate_report,
                  style='Custom.TButton').pack(side=tk.LEFT)
    
    def load_from_file(self, text_widget):
        """Cargar log desde archivo"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de log",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_widget.delete(1.0, tk.END)
                    text_widget.insert(1.0, content)
                messagebox.showinfo("Éxito", f"Archivo cargado: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")
    
    def process_basic_log(self):
        """Procesar log del bot básico"""
        content = self.basic_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Advertencia", "No hay contenido para procesar")
            return
        
        self.basic_bot_data = self.init_bot_data()
        self.parse_basic_bot_log(content)
        messagebox.showinfo("Éxito", "Log del Bot Básico procesado correctamente")
    
    def process_ml_log(self):
        """Procesar log del bot ML"""
        content = self.ml_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Advertencia", "No hay contenido para procesar")
            return
        
        self.ml_bot_data = self.init_bot_data()
        self.parse_ml_bot_log(content)
        messagebox.showinfo("Éxito", "Log del Bot ML procesado correctamente")
    
    def parse_basic_bot_log(self, log_content):
        """Analizar el log del bot básico"""
        lines = log_content.strip().split('\n')
        
        # Variables para seguimiento de sesiones
        session_starts = []
        session_ends = []
        
        for line in lines:
            # Extraer timestamp con formato más preciso
            timestamp_match = re.search(r'\[([\d-]+\s[\d:]+\.?\d*)\]', line)
            timestamp = None
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    # Intentar con microsegundos primero
                    if '.' in timestamp_str:
                        timestamp = dt.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                    else:
                        timestamp = dt.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    if not self.basic_bot_data['start_time']:
                        self.basic_bot_data['start_time'] = timestamp
                        session_starts.append(timestamp)
                    self.basic_bot_data['end_time'] = timestamp
                except:
                    pass
            
            # Detectar inicio de nueva sesión (cuando el bot se reinicia)
            if 'COMPRA BTC a $' in line and timestamp:
                # Si hay un gap de más de 10 minutos, es una nueva sesión
                if session_starts and self.basic_bot_data['end_time']:
                    time_gap = (timestamp - self.basic_bot_data['end_time']).total_seconds() / 60
                    if time_gap > 10:  # Más de 10 minutos = nueva sesión
                        session_starts.append(timestamp)
            
            # Detectar fin de sesión
            if 'Bot BTC detenido' in line and timestamp:
                session_ends.append(timestamp)
            
            # Detectar compras (formato: "COMPRA BTC a $115444.99")
            if 'COMPRA BTC a $' in line or ('COMPRA' in line and ('agresiva' in line or 'BÁSICA' in line)):
                price_match = re.search(r'\$(\d+\.\d+)', line)
                if not price_match:
                    price_match = re.search(r'(\d+\.\d+)', line)
                if price_match:
                    price = float(price_match.group(1))
                    self.basic_bot_data['trades'].append({
                        'type': 'BUY',
                        'price': price,
                        'timestamp': timestamp
                    })
            
            # Detectar ventas con P&L (formatos: "Ganancia/Pérdida: $-0.01 USD" o "P&L: +0.01")
            if any(keyword in line for keyword in ['STOP LOSS', 'TAKE PROFIT', 'VENTA', 'Ganancia/Pérdida']):
                profit_match = re.search(r'P&L[:\s]+([+-]?\d+\.\d+)', line)
                if not profit_match:
                    profit_match = re.search(r'Ganancia/Pérdida[:\s]+\$([+-]?\d+\.\d+)', line)
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
                    
                    trade_type = 'SELL'
                    if 'STOP LOSS' in line:
                        trade_type = 'STOP_LOSS'
                    elif 'TAKE PROFIT' in line:
                        trade_type = 'TAKE_PROFIT'
                    
                    price_match = re.search(r'\$(\d+\.\d+)', line)
                    if not price_match:
                        price_match = re.search(r'(\d+\.\d+)', line)
                    price = float(price_match.group(1)) if price_match else 0
                    
                    self.basic_bot_data['trades'].append({
                        'type': trade_type,
                        'price': price,
                        'profit': profit,
                        'timestamp': timestamp
                    })
        
        # Calcular tiempo real considerando múltiples sesiones
        if session_starts and session_ends:
            total_runtime = 0
            # Emparejar inicios con finales de sesión
            for i in range(min(len(session_starts), len(session_ends))):
                session_time = (session_ends[i] - session_starts[i]).total_seconds() / 3600
                total_runtime += session_time
            
            # Si hay más inicios que finales, la última sesión aún está activa
            if len(session_starts) > len(session_ends) and self.basic_bot_data['end_time']:
                last_session_time = (self.basic_bot_data['end_time'] - session_starts[-1]).total_seconds() / 3600
                total_runtime += last_session_time
            
            # Guardar el tiempo real calculado
            self.basic_bot_data['real_runtime_hours'] = total_runtime
    
    def parse_ml_bot_log(self, log_content):
        """Analizar el log del bot ML"""
        lines = log_content.strip().split('\n')
        
        for line in lines:
            # Extraer timestamp
            timestamp_match = re.search(r'\[([\d-]+\s[\d:]+)\]', line)
            timestamp = None
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    timestamp = dt.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    if not self.ml_bot_data['start_time']:
                        self.ml_bot_data['start_time'] = timestamp
                    self.ml_bot_data['end_time'] = timestamp
                except:
                    pass
            
            # Detectar predicciones y confianza - FORMATO ACTUALIZADO
            pred_match = re.search(r'Pred:\s*([+-]?\d+\.\d+).*Conf:\s*(\d+\.\d+)%', line)
            if pred_match:
                prediction = float(pred_match.group(1))
                confidence = float(pred_match.group(2))
                self.ml_bot_data['predictions'].append(prediction)
                self.ml_bot_data['confidence_levels'].append(confidence)
                
                # Extraer precio BTC del mismo log
                price_match = re.search(r'Precio BTC:\s*\$(\d+\.\d+)', line)
                if price_match:
                    price = float(price_match.group(1))
                    # Agregar como predicción con datos
                    self.ml_bot_data['trades'].append({
                        'type': 'PREDICTION',
                        'price': price,
                        'prediction': prediction,
                        'confidence': confidence,
                        'timestamp': timestamp
                    })
            
            # Detectar compras ML - FORMATO ACTUALIZADO PARA LOGS REALES
            if any(keyword in line for keyword in ['COMPRA ML', '🟢 COMPRA ML BTC', '🟢 COMPRA ML']):
                # Buscar precio en el formato: Precio: $115588.50
                price_match = re.search(r'Precio:\s*\$(\d+\.?\d*)', line)
                if not price_match:
                    # Formato alternativo: cualquier número decimal
                    price_match = re.search(r'(\d+\.\d+)', line)
                
                conf_match = re.search(r'Conf[:\s]+(\d+\.\d+)%', line)
                
                if price_match:
                    price = float(price_match.group(1))
                    confidence = float(conf_match.group(1)) if conf_match else 0
                    
                    self.ml_bot_data['trades'].append({
                        'type': 'BUY',
                        'price': price,
                        'confidence': confidence,
                        'timestamp': timestamp
                    })
            
            # Detectar estadísticas ML
            if 'ESTADÍSTICAS ML' in line:
                # Extraer balance, ROI, trades, etc.
                balance_match = re.search(r'Balance:\s*(\d+\.\d+)\s*USDT', line)
                roi_match = re.search(r'ROI:\s*([+-]?\d+\.\d+)%', line)
                trades_match = re.search(r'Trades:\s*(\d+)', line)
                winrate_match = re.search(r'Win Rate:\s*(\d+\.\d+)%', line)
                
                if balance_match:
                    self.ml_bot_data['balance'] = float(balance_match.group(1))
                if roi_match:
                    self.ml_bot_data['roi'] = float(roi_match.group(1))
                if trades_match:
                    self.ml_bot_data['total_trades'] = int(trades_match.group(1))
                if winrate_match:
                    self.ml_bot_data['win_rate'] = float(winrate_match.group(1))
            
            # Detectar ventas ML con P&L - ACTUALIZADO PARA NUEVOS FORMATOS
            if any(keyword in line for keyword in ['STOP LOSS', 'TAKE PROFIT', '✅ VENTA EXITOSA', '❌ PÉRDIDA']):
                profit_match = re.search(r'P&L[:\s]+([+-]?\$?\d+\.\d+)', line)
                
                if profit_match:
                    profit_str = profit_match.group(1).replace('$', '').replace('+', '')
                    profit = float(profit_str)
                    self.ml_bot_data['total_profit'] += profit
                    self.ml_bot_data['total_trades'] += 1
                    
                    if profit > 0:
                        self.ml_bot_data['winning_trades'] += 1
                    else:
                        self.ml_bot_data['losing_trades'] += 1
                    
                    # Determinar tipo de trade
                    if 'STOP LOSS' in line:
                        trade_type = 'STOP_LOSS'
                    elif 'TAKE PROFIT' in line:
                        trade_type = 'TAKE_PROFIT'
                    elif '✅' in line:
                        trade_type = 'WIN'
                    else:
                        trade_type = 'LOSS'
                    
                    price_match = re.search(r'(\d+\.\d+)', line)
                    price = float(price_match.group(1)) if price_match else 0
                    
                    self.ml_bot_data['trades'].append({
                        'type': trade_type,
                        'price': price,
                        'profit': profit,
                        'timestamp': timestamp
                    })
    
    def analyze_all(self):
        """Realizar análisis completo"""
        if not self.basic_text.get(1.0, tk.END).strip() and not self.ml_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Advertencia", "Primero carga y procesa al menos un log")
            return
        
        # Procesar logs si hay contenido
        basic_content = self.basic_text.get(1.0, tk.END).strip()
        if basic_content:
            self.basic_bot_data = self.init_bot_data()
            self.parse_basic_bot_log(basic_content)
        
        ml_content = self.ml_text.get(1.0, tk.END).strip()
        if ml_content:
            self.ml_bot_data = self.init_bot_data()
            self.parse_ml_bot_log(ml_content)
        
        # Generar estadísticas y visualizaciones
        self.display_statistics()
        self.create_charts()
        self.generate_report()
        
        messagebox.showinfo("Éxito", "¡Análisis completo realizado!")
    
    def display_statistics(self):
        """Mostrar estadísticas en la pestaña correspondiente"""
        # Limpiar contenido anterior
        for widget in self.stats_content.winfo_children():
            widget.destroy()
        
        # Calcular estadísticas
        stats = self.calculate_statistics()
        
        # Mostrar estadísticas del Bot Básico
        if 'basic_bot' in stats and stats['basic_bot']:
            basic_frame = ttk.LabelFrame(self.stats_content, text="🔵 Bot Básico", padding=15)
            basic_frame.pack(fill=tk.X, padx=10, pady=5)
            
            basic = stats['basic_bot']
            stats_text = [
                f"📊 Trades totales: {basic['total_trades']}",
                f"✅ Trades ganadores: {basic['winning_trades']}",
                f"❌ Trades perdedores: {basic['losing_trades']}",
                f"🎯 Tasa de éxito: {basic['win_rate']:.1f}%",
                f"💰 Ganancia total: {basic['total_profit']:.6f} USDT",
                f"📈 Ganancia promedio: {basic['avg_profit_per_trade']:.6f} USDT/trade",
                f"⏱️ Tiempo ejecutándose: {basic['runtime_hours']:.1f} horas"
            ]
            
            for stat in stats_text:
                ttk.Label(basic_frame, text=stat, style='Info.TLabel').pack(anchor=tk.W, pady=2)
        
        # Mostrar estadísticas del Bot ML
        if 'ml_bot' in stats and stats['ml_bot']:
            ml_frame = ttk.LabelFrame(self.stats_content, text="🟣 Bot ML", padding=15)
            ml_frame.pack(fill=tk.X, padx=10, pady=5)
            
            ml = stats['ml_bot']
            stats_text = [
                f"📊 Trades totales: {ml['total_trades']}",
                f"✅ Trades ganadores: {ml['winning_trades']}",
                f"❌ Trades perdedores: {ml['losing_trades']}",
                f"🎯 Tasa de éxito: {ml['win_rate']:.1f}%",
                f"💰 Ganancia total: {ml['total_profit']:.6f} USDT",
                f"📈 Ganancia promedio: {ml['avg_profit_per_trade']:.6f} USDT/trade",
                f"🧠 Confianza promedio: {ml['avg_confidence']:.1f}%",
                f"🔮 Predicciones generadas: {ml['total_predictions']}",
                f"⏱️ Tiempo ejecutándose: {ml['runtime_hours']:.1f} horas"
            ]
            
            for stat in stats_text:
                ttk.Label(ml_frame, text=stat, style='Info.TLabel').pack(anchor=tk.W, pady=2)
        
        # Mostrar comparación
        if 'comparison' in stats and stats['comparison']:
            comp_frame = ttk.LabelFrame(self.stats_content, text="🏆 Comparación", padding=15)
            comp_frame.pack(fill=tk.X, padx=10, pady=5)
            
            comp = stats['comparison']
            comp_text = [
                f"🔄 Más activo: Bot {comp['more_active']}",
                f"🎯 Mejor tasa de éxito: Bot {comp['better_win_rate']}",
                f"💰 Más rentable: Bot {comp['more_profitable']}",
                f"💵 Diferencia de ganancia: {comp['profit_difference']:.6f} USDT",
                f"⚡ Frecuencia Basic: {comp['trade_frequency_basic']:.2f} trades/hora",
                f"⚡ Frecuencia ML: {comp['trade_frequency_ml']:.2f} trades/hora"
            ]
            
            for comp_stat in comp_text:
                ttk.Label(comp_frame, text=comp_stat, style='Info.TLabel').pack(anchor=tk.W, pady=2)
    
    def calculate_statistics(self):
        """Calcular estadísticas detalladas"""
        stats = {}
        
        # Estadísticas Bot Básico
        basic = self.basic_bot_data
        if basic['total_trades'] > 0:
            # Usar tiempo real calculado si está disponible, sino usar el cálculo estándar
            real_runtime = basic.get('real_runtime_hours', self._calculate_runtime(basic['start_time'], basic['end_time']))
            stats['basic_bot'] = {
                'total_trades': basic['total_trades'],
                'winning_trades': basic['winning_trades'],
                'losing_trades': basic['losing_trades'],
                'win_rate': (basic['winning_trades'] / basic['total_trades']) * 100,
                'total_profit': basic['total_profit'],
                'avg_profit_per_trade': basic['total_profit'] / basic['total_trades'],
                'runtime_hours': real_runtime
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
        """Calcular el tiempo de ejecución en horas"""
        if start_time and end_time:
            delta = end_time - start_time
            return delta.total_seconds() / 3600
        return 0
    
    def create_charts(self):
        """Crear gráficos de comparación"""
        # Limpiar frame anterior
        for widget in self.charts_frame.winfo_children():
            widget.destroy()
        
        # Crear figura con subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.patch.set_facecolor('#2b2b2b')
        
        # Configurar colores
        colors = ['#4CAF50', '#9C27B0']  # Verde para básico, morado para ML
        
        # Gráfico 1: Trades por bot
        basic_trades = self.basic_bot_data['total_trades']
        ml_trades = self.ml_bot_data['total_trades']
        
        if basic_trades > 0 or ml_trades > 0:
            ax1.bar(['Bot Básico', 'Bot ML'], [basic_trades, ml_trades], color=colors)
            ax1.set_title('Total de Trades', color='white', fontweight='bold')
            ax1.set_ylabel('Número de Trades', color='white')
            ax1.tick_params(colors='white')
        
        # Gráfico 2: Rentabilidad
        basic_profit = self.basic_bot_data['total_profit']
        ml_profit = self.ml_bot_data['total_profit']
        
        if basic_profit != 0 or ml_profit != 0:
            ax2.bar(['Bot Básico', 'Bot ML'], [basic_profit, ml_profit], color=colors)
            ax2.set_title('Ganancia Total (USDT)', color='white', fontweight='bold')
            ax2.set_ylabel('USDT', color='white')
            ax2.tick_params(colors='white')
        
        # Gráfico 3: Tasa de éxito
        basic_win_rate = (self.basic_bot_data['winning_trades'] / basic_trades * 100) if basic_trades > 0 else 0
        ml_win_rate = (self.ml_bot_data['winning_trades'] / ml_trades * 100) if ml_trades > 0 else 0
        
        if basic_win_rate > 0 or ml_win_rate > 0:
            ax3.bar(['Bot Básico', 'Bot ML'], [basic_win_rate, ml_win_rate], color=colors)
            ax3.set_title('Tasa de Éxito (%)', color='white', fontweight='bold')
            ax3.set_ylabel('Porcentaje', color='white')
            ax3.tick_params(colors='white')
        
        # Gráfico 4: Distribución ganadores vs perdedores
        if basic_trades > 0 and ml_trades > 0:
            basic_data = [self.basic_bot_data['winning_trades'], self.basic_bot_data['losing_trades']]
            ml_data = [self.ml_bot_data['winning_trades'], self.ml_bot_data['losing_trades']]
            
            x = ['Ganadores', 'Perdedores']
            width = 0.35
            x_pos = [0, 1]
            
            ax4.bar([p - width/2 for p in x_pos], basic_data, width, label='Bot Básico', color=colors[0])
            ax4.bar([p + width/2 for p in x_pos], ml_data, width, label='Bot ML', color=colors[1])
            
            ax4.set_title('Trades Ganadores vs Perdedores', color='white', fontweight='bold')
            ax4.set_ylabel('Número de Trades', color='white')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(x)
            ax4.legend()
            ax4.tick_params(colors='white')
        
        # Configurar fondo de todos los subplots
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_facecolor('#3b3b3b')
            for spine in ax.spines.values():
                spine.set_color('white')
        
        plt.tight_layout()
        
        # Agregar a tkinter
        canvas = FigureCanvasTkAgg(fig, self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def generate_report(self):
        """Generar reporte completo"""
        stats = self.calculate_statistics()
        
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
            report.append(f"⏱️ Tiempo ejecutándose: {basic['runtime_hours']:.1f} horas")
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
            report.append(f"⏱️ Tiempo ejecutándose: {ml['runtime_hours']:.1f} horas")
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
            report.append("⚠️ Necesitas más datos para una comparación definitiva")
            report.append("   📊 Ejecuta los bots por al menos 24 horas")
        
        # Mostrar en la interfaz
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, "\n".join(report))
    
    def save_report(self):
        """Guardar reporte en archivo"""
        content = self.report_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showwarning("Advertencia", "No hay reporte para guardar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialname=f"trading_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Éxito", f"Reporte guardado en: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

def main():
    root = tk.Tk()
    app = TradingBotAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()