#!/bin/bash
# 🤖 Script de Monitoreo del Bot ML
# Ejecuta verificaciones completas del bot de machine learning

echo "🤖 MONITOR BOT ML - $(date)"
echo "=================================="

# Verificar procesos Python
echo "📊 Procesos Python ejecutándose:"
gcloud compute ssh rodrigomd123456@bot-trading-ml --zone=asia-southeast1-a --command="ps aux | grep python | grep -v grep"

echo ""
echo "📺 Sesiones Screen activas:"
gcloud compute ssh rodrigomd123456@bot-trading-ml --zone=asia-southeast1-a --command="screen -ls"

echo ""
echo "📁 Información de logs:"
gcloud compute ssh rodrigomd123456@bot-trading-ml --zone=asia-southeast1-a --command="ls -lh *log*.txt"

echo ""
echo "🔄 Últimas 10 líneas de actividad:"
gcloud compute ssh rodrigomd123456@bot-trading-ml --zone=asia-southeast1-a --command="tail -10 ml_bot_log.txt"

echo ""
echo "💰 Estadísticas de trading:"
gcloud compute ssh rodrigomd123456@bot-trading-ml --zone=asia-southeast1-a --command="echo 'Trades totales:'; grep -c 'BUY\|SELL' ml_bot_log.txt || echo '0'"

echo ""
echo "🚨 Errores recientes:"
gcloud compute ssh rodrigomd123456@bot-trading-ml --zone=asia-southeast1-a --command="grep -i 'error\|exception' ml_bot_log.txt | tail -5 || echo 'Sin errores recientes'"

echo ""
echo "✅ Verificación completada - $(date)"