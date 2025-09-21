# Instrucciones de Deployment - Bot Financiero en Google Cloud
# Fecha: 21 septiembre 2025

## PREPARACIÓN PARA GOOGLE CLOUD VM

### 1. ARCHIVOS NECESARIOS PARA UPLOAD:
```
- BotFinanciero.py (bot principal)
- config_financiero.py (configuración - COMPLETA LOS TOKENS)
- control_financiero.sh (script de control)
- requirements.txt (dependencias)
- deploy_setup.sh (configuración automática)
```

### 2. CONFIGURACIÓN PREVIA:

#### A. Crear Bot de Telegram:
1. Busca @BotFather en Telegram
2. Escribe /newbot
3. Elige nombre: "Financial Trading Bot"
4. Elige username: "tu_financial_bot"
5. Copia el TOKEN

#### B. Obtener Chat ID:
1. Busca @userinfobot en Telegram
2. Escribe /start
3. Copia tu Chat ID

#### C. Editar config_financiero.py:
```python
TELEGRAM_TOKEN = "tu_token_aqui"
CHAT_ID = "tu_chat_id_aqui"
```

### 3. COMANDO PARA DEPLOYMENT EN VM1:

```bash
# Conectar a VM1
gcloud compute ssh bot-trading-asia --zone=asia-southeast1-a

# Subir archivos (desde tu PC)
gcloud compute scp *.py bot-trading-asia:~/financial-bot/ --zone=asia-southeast1-a
gcloud compute scp *.sh bot-trading-asia:~/financial-bot/ --zone=asia-southeast1-a

# En la VM, ejecutar:
cd ~/financial-bot
chmod +x *.sh
./deploy_setup.sh
```

### 4. COMANDOS DE CONTROL:

```bash
# Iniciar bot
./control_financiero.sh start

# Ver estado
./control_financiero.sh status

# Ver logs en tiempo real
./control_financiero.sh logs

# Monitoreo automático
./control_financiero.sh monitor

# Reiniciar si hay problemas
./control_financiero.sh restart
```

### 5. VERIFICACIÓN POST-DEPLOYMENT:

#### A. Verificar recursos:
- Memoria disponible: ~350MB mínimo
- CPU: Menos del 50% en promedio
- Disco: Menos del 80%

#### B. Verificar funcionamiento:
- Mensaje de inicio en Telegram
- Logs generándose correctamente
- Análisis cada 5 minutos durante horario de mercado

#### C. Monitoreo 24h:
- Bot responde a señales de trading
- Notificaciones por Telegram funcionando
- Sin errores críticos en logs

### 6. CONFIGURACIÓN AVANZADA:

#### A. Horarios optimizados:
- Análisis intensivo: 9:30-16:00 EST (mercado abierto)
- Análisis básico: 16:00-9:30 EST (mercado cerrado)
- Mantenimiento: Domingos 2:00-4:00 EST

#### B. Gestión de recursos:
- Límite memoria: 300MB máximo
- Límite CPU: 50% promedio
- Rotación de logs: Cada 7 días

#### C. Alertas automáticas:
- Notificación si bot se detiene
- Alerta por alto uso de recursos
- Resumen diario de performance

### 7. TROUBLESHOOTING:

#### Problema: Bot no inicia
```bash
# Verificar logs
cat bot_output.log
cat financial_bot_log.txt

# Verificar configuración
python3 -c "from config_financiero import *; print('Config OK')"

# Reinstalar dependencias
./control_financiero.sh setup
```

#### Problema: Sin notificaciones Telegram
```bash
# Verificar token
curl https://api.telegram.org/bot<TOKEN>/getMe

# Verificar chat ID
# Envía mensaje a tu bot y verifica
```

#### Problema: Alto uso de memoria
```bash
# Verificar procesos
./control_financiero.sh status

# Reiniciar si necesario
./control_financiero.sh restart

# Limpiar logs
./control_financiero.sh clean
```

### 8. MANTENIMIENTO REGULAR:

#### Diario:
- Verificar estado general
- Revisar alertas de Telegram
- Verificar P&L de trades simulados

#### Semanal:
- Limpiar logs antiguos
- Verificar accuracy del modelo ML
- Ajustar parámetros si necesario

#### Mensual:
- Reentrenar modelo ML con datos nuevos
- Revisar performance vs mercado
- Optimizar configuraciones

### 9. ESCALAMIENTO FUTURO:

#### Recursos adicionales necesarios para:
- Más acciones (+50MB por cada 10 símbolos)
- Trading real (+100MB para gestión de órdenes)
- Múltiples mercados (+150MB por mercado)

#### Posibles mejoras:
- Integración con APIs de brokers reales
- Dashboard web para monitoreo
- Backtesting automatizado
- Análisis de noticias con NLP

### 10. COMANDOS ÚTILES DE MONITOREO:

```bash
# Ver uso de recursos en tiempo real
htop

# Ver logs específicos por fecha
grep "$(date +%Y-%m-%d)" financial_bot_log.txt

# Estadísticas de trading
grep "TRADE SIMULADO" financial_bot_log.txt | wc -l

# Verificar conectividad
ping -c 3 google.com

# Espacio en disco
df -h

# Procesos activos del bot
ps aux | grep BotFinanciero
```