#!/bin/bash
# 🔧 Script de Control Remoto del Bot ML
# Permite reiniciar, detener y gestionar el bot ML

ZONE="asia-southeast1-a"
VM_NAME="rodrigomd123456@bot-trading-ml"

case "$1" in
    "status")
        echo "📊 Estado del Bot ML:"
        gcloud compute ssh $VM_NAME --zone=$ZONE --command="ps aux | grep BotMLCloud"
        ;;
    "logs")
        echo "📋 Logs en tiempo real (Ctrl+C para salir):"
        gcloud compute ssh $VM_NAME --zone=$ZONE --command="tail -f ml_bot_log.txt"
        ;;
    "restart")
        echo "🔄 Reiniciando Bot ML..."
        gcloud compute ssh $VM_NAME --zone=$ZONE --command="pkill -f BotMLCloud; screen -S bot-ml -dm python3 BotMLCloud.py"
        echo "✅ Bot ML reiniciado"
        ;;
    "download-logs")
        echo "📥 Descargando logs..."
        gcloud compute scp $VM_NAME:~/ml_bot_log.txt ./ml_bot_log_$(date +%Y%m%d_%H%M).txt --zone=$ZONE
        echo "✅ Logs descargados"
        ;;
    "stats")
        echo "📈 Estadísticas del Bot ML:"
        gcloud compute ssh $VM_NAME --zone=$ZONE --command="
            echo 'Archivo de logs:';
            ls -lh ml_bot_log.txt;
            echo '';
            echo 'Trades realizados:';
            grep -c 'BUY\|SELL' ml_bot_log.txt;
            echo '';
            echo 'Última actividad:';
            tail -3 ml_bot_log.txt;
        "
        ;;
    *)
        echo "🤖 Control del Bot ML"
        echo "Uso: $0 {status|logs|restart|download-logs|stats}"
        echo ""
        echo "Comandos disponibles:"
        echo "  status       - Ver si el bot está ejecutándose"
        echo "  logs         - Ver logs en tiempo real"
        echo "  restart      - Reiniciar el bot"
        echo "  download-logs - Descargar logs localmente"
        echo "  stats        - Ver estadísticas de trading"
        ;;
esac