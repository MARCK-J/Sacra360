# OCR Service - Sacra360 OCR V2 CPU-only
# Dockerfile para microservicio de OCR con EasyOCR (CPU)

# Usar imagen base de Python
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

# Instalar dependencias del sistema para OCR y procesamiento de imágenes
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    libmupdf-dev \
    mupdf-tools \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip
RUN pip install --upgrade pip setuptools wheel

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar PyTorch CPU-only (compatible con EasyOCR)
RUN pip install --no-cache-dir torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cpu

# Instalar dependencias Python restantes
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios para el procesamiento
RUN mkdir -p temp temp_preprocessed logs uploads

# Exponer puerto
EXPOSE 8003
# Configurar variables de entorno por defecto
ENV DATABASE_URL=postgresql://postgres:password@postgres:5432/sacra360
ENV SERVICE_PORT=8003
ENV LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]