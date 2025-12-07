# Script de verificacion de requisitos para OCR con GPU
# Uso: .\check_requirements.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "VERIFICACION DE REQUISITOS - OCR CON GPU" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$allChecks = @()

# 1. Verificar Drivers NVIDIA
Write-Host "1. Verificando drivers NVIDIA..." -ForegroundColor Yellow
try {
    $nvidiaOutput = nvidia-smi 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Drivers NVIDIA instalados" -ForegroundColor Green
        $allChecks += @{Name="Drivers NVIDIA"; Status="OK"}
    }
} catch {
    Write-Host "   [FAIL] Drivers NVIDIA no detectados" -ForegroundColor Red
    Write-Host "   Instalar desde: https://www.nvidia.com/Download/index.aspx" -ForegroundColor Yellow
    $allChecks += @{Name="Drivers NVIDIA"; Status="FAIL"}
}
Write-Host ""

# 2. Verificar Docker
Write-Host "2. Verificando Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Docker instalado: $dockerVersion" -ForegroundColor Green
        $allChecks += @{Name="Docker"; Status="OK"}
    }
} catch {
    Write-Host "   [FAIL] Docker no instalado" -ForegroundColor Red
    Write-Host "   Instalar Docker Desktop desde: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    $allChecks += @{Name="Docker"; Status="FAIL"}
}
Write-Host ""

# 3. Verificar Docker Compose
Write-Host "3. Verificando Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Docker Compose instalado: $composeVersion" -ForegroundColor Green
        $allChecks += @{Name="Docker Compose"; Status="OK"}
    }
} catch {
    Write-Host "   [FAIL] Docker Compose no instalado" -ForegroundColor Red
    $allChecks += @{Name="Docker Compose"; Status="FAIL"}
}
Write-Host ""

# 4. Verificar soporte GPU en Docker
Write-Host "4. Verificando soporte GPU en Docker..." -ForegroundColor Yellow
try {
    Write-Host "   Probando contenedor CUDA..." -ForegroundColor Gray
    $cudaTest = docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   [OK] Docker puede acceder a GPU" -ForegroundColor Green
        $allChecks += @{Name="Docker GPU Support"; Status="OK"}
    } else {
        throw "GPU no accesible"
    }
} catch {
    Write-Host "   [FAIL] Docker no puede acceder a GPU" -ForegroundColor Red
    Write-Host "   Necesitas NVIDIA Container Toolkit" -ForegroundColor Yellow
    Write-Host "   Ver: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html" -ForegroundColor Yellow
    $allChecks += @{Name="Docker GPU Support"; Status="FAIL"}
}
Write-Host ""

# 5. Verificar archivos del proyecto
Write-Host "5. Verificando archivos del proyecto..." -ForegroundColor Yellow
$projectFiles = @(
    "server-sacra360\OCR-service\Dockerfile",
    "server-sacra360\OCR-service\requirements.txt",
    "server-sacra360\OCR-service\app\ocr_gpu_processor.py",
    "docker-compose.yml"
)

$filesOk = $true
foreach ($file in $projectFiles) {
    if (Test-Path $file) {
        Write-Host "   [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] $file no encontrado" -ForegroundColor Red
        $filesOk = $false
    }
}

if ($filesOk) {
    $allChecks += @{Name="Archivos del proyecto"; Status="OK"}
} else {
    $allChecks += @{Name="Archivos del proyecto"; Status="FAIL"}
}
Write-Host ""

# Resumen
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

$passed = ($allChecks | Where-Object { $_.Status -eq "OK" }).Count
$failed = ($allChecks | Where-Object { $_.Status -eq "FAIL" }).Count
$total = $allChecks.Count

Write-Host "Verificaciones pasadas: $passed/$total" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })

if ($failed -eq 0) {
    Write-Host ""
    Write-Host "[OK] Todos los requisitos cumplidos!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximos pasos:" -ForegroundColor Cyan
    Write-Host "  1. docker-compose build ocr-service" -ForegroundColor White
    Write-Host "  2. docker-compose up ocr-service" -ForegroundColor White
    Write-Host "  3. curl http://localhost:8003/ocr-gpu/gpu-status" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "[WARN] Hay requisitos faltantes. Revisa los errores arriba." -ForegroundColor Red
    Write-Host ""
    Write-Host "Documentacion completa:" -ForegroundColor Cyan
    Write-Host "  server-sacra360/OCR-service/README_GPU.md" -ForegroundColor White
}

Write-Host ""
