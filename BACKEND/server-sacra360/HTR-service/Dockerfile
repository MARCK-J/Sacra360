FROM pytorch/pytorch:latest

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instalar dependencias del sistema necesarias (Poppler, librerías de imágenes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias de Python
COPY requirements.txt /app/

# La imagen base incluye PyTorch con soporte CUDA; no instalar la variante CPU.
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app /app

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
