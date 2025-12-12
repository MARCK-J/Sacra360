FROM ubuntu:22.04

# Evitar prompts interactivos durante la instalación
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instalar Python 3.11, pip y dependencias del sistema (incluye Poppler 22.02)
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-distutils \
    python3-pip \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/* \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Copiar y instalar dependencias de Python
COPY requirements.txt /app/

# Instalar PyTorch primero desde el índice correcto (versión específica que funciona)
RUN pip install --no-cache-dir torch==2.2.0 torchvision==0.17.0 --index-url https://download.pytorch.org/whl/cpu

# Instalar el resto de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app /app

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
