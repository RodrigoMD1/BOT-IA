#!/bin/bash
# Script de Control para Bot Financiero - Google Cloud VM
# Versión: 1.0
# Fecha: 21 septiembre 2025

# Configuración
BOT_NAME="bot_financiero"
BOT_SCRIPT="BotFinanciero.py"
LOG_FILE="financial_bot_log.txt"
PID_FILE="${BOT_NAME}.pid"
VENV_PATH="financial-env"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a control_bot.log
}

# Función para mostrar estado
print_status() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}     BOT FINANCIERO - ESTADO ACTUAL${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Función para verificar si el bot está ejecutándose
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Función para verificar recursos del sistema
check_resources() {
    echo -e "${YELLOW}📊 Verificando recursos del sistema...${NC}"
    
    # Memoria
    MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    MEMORY_AVAILABLE=$(free -m | grep Mem | awk '{print $7}')
    
    # CPU
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    
    # Espacio en disco
    DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    DISK_AVAILABLE=$(df -h / | awk 'NR==2{print $4}')
    
    echo -e "💾 Memoria: ${MEMORY_USAGE}% usada, ${MEMORY_AVAILABLE}MB disponible"
    echo -e "🖥️  CPU: ${CPU_USAGE}% de uso"
    echo -e "💽 Disco: ${DISK_USAGE}% usado, ${DISK_AVAILABLE} disponible"
    
    # Verificar límites críticos
    if (( $(echo "$MEMORY_USAGE > 85" | bc -l) )); then
        echo -e "${RED}⚠️  ADVERTENCIA: Uso de memoria alto (${MEMORY_USAGE}%)${NC}"
    fi
    
    if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
        echo -e "${RED}⚠️  ADVERTENCIA: Uso de CPU alto (${CPU_USAGE}%)${NC}"
    fi
    
    if [ "$DISK_USAGE" -gt 90 ]; then
        echo -e "${RED}⚠️  ADVERTENCIA: Espacio en disco bajo (${DISK_USAGE}%)${NC}"
    fi
}

# Función para configurar entorno virtual
setup_environment() {
    echo -e "${YELLOW}🔧 Configurando entorno virtual...${NC}"
    
    if [ ! -d "$VENV_PATH" ]; then
        log "Creando entorno virtual..."
        python3 -m venv $VENV_PATH
    fi
    
    source $VENV_PATH/bin/activate
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias
    log "Instalando dependencias..."
    pip install yfinance pandas numpy scikit-learn requests pytz
    
    echo -e "${GREEN}✅ Entorno configurado correctamente${NC}"
}

# Función para iniciar el bot
start_bot() {
    print_status
    
    if is_running; then
        echo -e "${YELLOW}⚠️  El bot ya está ejecutándose (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}🚀 Iniciando Bot Financiero...${NC}"
    
    # Verificar archivos necesarios
    if [ ! -f "$BOT_SCRIPT" ]; then
        echo -e "${RED}❌ Error: $BOT_SCRIPT no encontrado${NC}"
        return 1
    fi
    
    if [ ! -f "config_financiero.py" ]; then
        echo -e "${RED}❌ Error: config_financiero.py no encontrado${NC}"
        echo -e "${YELLOW}💡 Configura el archivo antes de continuar${NC}"
        return 1
    fi
    
    # Verificar recursos antes de iniciar
    check_resources
    
    # Configurar entorno si es necesario
    if [ ! -d "$VENV_PATH" ]; then
        setup_environment
    fi
    
    # Activar entorno virtual
    source $VENV_PATH/bin/activate
    
    # Iniciar bot en background
    nohup python3 $BOT_SCRIPT > bot_output.log 2>&1 &
    BOT_PID=$!
    
    # Guardar PID
    echo $BOT_PID > $PID_FILE
    
    # Esperar un momento para verificar que se inició correctamente
    sleep 3
    
    if is_running; then
        log "Bot iniciado correctamente (PID: $BOT_PID)"
        echo -e "${GREEN}✅ Bot Financiero iniciado exitosamente${NC}"
        echo -e "${GREEN}📊 PID: $BOT_PID${NC}"
        echo -e "${GREEN}📝 Logs: $LOG_FILE${NC}"
        return 0
    else
        echo -e "${RED}❌ Error: El bot no se pudo iniciar${NC}"
        echo -e "${YELLOW}🔍 Revisa bot_output.log para más detalles${NC}"
        return 1
    fi
}

# Función para detener el bot
stop_bot() {
    print_status
    
    if ! is_running; then
        echo -e "${YELLOW}⚠️  El bot no está ejecutándose${NC}"
        return 1
    fi
    
    PID=$(cat $PID_FILE)
    echo -e "${YELLOW}🛑 Deteniendo Bot Financiero (PID: $PID)...${NC}"
    
    # Intentar detención suave
    kill $PID
    
    # Esperar hasta 10 segundos
    for i in {1..10}; do
        if ! is_running; then
            break
        fi
        sleep 1
    done
    
    # Si aún está ejecutándose, forzar detención
    if is_running; then
        echo -e "${YELLOW}⚡ Forzando detención...${NC}"
        kill -9 $PID
        sleep 2
    fi
    
    # Limpiar archivo PID
    rm -f $PID_FILE
    
    if ! is_running; then
        log "Bot detenido correctamente"
        echo -e "${GREEN}✅ Bot Financiero detenido${NC}"
        return 0
    else
        echo -e "${RED}❌ Error: No se pudo detener el bot${NC}"
        return 1
    fi
}

# Función para reiniciar el bot
restart_bot() {
    echo -e "${YELLOW}🔄 Reiniciando Bot Financiero...${NC}"
    stop_bot
    sleep 2
    start_bot
}

# Función para mostrar estado del bot
status_bot() {
    print_status
    
    if is_running; then
        PID=$(cat $PID_FILE)
        echo -e "${GREEN}✅ Bot Financiero está ejecutándose${NC}"
        echo -e "${GREEN}📊 PID: $PID${NC}"
        
        # Mostrar información del proceso
        echo -e "${BLUE}📈 Información del proceso:${NC}"
        ps -p $PID -o pid,ppid,cmd,%cpu,%mem,etime
        
        # Mostrar últimas líneas del log
        if [ -f "$LOG_FILE" ]; then
            echo -e "${BLUE}📝 Últimas líneas del log:${NC}"
            tail -5 $LOG_FILE
        fi
    else
        echo -e "${RED}❌ Bot Financiero no está ejecutándose${NC}"
    fi
    
    # Mostrar recursos del sistema
    echo ""
    check_resources
    
    # Mostrar información de archivos
    echo -e "${BLUE}📁 Información de archivos:${NC}"
    if [ -f "$LOG_FILE" ]; then
        LOG_SIZE=$(du -h $LOG_FILE | cut -f1)
        LOG_LINES=$(wc -l < $LOG_FILE)
        echo -e "📝 Log: $LOG_FILE (${LOG_SIZE}, ${LOG_LINES} líneas)"
    fi
    
    if [ -f "bot_output.log" ]; then
        OUTPUT_SIZE=$(du -h bot_output.log | cut -f1)
        echo -e "📄 Output: bot_output.log (${OUTPUT_SIZE})"
    fi
}

# Función para mostrar logs en tiempo real
logs_bot() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}📝 Mostrando logs en tiempo real (Ctrl+C para salir)...${NC}"
        tail -f $LOG_FILE
    else
        echo -e "${YELLOW}⚠️  Archivo de log no encontrado: $LOG_FILE${NC}"
    fi
}

