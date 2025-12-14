# Script de verificación para Documents Service en Windows PowerShell
Write-Host "🔍 Verificando configuración del Documents Service..." -ForegroundColor Green

# Verificar que estamos en el directorio correcto
$currentPath = Get-Location
Write-Host "📂 Directorio actual: $currentPath" -ForegroundColor Blue

# Verificar estructura de archivos
Write-Host "`n📂 Verificando estructura de archivos..." -ForegroundColor Yellow

$requiredFiles = @(
    "server-sacra360\Documents-service\Dockerfile",
    "server-sacra360\Documents-service\requirements.txt",
    "server-sacra360\Documents-service\.env.example",
    "server-sacra360\Documents-service\app\main.py",
    "server-sacra360\Documents-service\app\database.py",
    "server-sacra360\Documents-service\app\models\__init__.py",
    "server-sacra360\Documents-service\app\controllers\persona_controller.py",
    "server-sacra360\Documents-service\app\controllers\libro_controller.py",
    "server-sacra360\Documents-service\app\services\persona_service.py",
    "server-sacra360\Documents-service\app\services\libro_service.py",
    "server-sacra360\Documents-service\app\dto\persona_dto.py",
    "server-sacra360\Documents-service\app\dto\libro_dto.py",
    "server-sacra360\Documents-service\app\entities\persona.py",
    "server-sacra360\Documents-service\app\entities\libro.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ FALTA: $file" -ForegroundColor Red
    }
}

Write-Host "`n🐳 Configuración de Docker:" -ForegroundColor Cyan
Write-Host "- Puerto del servicio: 8002" -ForegroundColor White
Write-Host "- Base de datos: PostgreSQL en puerto 5432" -ForegroundColor White
Write-Host "- Credenciales BD: postgres:lolsito101@postgres:5432/sacra360" -ForegroundColor White
Write-Host "- Redis: redis:6379" -ForegroundColor White

Write-Host "`n🚀 Para probar el microservicio:" -ForegroundColor Magenta
Write-Host "1. Abrir PowerShell como Administrador" -ForegroundColor White
Write-Host "2. cd al directorio BACKEND\" -ForegroundColor White
Write-Host "3. docker-compose up -d postgres redis" -ForegroundColor White
Write-Host "4. docker-compose up --build documents-service" -ForegroundColor White
Write-Host "5. Visitar: http://localhost:8002/docs" -ForegroundColor White

Write-Host "`n🔧 Endpoints disponibles:" -ForegroundColor Yellow
Write-Host "- GET http://localhost:8002/health - Health check" -ForegroundColor White
Write-Host "- GET http://localhost:8002/docs - Documentación Swagger" -ForegroundColor White
Write-Host "- GET http://localhost:8002/ - Info del servicio" -ForegroundColor White
Write-Host "- API Personas: http://localhost:8002/api/v1/personas/" -ForegroundColor White
Write-Host "- API Libros: http://localhost:8002/api/v1/libros/" -ForegroundColor White

Write-Host "`n📝 Para crear archivo .env (copia de .env.example):" -ForegroundColor Cyan
Write-Host "Copy-Item server-sacra360\Documents-service\.env.example server-sacra360\Documents-service\.env" -ForegroundColor White

Write-Host "`n✅ Verificación completada!" -ForegroundColor Green

# Verificar si Docker está instalado
try {
    $dockerVersion = docker --version
    Write-Host "`n🐳 Docker detectado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "`n❌ Docker no está instalado o no está en el PATH" -ForegroundColor Red
}

# Verificar si docker-compose está disponible
try {
    $composeVersion = docker-compose --version
    Write-Host "🐳 Docker Compose detectado: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose no está instalado o no está en el PATH" -ForegroundColor Red
}