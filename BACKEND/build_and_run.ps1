#!/usr/bin/env pwsh
# Script para construir y ejecutar el servicio OCR con GPU
# Uso: .\build_and_run.ps1 [-BuildOnly] [-NoBuild] [-Logs]

param(
    [switch]$BuildOnly,
    [switch]$NoBuild,
    [switch]$Logs
)

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "OCR SERVICE CON GPU - BUILD & RUN" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar ubicación
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "Error: Ejecuta este script desde el directorio BACKEND/" -ForegroundColor Red
    exit 1
}

# Build
if (-not $NoBuild) {
    Write-Host "Construyendo imagen Docker..." -ForegroundColor Yellow
    Write-Host "Esto puede tomar 10-15 minutos la primera vez..." -ForegroundColor Gray
    Write-Host ""
    
    try {
        docker-compose build ocr-service
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "[OK] Imagen construida exitosamente" -ForegroundColor Green
        } else {
            throw "Error en construcción"
        }
    } catch {
        Write-Host "[FAIL] Error construyendo imagen" -ForegroundColor Red
        exit 1
    }
}

if ($BuildOnly) {
    Write-Host ""
    Write-Host "Construcción completada. Para ejecutar:" -ForegroundColor Cyan
    Write-Host "  docker-compose up ocr-service" -ForegroundColor White
    exit 0
}

# Run
Write-Host ""
Write-Host "Iniciando servicio OCR..." -ForegroundColor Yellow
Write-Host ""

try {
    if ($Logs) {
        # Modo foreground con logs
        docker-compose up ocr-service
    } else {
        # Modo background
        docker-compose up -d ocr-service
        
        Start-Sleep -Seconds 3
        
        Write-Host ""
        Write-Host "[OK] Servicio iniciado" -ForegroundColor Green
        Write-Host ""
        
        # Verificar estado
        Write-Host "Estado del contenedor:" -ForegroundColor Cyan
        docker ps --filter "name=sacra360_ocr_service" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        Write-Host ""
        Write-Host "Verificando GPU..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
        
        # Verificar GPU en el contenedor
        try {
            $gpuCheck = docker exec sacra360_ocr_service nvidia-smi 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] GPU accesible en el contenedor" -ForegroundColor Green
            }
        } catch {
            Write-Host "[WARN] No se pudo verificar GPU" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "================================================" -ForegroundColor Cyan
        Write-Host "COMANDOS ÚTILES" -ForegroundColor Cyan
        Write-Host "================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Ver logs:" -ForegroundColor Yellow
        Write-Host "  docker logs -f sacra360_ocr_service" -ForegroundColor White
        Write-Host ""
        Write-Host "Verificar GPU:" -ForegroundColor Yellow
        Write-Host "  docker exec sacra360_ocr_service nvidia-smi" -ForegroundColor White
        Write-Host ""
        Write-Host "Test de API:" -ForegroundColor Yellow
        Write-Host "  curl http://localhost:8003/ocr-gpu/gpu-status" -ForegroundColor White
        Write-Host ""
        Write-Host "Detener servicio:" -ForegroundColor Yellow
        Write-Host "  docker-compose down" -ForegroundColor White
        Write-Host ""
        
        # Intentar verificar endpoint
        Write-Host "Esperando que el servicio esté listo..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
        
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:8003/ocr-gpu/gpu-status" -TimeoutSec 5
            Write-Host ""
            Write-Host "[OK] Servicio respondiendo:" -ForegroundColor Green
            Write-Host "  GPU Enabled: $($response.gpu_enabled)" -ForegroundColor White
            Write-Host "  GPU Name: $($response.device_name)" -ForegroundColor White
        } catch {
            Write-Host ""
            Write-Host "[INFO] Servicio aún iniciando. Verifica con:" -ForegroundColor Yellow
            Write-Host "  curl http://localhost:8003/ocr-gpu/gpu-status" -ForegroundColor White
        }
    }
} catch {
    Write-Host "[FAIL] Error iniciando servicio" -ForegroundColor Red
    Write-Host "Ver logs con: docker logs sacra360_ocr_service" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
