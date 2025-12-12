"""
Script para ejecutar HTR Service localmente con modelo HTR_Sacra360
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

logger.info("=" * 70)
logger.info("🚀 Iniciando HTR Service con HTR_Sacra360")
logger.info("=" * 70)
logger.info(f"📍 Puerto: {os.getenv('SERVICE_PORT', '8004')}")
logger.info(f"💾 Database: {os.getenv('DATABASE_URL', 'No configurado')}")
logger.info(f"☁️  MinIO: {os.getenv('MINIO_ENDPOINT', 'No configurado')}")
logger.info("=" * 70)

# Importar FastAPI app
from app.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv('SERVICE_PORT', 8004)),
        log_level="info"
    )
