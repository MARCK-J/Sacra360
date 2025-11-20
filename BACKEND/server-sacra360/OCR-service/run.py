"""
Script para ejecutar el microservicio OCR
"""

import uvicorn
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # Configuración para desarrollo
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8003,
        reload=True,
        log_level="info",
        access_log=True
    )