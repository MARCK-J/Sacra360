#!/bin/bash

# Script de verificación de configuración del Documents Service
echo "🔍 Verificando configuración del Documents Service..."

# Verificar estructura de archivos
echo "📂 Verificando estructura de archivos..."
REQUIRED_FILES=(
    "Dockerfile"
    "requirements.txt"
    ".env.example"
    "app/main.py"
    "app/database.py"
    "app/models/__init__.py"
    "app/controllers/persona_controller.py"
    "app/controllers/libro_controller.py"
    "app/services/persona_service.py"
    "app/services/libro_service.py"
    "app/dto/persona_dto.py"
    "app/dto/libro_dto.py"
    "app/entities/persona.py"
    "app/entities/libro.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ FALTA: $file"
    fi
done

echo ""
echo "🐳 Configuración de Docker:"
echo "- Puerto del servicio: 8002"
echo "- Base de datos: PostgreSQL en puerto 5432"
echo "- Credenciales BD: postgres:lolsito101@postgres:5432/sacra360"
echo "- Redis: redis:6379"

echo ""
echo "🚀 Para probar el microservicio:"
echo "1. cd al directorio BACKEND/"
echo "2. docker-compose up -d postgres redis"
echo "3. docker-compose up --build documents-service"
echo "4. Visitar: http://localhost:8002/docs"

echo ""
echo "🔧 Endpoints disponibles:"
echo "- GET /health - Health check"
echo "- GET /docs - Documentación Swagger"
echo "- API Personas: /api/v1/personas/"
echo "- API Libros: /api/v1/libros/"

echo ""
echo "✅ Verificación completada!"