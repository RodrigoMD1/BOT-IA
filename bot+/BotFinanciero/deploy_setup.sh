#!/bin/bash
# Script de Configuración Automática para Bot Financiero
# Ejecutar en Google Cloud VM

echo "🚀 Configurando Bot Financiero en Google Cloud VM..."

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python y pip si no están instalados
echo "🐍 Verificando Python..."
sudo apt install -y python3 python3-pip python3-venv

# Crear directorio para el bot si no existe
mkdir -p ~/financial-bot
cd ~/financial-bot

# Crear entorno virtual
echo "🔧 Creando entorno virtual..."
python3 -m venv financial-env
source financial-env/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install yfinance pandas numpy scikit-learn requests pytz

# Crear archivo requirements.txt
cat > requirements.txt << EOF
yfinance>=0.2.18
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
requests>=2.31.0
pytz>=2023.3
EOF

# Hacer ejecutables los scripts
chmod +x *.sh

# Crear estructura de directorios
mkdir -p logs backups

# Configurar logrotate para gestión de logs
sudo tee /etc/logrotate.d/financial-bot > /dev/null << EOF
/home/$(whoami)/financial-bot/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $(whoami) $(whoami)
}
EOF

# Configurar firewall (si es necesario)
echo "🔒 Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw --force enable

# Verificar configuración
echo "✅ Verificando configuración..."

# Verificar Python
python3 --version

# Verificar dependencias
python3 -c "
import yfinance as yf
import pandas as pd
import numpy as np
import sklearn
import requests
import pytz
print('✅ Todas las dependencias instaladas correctamente')
"

# Verificar archivo de configuración
if [ -f "config_financiero.py" ]; then
    echo "✅ Archivo de configuración encontrado"
    
    # Verificar que no tenga valores por defecto
    if grep -q "YOUR_TELEGRAM_BOT_TOKEN_HERE" config_financiero.py; then
        echo "⚠️  ADVERTENCIA: Debes configurar TELEGRAM_TOKEN en config_financiero.py"
    fi
    
    if grep -q "YOUR_CHAT_ID_HERE" config_financiero.py; then
        echo "⚠️  ADVERTENCIA: Debes configurar CHAT_ID en config_financiero.py"
    fi
else
    echo "❌ ERROR: config_financiero.py no encontrado"
    echo "📝 Asegúrate de subir todos los archivos necesarios"
fi

# Crear script de inicio automático
cat > start_on_boot.sh << 'EOF'
#!/bin/bash
# Script para iniciar el bot automáticamente al reiniciar la VM

sleep 30  # Esperar que el sistema se estabilice

cd /home/$(whoami)/financial-bot
source financial-env/bin/activate

# Verificar si el bot ya está ejecutándose
if [ -f "bot_financiero.pid" ]; then
    PID=$(cat bot_financiero.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "Bot ya está ejecutándose"
        exit 0
    fi
fi

# Iniciar bot
./control_financiero.sh start

# Log del inicio automático
echo "$(date): Bot iniciado automáticamente" >> auto_start.log
EOF

chmod +x start_on_boot.sh

# Configurar crontab para inicio automático
(crontab -l 2>/dev/null; echo "@reboot /home/$(whoami)/financial-bot/start_on_boot.sh") | crontab -

# Mostrar información del sistema
echo ""
echo "📊 Información del sistema:"
echo "💾 Memoria total: $(free -h | grep Mem | awk '{print $2}')"
echo "💽 Espacio en disco: $(df -h ~ | tail -1 | awk '{print $4}') disponible"
echo "🖥️  CPU: $(nproc) cores"

# Mostrar resumen de la instalación
echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📝 Próximos pasos:"
echo "1. Editar config_financiero.py con tus tokens de Telegram"
echo "2. Ejecutar: ./control_financiero.sh start"
echo "3. Monitorear: ./control_financiero.sh status"
echo ""
echo "📚 Comandos útiles:"
echo "   ./control_financiero.sh help    - Ver todos los comandos"
echo "   ./control_financiero.sh logs    - Ver logs en tiempo real"
echo "   ./control_financiero.sh monitor - Monitoreo automático"
echo ""
echo "🔧 Archivos de configuración:"
echo "   config_financiero.py - Configuración principal"
echo "   requirements.txt     - Dependencias Python"
echo "   DEPLOYMENT_GUIDE.md  - Guía completa"
echo ""

# Verificar espacio disponible para el bot
AVAILABLE_SPACE=$(df ~ | tail -1 | awk '{print $4}')
if [ $AVAILABLE_SPACE -lt 1048576 ]; then  # Menos de 1GB
    echo "⚠️  ADVERTENCIA: Poco espacio en disco disponible"
    echo "   Considera limpiar archivos innecesarios"
fi

# Verificar memoria disponible
AVAILABLE_MEMORY=$(free -m | grep Available | awk '{print $7}')
if [ $AVAILABLE_MEMORY -lt 400 ]; then  # Menos de 400MB
    echo "⚠️  ADVERTENCIA: Poca memoria disponible"
    echo "   El bot necesita al menos 300MB para funcionar correctamente"
fi

echo ""
echo "✅ Setup completado exitosamente - Listo para iniciar el bot!"