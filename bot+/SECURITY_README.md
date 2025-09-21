# 🔒 Sistema de Configuración Segura

## ¿Por qué es importante?

❌ **ANTES:** Las claves API estaban hardcodeadas en los archivos Python  
✅ **AHORA:** Las claves se manejan de forma segura con variables de entorno

## 🚀 Configuración rápida

### 1. Instalar dependencias
```bash
chmod +x install_security.sh
./install_security.sh
```

### 2. Configurar variables de entorno
Edita el archivo `.env` y completa tus claves reales:

```bash
# Ejemplo de .env
ENVIRONMENT=TESTNET  # o PRODUCTION

# Binance API Keys
BINANCE_API_KEY_PROD=tu_clave_api_real
BINANCE_SECRET_KEY_PROD=tu_clave_secreta_real

# Telegram
TELEGRAM_TOKEN_FINANCIAL=tu_token_telegram
TELEGRAM_CHAT_ID=tu_chat_id
```

### 3. Probar configuración
```bash
python secure_config.py
```

### 4. Ejecutar bots
Los bots ahora cargan automáticamente las claves de forma segura:
```bash
python Bot-trading-REAL.py
python BotMLCloud-REAL.py
python BotFinanciero/BotFinanciero.py
```

## 🛡️ Características de seguridad

### ✅ Variables de entorno
- Las claves se guardan en `.env` (no en GitHub)
- Carga automática con `python-dotenv`
- Fallback a configuración local si falla

### ✅ Protección Git
- `.gitignore` incluye `.env` y archivos sensibles
- Nunca se suben claves a repositorios

### ✅ Verificación de ambiente
- Modo TESTNET vs PRODUCTION
- Confirmación antes de usar dinero real
- Logs que no muestran claves completas

### ✅ Configuración centralizada
- Un solo archivo `secure_config.py` maneja todo
- Fácil cambio entre testnet y producción
- Validación automática de variables críticas

## 📁 Estructura de archivos

```
bot+/
├── .env                    ← Claves API (NO SUBIR A GIT)
├── .gitignore             ← Protección Git
├── secure_config.py       ← Manejador de configuración
├── install_security.sh    ← Script de instalación
├── Bot-trading-REAL.py    ← Usa configuración segura
├── BotMLCloud-REAL.py     ← Usa configuración segura
└── BotFinanciero/
    ├── BotFinanciero.py   ← Usa configuración segura
    └── config_financiero.py ← Actualizado para .env
```

## 🔧 Configuración avanzada

### Ambientes múltiples
```bash
# Para desarrollo
ENVIRONMENT=TESTNET

# Para producción
ENVIRONMENT=PRODUCTION
```

### Claves múltiples
```bash
# Crypto bots
BINANCE_API_KEY_PROD=...
BINANCE_SECRET_KEY_PROD=...

# Telegram bots
TELEGRAM_TOKEN_FINANCIAL=...
TELEGRAM_TOKEN_CRYPTO=...
```

### Configuración GCP
```bash
GCP_PROJECT_ID=tu-proyecto
GCP_ZONE=asia-southeast1-a
GCP_VM_CRYPTO=bot-trading-asia
```

## 🚨 Medidas de seguridad adicionales

### 1. Backup seguro del .env
```bash
# Crear backup encriptado
cp .env .env.backup
gpg -c .env.backup  # Encriptar con contraseña
rm .env.backup      # Eliminar backup sin encriptar
```

### 2. Verificación antes de commits
```bash
# Siempre verificar antes de commit
git status
grep -r "API_KEY\|SECRET_KEY" *.py  # No debe mostrar claves
```

### 3. Rotación de claves
- Cambia las claves API periódicamente
- Usa claves diferentes para desarrollo y producción
- Revoca claves comprometidas inmediatamente

## 🔍 Troubleshooting

### Error: "Variable requerida no encontrada"
```bash
# Verificar archivo .env
ls -la .env
cat .env | grep BINANCE_API_KEY_PROD
```

### Error: "python-dotenv no instalado"
```bash
pip install python-dotenv
```

### Error: "secure_config no disponible"
```bash
# Verificar ubicación del archivo
ls -la secure_config.py
# El archivo debe estar en el mismo directorio que los bots
```

## 📞 Deployment en Google Cloud

### 1. Subir archivos (SIN .env)
```bash
gcloud compute scp *.py bot-trading-asia: --zone=asia-southeast1-a
gcloud compute scp BotFinanciero/*.py bot-trading-asia:~/financial-bot/ --zone=asia-southeast1-a
```

### 2. Crear .env en la VM
```bash
gcloud compute ssh bot-trading-asia --zone=asia-southeast1-a
nano .env  # Crear y configurar en la VM
```

### 3. Configurar variables de entorno del sistema (alternativa)
```bash
export BINANCE_API_KEY_PROD="tu_clave_aqui"
export BINANCE_SECRET_KEY_PROD="tu_clave_secreta_aqui"
```

## ✅ Checklist de seguridad

- [ ] `.env` configurado con claves reales
- [ ] `.env` incluido en `.gitignore`
- [ ] `python-dotenv` instalado
- [ ] Configuración probada con `python secure_config.py`
- [ ] Bots funcionando con nuevas claves
- [ ] Claves API anteriores removidas del código
- [ ] Verificado que no se suben claves a Git

---

**🔐 ¡Ahora tus claves API están protegidas y tu código es seguro para GitHub!**