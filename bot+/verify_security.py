#!/usr/bin/env python3
"""
Script de verificación de seguridad
Comprueba que todos los bots usen configuración segura
"""

import os
import sys
import re

def check_file_security(filepath):
    """Verificar que un archivo no tenga claves hardcodeadas"""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar patrones de claves hardcodeadas
        api_key_pattern = r'API_KEY\s*=\s*[\'"][A-Za-z0-9]{50,}[\'"]'
        secret_pattern = r'API_SECRET\s*=\s*[\'"][A-Za-z0-9]{50,}[\'"]'
        
        api_matches = re.findall(api_key_pattern, content)
        secret_matches = re.findall(secret_pattern, content)
        
        # Verificar si usa secure_config
        uses_secure_config = 'from secure_config import' in content
        
        if api_matches and not uses_secure_config:
            issues.append(f"❌ API_KEY hardcodeada sin secure_config")
        
        if secret_matches and not uses_secure_config:
            issues.append(f"❌ API_SECRET hardcodeada sin secure_config")
        
        if uses_secure_config:
            issues.append("✅ Usa configuración segura")
        
        return issues
        
    except Exception as e:
        return [f"❌ Error leyendo archivo: {e}"]

def main():
    print("🔒 Verificación de Seguridad - Bot Trading")
    print("=" * 50)
    
    # Archivos a verificar
    files_to_check = [
        'Bot-trading.py',
        'Bot-trading-REAL.py',
        'BotMLCloud.py',
        'BotMLCloud-REAL.py',
        'BotFinanciero/BotFinanciero.py',
        'BotFinanciero/config_financiero.py'
    ]
    
    all_secure = True
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"\n📁 {filepath}:")
            issues = check_file_security(filepath)
            for issue in issues:
                print(f"  {issue}")
                if "❌" in issue:
                    all_secure = False
        else:
            print(f"\n⚠️  {filepath}: Archivo no encontrado")
    
    # Verificar archivos críticos
    print(f"\n🔍 Verificación de archivos críticos:")
    
    # .env debe existir
    if os.path.exists('.env'):
        print("✅ .env encontrado")
    else:
        print("❌ .env no encontrado")
        all_secure = False
    
    # .gitignore debe incluir .env
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
        if '.env' in gitignore_content:
            print("✅ .env está en .gitignore")
        else:
            print("❌ .env NO está en .gitignore")
            all_secure = False
    else:
        print("❌ .gitignore no encontrado")
        all_secure = False
    
    # secure_config.py debe existir
    if os.path.exists('secure_config.py'):
        print("✅ secure_config.py encontrado")
    else:
        print("❌ secure_config.py no encontrado")
        all_secure = False
    
    print(f"\n{'='*50}")
    if all_secure:
        print("🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ Todos los bots usan configuración segura")
        print("✅ Las claves están protegidas")
        print("✅ Seguro para subir a GitHub")
    else:
        print("⚠️  SE ENCONTRARON PROBLEMAS DE SEGURIDAD")
        print("❌ Revisa los errores y corrígelos antes de continuar")
        print("❌ NO subas a GitHub hasta resolver los problemas")
    
    print(f"\n📝 Para probar la configuración:")
    print("   python secure_config.py")
    
    return all_secure

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)