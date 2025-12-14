# Script para limpiar la base de datos de Sacra360
# Ejecutar desde: d:\MARCK-J\TRABAJOS\GITHUB\Sacra360\BACKEND\

Write-Host "🗑️  Limpiando base de datos Sacra360..." -ForegroundColor Yellow

# Confirmar acción
$confirmacion = Read-Host "¿Está seguro que desea ELIMINAR TODOS LOS DATOS? (escriba 'SI' para confirmar)"

if ($confirmacion -ne "SI") {
    Write-Host "❌ Operación cancelada" -ForegroundColor Red
    exit
}

Write-Host "🔄 Ejecutando TRUNCATE en tablas..." -ForegroundColor Cyan

docker exec sacra360-postgres psql -U postgres -d sacra360 -c "TRUNCATE TABLE sacramentos, personas, ocr_resultado, documento_digitalizado, validacion_tuplas RESTART IDENTITY CASCADE;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Base de datos limpiada exitosamente" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Verificando estado de las tablas:" -ForegroundColor Cyan
    docker exec sacra360-postgres psql -U postgres -d sacra360 -c "SELECT 'personas' as tabla, COUNT(*) as registros FROM personas UNION ALL SELECT 'sacramentos', COUNT(*) FROM sacramentos UNION ALL SELECT 'documentos', COUNT(*) FROM documento_digitalizado UNION ALL SELECT 'ocr_resultado', COUNT(*) FROM ocr_resultado;"
} else {
    Write-Host "❌ Error al limpiar la base de datos" -ForegroundColor Red
}
