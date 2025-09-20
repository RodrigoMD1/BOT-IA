#!/bin/bash
# Script para configurar y ejecutar ambos bots en Google Cloud VM

echo "🚀 Configurando Bot Trading Dual en Google Cloud"
echo "=================================================="

# Verificar dependencias
echo "📦 Verificando dependencias..."
python3 -c "import pandas, numpy, binance" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Dependencias OK"
else
    echo "❌ Instalando dependencias faltantes..."
    pip3 install pandas numpy python-binance
fi

# Crear directorios para logs
mkdir -p ~/trading_logs
mkdir -p ~/trading_backup

echo "🤖 Configuración de bots:"
echo "========================="
echo "Bot Básico: Bot-trading.py (Medias móviles)"
echo "Bot ML: BotMLCloud.py (Machine Learning)"
echo ""

# Función para ejecutar bot básico
run_basic_bot() {
    echo "🔵 Iniciando Bot Básico..."
    cd ~/
    nohup python3 Bot-trading.py > ~/trading_logs/basic_bot.log 2>&1 &
    echo $! > ~/trading_logs/basic_bot.pid
    echo "✅ Bot Básico ejecutándose (PID: $(cat ~/trading_logs/basic_bot.pid))"
}

# Función para ejecutar bot ML
run_ml_bot() {
    echo "🟣 Iniciando Bot ML..."
    cd ~/
    nohup python3 BotMLCloud.py > ~/trading_logs/ml_bot.log 2>&1 &
    echo $! > ~/trading_logs/ml_bot.pid
    echo "✅ Bot ML ejecutándose (PID: $(cat ~/trading_logs/ml_bot.pid))"
}

# Función para mostrar estado
show_status() {
    echo "📊 Estado de los bots:"
    echo "====================="
    
    if [ -f ~/trading_logs/basic_bot.pid ]; then
        basic_pid=$(cat ~/trading_logs/basic_bot.pid)
        if ps -p $basic_pid > /dev/null 2>&1; then
            echo "🔵 Bot Básico: EJECUTÁNDOSE (PID: $basic_pid)"
        else
            echo "🔴 Bot Básico: DETENIDO"
        fi
    else
        echo "⚪ Bot Básico: NO INICIADO"
    fi
    
    if [ -f ~/trading_logs/ml_bot.pid ]; then
        ml_pid=$(cat ~/trading_logs/ml_bot.pid)
        if ps -p $ml_pid > /dev/null 2>&1; then
            echo "🟣 Bot ML: EJECUTÁNDOSE (PID: $ml_pid)"
        else
        echo "🔴 Bot ML: DETENIDO"
        fi
    else
        echo "⚪ Bot ML: NO INICIADO"
    fi
    
    echo ""
    echo "📈 Últimas líneas de logs:"
    echo "========================="
    if [ -f ~/trading_logs/basic_bot.log ]; then
        echo "🔵 Bot Básico (últimas 3 líneas):"
        tail -3 ~/trading_logs/basic_bot.log
        echo ""
    fi
    
    if [ -f ~/trading_logs/ml_bot.log ]; then
        echo "🟣 Bot ML (últimas 3 líneas):"
        tail -3 ~/trading_logs/ml_bot.log
        echo ""
    fi
}

# Función para detener bots
stop_bots() {
    echo "🛑 Deteniendo bots..."
    
    if [ -f ~/trading_logs/basic_bot.pid ]; then
        basic_pid=$(cat ~/trading_logs/basic_bot.pid)
        if ps -p $basic_pid > /dev/null 2>&1; then
            kill $basic_pid
            echo "🔵 Bot Básico detenido"
        fi
        rm -f ~/trading_logs/basic_bot.pid
    fi
    
    if [ -f ~/trading_logs/ml_bot.pid ]; then
        ml_pid=$(cat ~/trading_logs/ml_bot.pid)
        if ps -p $ml_pid > /dev/null 2>&1; then
            kill $ml_pid
            echo "🟣 Bot ML detenido"
        fi
        rm -f ~/trading_logs/ml_bot.pid
    fi
}

# Función para mostrar logs en tiempo real
show_logs() {
    echo "📊 Logs en tiempo real (Ctrl+C para salir):"
    echo "==========================================="
    
    if [ "$1" == "basic" ]; then
        tail -f ~/trading_logs/basic_bot.log
    elif [ "$1" == "ml" ]; then
        tail -f ~/trading_logs/ml_bot.log
    else
        # Mostrar ambos logs intercalados
        tail -f ~/trading_logs/basic_bot.log ~/trading_logs/ml_bot.log
    fi
}

# Función para backup de logs
backup_logs() {
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_dir="~/trading_backup/backup_$timestamp"
    mkdir -p $backup_dir
    
    cp ~/trading_logs/*.log $backup_dir/ 2>/dev/null
    cp ~/trading_log.txt $backup_dir/ 2>/dev/null
    cp ~/ml_cloud_trading_log.txt $backup_dir/ 2>/dev/null
    
    echo "💾 Backup creado en: $backup_dir"
}

# Función para comparar rendimiento
compare_performance() {
    echo "📊 COMPARACIÓN DE RENDIMIENTO"
    echo "=============================="
    
    echo "🔵 Bot Básico:"
    if [ -f ~/trading_log.txt ]; then
        echo "   Trades ejecutados:"
        grep -c "COMPRA\|VENTA" ~/trading_log.txt
        echo "   Ganancias/Pérdidas:"
        grep "Ganancia/Pérdida" ~/trading_log.txt | tail -5
    else
        echo "   No hay log disponible"
    fi
    
    echo ""
    echo "🟣 Bot ML:"
    if [ -f ~/ml_cloud_trading_log.txt ]; then
        echo "   Trades ejecutados:"
        grep -c "COMPRA\|VENTA" ~/ml_cloud_trading_log.txt
        echo "   Ganancias/Pérdidas:"
        grep "P&L" ~/ml_cloud_trading_log.txt | tail -5
    else
        echo "   No hay log disponible"
    fi
}

# Menú principal
case "$1" in
    "start")
        echo "🚀 Iniciando ambos bots..."
        run_basic_bot
        sleep 5
        run_ml_bot
        sleep 3
        show_status
        ;;
    "stop")
        stop_bots
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs $2
        ;;
    "backup")
        backup_logs
        ;;
    "compare")
        compare_performance
        ;;
    "restart")
        echo "🔄 Reiniciando bots..."
        stop_bots
        sleep 5
        run_basic_bot
        sleep 5
        run_ml_bot
        sleep 3
        show_status
        ;;
    *)
        echo "🤖 Bot Trading Manager - Google Cloud"
        echo "====================================="
        echo ""
        echo "Uso: $0 {comando}"
        echo ""
        echo "Comandos disponibles:"
        echo "  start      - Iniciar ambos bots"
        echo "  stop       - Detener ambos bots"
        echo "  restart    - Reiniciar ambos bots"
        echo "  status     - Mostrar estado actual"
        echo "  logs       - Mostrar logs en tiempo real"
        echo "  logs basic - Mostrar solo logs del bot básico"
        echo "  logs ml    - Mostrar solo logs del bot ML"
        echo "  backup     - Crear backup de logs"
        echo "  compare    - Comparar rendimiento de ambos bots"
        echo ""
        echo "Ejemplos:"
        echo "  ./bot_manager.sh start"
        echo "  ./bot_manager.sh status"
        echo "  ./bot_manager.sh logs ml"
        ;;
esac