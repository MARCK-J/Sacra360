# Script de limpieza completa del sistema Sacra360 (SOLO PARA TESTING)
# Ejecutar desde el directorio BACKEND

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  LIMPIEZA COMPLETA DEL SISTEMA" -ForegroundColor Cyan
Write-Host "  (Solo para ambiente de pruebas)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Confirmar acción
$confirmacion = Read-Host "¿Está seguro de eliminar TODOS los datos? (escriba 'SI' para continuar)"
if ($confirmacion -ne "SI") {
    Write-Host "Operación cancelada." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "1. Limpiando tablas de PostgreSQL..." -ForegroundColor Green

# Ejecutar TRUNCATE en las tablas
Get-Content "sql\Truncate_Tablas_Testing.sql" | docker exec -i sacra360-postgres psql -U postgres -d sacra360

Write-Host ""
Write-Host "2. Verificando limpieza de base de datos..." -ForegroundColor Green
docker exec sacra360-postgres psql -U postgres -d sacra360 -c "SELECT 'personas' as tabla, COUNT(*) as registros FROM personas UNION ALL SELECT 'sacramentos', COUNT(*) FROM sacramentos UNION ALL SELECT 'documento_digitalizado', COUNT(*) FROM documento_digitalizado UNION ALL SELECT 'ocr_resultado', COUNT(*) FROM ocr_resultado UNION ALL SELECT 'validacion_tuplas', COUNT(*) FROM validacion_tuplas;"

Write-Host ""
Write-Host "3. Instrucciones para limpiar MinIO (opcional):" -ForegroundColor Yellow
Write-Host "   - Acceder a MinIO Console: http://localhost:9001" -ForegroundColor White
Write-Host "   - Usuario: minioadmin / Contraseña: minioadmin" -ForegroundColor White
Write-Host "   - Ir al bucket 'sacra360-documents'" -ForegroundColor White
Write-Host "   - Seleccionar todos los archivos y eliminar" -ForegroundColor White
Write-Host ""

Write-Host "✓ Limpieza de base de datos completada!" -ForegroundColor Green
Write-Host "  El sistema está listo para comenzar desde cero." -ForegroundColor Green
Write-Host ""