# Función para limpiar logs antiguos
clean_logs() {
    echo -e "${YELLOW}🧹 Limpiando logs antiguos...${NC}"
    
    # Hacer backup de logs actuales
    if [ -f "$LOG_FILE" ]; then
        mv $LOG_FILE "${LOG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✅ Backup creado: ${LOG_FILE}.backup.$(date +%Y%m%d_%H%M%S)${NC}"
    fi
    
    if [ -f "bot_output.log" ]; then
        mv bot_output.log "bot_output.log.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Limpiar logs antiguos (más de 7 días)
    find . -name "*.log.backup.*" -mtime +7 -delete
    
    echo -e "${GREEN}✅ Logs limpiados${NC}"
}

# Función para monitoreo automático
monitor_bot() {
    echo -e "${BLUE}🔍 Iniciando monitoreo automático...${NC}"
    echo -e "${YELLOW}Presiona Ctrl+C para detener el monitoreo${NC}"
    
    while true; do
        clear
        echo -e "${BLUE}🕐 $(date '+%Y-%m-%d %H:%M:%S')${NC}"
        status_bot
        
        # Verificar si el bot sigue ejecutándose
        if ! is_running; then
            echo -e "${RED}💥 ¡Bot se detuvo inesperadamente!${NC}"
            echo -e "${YELLOW}🔧 Intentando reiniciar...${NC}"
            start_bot
        fi
        
        echo -e "${YELLOW}Próxima verificación en 60 segundos...${NC}"
        sleep 60
    done
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}🤖 Control del Bot Financiero${NC}"
    echo ""
    echo "Uso: $0 {start|stop|restart|status|logs|monitor|clean|setup|help}"
    echo ""
    echo "Comandos:"
    echo "  start    - Iniciar el bot"
    echo "  stop     - Detener el bot"
    echo "  restart  - Reiniciar el bot"
    echo "  status   - Mostrar estado del bot y recursos"
    echo "  logs     - Mostrar logs en tiempo real"
    echo "  monitor  - Monitoreo automático continuo"
    echo "  clean    - Limpiar logs antiguos"
    echo "  setup    - Configurar entorno virtual"
    echo "  help     - Mostrar esta ayuda"
    echo ""
    echo "Archivos:"
    echo "  $BOT_SCRIPT - Script principal del bot"
    echo "  config_financiero.py - Configuración del bot"
    echo "  $LOG_FILE - Log principal"
    echo "  $PID_FILE - Archivo PID"
    echo ""
}

# Función principal
main() {
    case "$1" in
        start)
            start_bot
            ;;
        stop)
            stop_bot
            ;;
        restart)
            restart_bot
            ;;
        status)
            status_bot
            ;;
        logs)
            logs_bot
            ;;
        monitor)
            monitor_bot
            ;;
        clean)
            clean_logs
            ;;
        setup)
            setup_environment
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Comando no reconocido: $1${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Verificar si se ejecuta con argumentos
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Ejecutar función principal
main "$1"