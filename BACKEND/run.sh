#!/bin/bash

# Script para ejecutar la API de Sacra360
# Para Windows, ejecutar desde Git Bash o usar PowerShell equivalente

echo "🚀 Iniciando Sacra360 API..."

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate  # Para Linux/Mac
# En Windows usar: venv\Scripts\activate

# Instalar dependencias si no están instaladas
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Verificar que el archivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado. Usando configuración por defecto."
fi

# Ejecutar la aplicación
echo "🌟 Iniciando servidor de desarrollo..."
echo "📍 La API estará disponible en: http://localhost:8000"
echo "📖 Documentación en: http://localhost:8000/docs"
echo "🔍 ReDoc en: http://localhost:8000/redoc"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000