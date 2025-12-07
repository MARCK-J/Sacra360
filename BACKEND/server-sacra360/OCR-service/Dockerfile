# OCR Service - Sacra360 con soporte GPU AMD/Vulkan
# Dockerfile para microservicio de OCR con DirectML/OpenCL

# Usar imagen base de Python con soporte para OpenCL y Vulkan
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    FORCE_CUDA=0 \
    USE_ROCM=1

# Instalar dependencias del sistema con soporte OpenCL y Vulkan para AMD
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    ffmpeg \
    libavcodec-extra \
    wget \
    curl \
    ocl-icd-libopencl1 \
    opencl-headers \
    clinfo \
    mesa-opencl-icd \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip
RUN pip install --upgrade pip setuptools wheel

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar PyTorch CPU (compatible con DirectML en Windows host)
# En contenedor Linux usaremos CPU o detectará GPU automáticamente
RUN pip install --no-cache-dir torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/cpu

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
ENV TESSERACT_PATH=/usr/bin/tesseract
ENV SERVICE_PORT=8003
ENV LOG_LEVEL=INFO
ENV FORCE_CPU=0
ENV USE_DIRECTML=1
ENV TORCH_CUDA_ARCH_LIST="6.0 6.1 7.0 7.5 8.0 8.6"

# Comando para ejecutar la aplicación
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]