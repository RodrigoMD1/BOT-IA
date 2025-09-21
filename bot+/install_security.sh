#!/bin/bash
# Script de instalación de dependencias para sistema seguro
# Ejecutar antes de usar los bots con configuración segura

echo "🔒 Instalando dependencias para sistema de configuración segura..."

# Instalar python-dotenv para manejo de .env
pip install python-dotenv

echo "📋 Dependencias instaladas:"
echo "✅ python-dotenv - Para manejo de variables de entorno"

echo ""
echo "📝 Próximos pasos:"
echo "1. Completa el archivo .env con tus claves reales"
echo "2. Verifica que .env esté en .gitignore"
echo "3. Ejecuta: python secure_config.py para probar la configuración"
echo "4. Los bots ahora cargarán las claves de forma segura"

echo ""
echo "⚠️  IMPORTANTE:"
echo "- Nunca subas el archivo .env a GitHub"
echo "- Mantén tus claves API seguras"
echo "- Usa ENVIRONMENT=TESTNET para pruebas"
echo "- Cambia a ENVIRONMENT=PRODUCTION solo cuando estés listo"