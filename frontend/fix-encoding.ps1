# Script para corregir la codificación de caracteres en archivos JSX

Get-ChildItem -Path "src/pages" -Filter "*.jsx" | ForEach-Object {
    Write-Host "Processing $($_.Name)..."
    
    $bytes = [System.IO.File]::ReadAllBytes($_.FullName)
    $content = [System.Text.Encoding]::UTF8.GetString($bytes)
    
    # Reemplazos específicos de strings conocidas
    $content = $content -replace 'Revisi├│n', 'Revisión'
    $content = $content -replace 'Auditor├¡a', 'Auditoría'
    $content = $content -replace 'Garc├¡a', 'García'
    $content = $content -replace 'P├®rez', 'Pérez'
    $content = $content -replace 'Rodr├¡guez', 'Rodríguez'
    $content = $content -replace 'L├¡nea', 'Línea'
    $content = $content -replace 'L├│pez', 'López'
    $content = $content -replace 'Mart├¡nez', 'Martínez'
    $content = $content -replace 'Fern├índez', 'Fernández'
    $content = $content -replace 'realiz├│', 'realizó'
    $content = $content -replace 'detect├│', 'detectó'
    $content = $content -replace 'consult├│', 'consultó'
    $content = $content -replace 'Acci├│n', 'Acción'
    $content = $content -replace 'Creaci├│n', 'Creación'
    $content = $content -replace 'Modificaci├│n', 'Modificación'
    $content = $content -replace 'Eliminaci├│n', 'Eliminación'
    $content = $content -replace 'Confirmaci├│n', 'Confirmación'
    $content = $content -replace 'Defunci├│n', 'Defunción'
    $content = $content -replace 'Digitalizaci├│n', 'Digitalización'
    $content = $content -replace 'Generaci├│n', 'Generación'
    $content = $content -replace 'Ingl├®s', 'Inglés'
    $content = $content -replace 'M├ís', 'Más'
    $content = $content -replace 'Gesti├│n', 'Gestión'
    $content = $content -replace 'M├│dulo', 'Módulo'
    $content = $content -replace 'Validaci├│n', 'Validación'
    $content = $content -replace 'validaci├│n', 'validación'
    $content = $content -replace 'Informaci├│n', 'Información'
    $content = $content -replace 'aqu├¡', 'aquí'
    $content = $content -replace 'Ubicaci├│n', 'Ubicación'
    $content = $content -replace 'ubicaci├│n', 'ubicación'
    $content = $content -replace 'F├¡sica', 'Física'
    $content = $content -replace 'Cuadr├¡cula', 'Cuadrícula'
    $content = $content -replace 'Estanter├¡as', 'Estanterías'
    $content = $content -replace 'Redirecci├│n', 'Redirección'
    $content = $content -replace 'autom├ítica', 'automática'
    $content = $content -replace 'ÔåÉ', '←'
    $content = $content -replace 'Sof├¡a', 'Sofía'
    
    # Guardar con UTF-8 sin BOM
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($_.FullName, $content, $utf8NoBom)
}

Write-Host "Encoding fixed in all JSX files!"
