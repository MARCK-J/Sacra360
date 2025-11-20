#!/usr/bin/env python3
"""
Script para ejecutar el OCR Service - Sacra360
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Función principal para ejecutar el servicio"""
    
    # Configuración del servidor
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8003))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    print("🚀 Iniciando OCR Service - Sacra360")
    print(f"   📍 Host: {host}")
    print(f"   🔌 Puerto: {port}")
    print(f"   🔄 Reload: {reload}")
    print(f"   📊 Log Level: {log_level}")
    print(f"   📚 Docs: http://{host}:{port}/docs")
    print("-" * 50)
    
    try:
        # Ejecutar servidor
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except Exception as e:
        print(f"❌ Error al iniciar el servicio: {e}")
        print("💡 Asegúrate de estar en el directorio correcto del OCR-service")

if __name__ == "__main__":
    main()