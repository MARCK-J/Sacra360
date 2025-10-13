# Script PowerShell para ejecutar la API de Sacra360

Write-Host "🚀 Iniciando Sacra360 API..." -ForegroundColor Green

# Verificar si el entorno virtual existe
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Activar entorno virtual
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Instalar dependencias
Write-Host "📚 Instalando dependencias..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verificar que el archivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Archivo .env no encontrado. Usando configuración por defecto." -ForegroundColor Yellow
}

# Ejecutar la aplicación
Write-Host "🌟 Iniciando servidor de desarrollo..." -ForegroundColor Green
Write-Host "📍 La API estará disponible en: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 Documentación en: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🔍 ReDoc en: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000