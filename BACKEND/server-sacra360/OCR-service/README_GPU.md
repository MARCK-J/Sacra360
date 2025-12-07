# Configuración GPU para OCR-Service - Sacra360

Este documento explica cómo configurar y ejecutar el servicio OCR con aceleración GPU usando Docker y NVIDIA CUDA.

## 📋 Requisitos Previos

### Hardware
- **GPU NVIDIA** compatible con CUDA 11.8 o superior
- Arquitectura mínima recomendada: **Turing (RTX 20xx, GTX 16xx) o superior**
- GPU equivalente a T4 de Google Colab o mejor
- Mínimo 4GB de VRAM (recomendado 8GB+)

### Software

#### 1. Drivers NVIDIA
Instala los drivers más recientes de NVIDIA para tu GPU:

**Windows:**
```powershell
# Descargar desde: https://www.nvidia.com/Download/index.aspx
# O usando winget:
winget install --id=Nvidia.GeForceExperience -e
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nvidia-driver-535

# Verificar instalación
nvidia-smi
```

#### 2. NVIDIA Container Toolkit
Para que Docker pueda usar la GPU:

**Windows:**
- Docker Desktop debe estar configurado con soporte WSL2
- Instalar [NVIDIA Container Toolkit for WSL2](https://docs.nvidia.com/cuda/wsl-user-guide/index.html)

**Linux:**
```bash
# Añadir repositorio
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Instalar
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Reiniciar Docker
sudo systemctl restart docker
```

#### 3. Docker & Docker Compose
```bash
# Verificar versiones mínimas
docker --version          # >= 20.10
docker-compose --version  # >= 1.29
```

## 🚀 Instalación y Configuración

### Paso 1: Verificar GPU
```bash
# Verificar que la GPU sea detectada
nvidia-smi

# Deberías ver algo como:
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 535.x        Driver Version: 535.x        CUDA Version: 12.x    |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name                     | ...                                         |
```

### Paso 2: Probar Docker con GPU
```bash
# Test rápido de CUDA en Docker
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Si funciona, verás la salida de nvidia-smi dentro del contenedor
```

### Paso 3: Construir la Imagen OCR con GPU

#### Opción A: Construir solo el servicio OCR
```powershell
# Desde el directorio raíz del proyecto
cd BACKEND

# Construir imagen
docker-compose build ocr-service

# Esto tomará varios minutos la primera vez (descarga CUDA, PyTorch, etc.)
```

#### Opción B: Construir todos los servicios
```powershell
docker-compose build
```

### Paso 4: Iniciar el Servicio

#### Iniciar solo OCR service con GPU:
```powershell
docker-compose up ocr-service
```

#### Iniciar todo el stack:
```powershell
docker-compose up -d
```

### Paso 5: Verificar que la GPU está siendo usada

#### Ver logs del contenedor:
```powershell
docker logs sacra360_ocr_service
```

#### Verificar GPU dentro del contenedor:
```powershell
docker exec -it sacra360_ocr_service nvidia-smi
```

#### Probar endpoint de estado GPU:
```powershell
curl http://localhost:8003/ocr-gpu/gpu-status
```

Deberías ver:
```json
{
  "status": "success",
  "gpu_enabled": true,
  "cuda_version": "11.8",
  "device_count": 1,
  "device_name": "NVIDIA GeForce RTX 3060",
  "message": "GPU disponible y lista para usar"
}
```

## 📊 Uso del Servicio

### Endpoint: Verificar GPU
```bash
GET http://localhost:8003/ocr-gpu/gpu-status
```

### Endpoint: Procesar Tabla PDF
```bash
POST http://localhost:8003/ocr-gpu/process-table
Content-Type: multipart/form-data

{
  "file": [archivo PDF],
  "page_number": 0,
  "num_cols": 10,
  "use_gpu": true,
  "output_format": "json"
}
```

### Ejemplo con cURL:
```powershell
curl -X POST http://localhost:8003/ocr-gpu/process-table `
  -F "file=@tabla.pdf" `
  -F "page_number=0" `
  -F "num_cols=10" `
  -F "use_gpu=true" `
  -F "output_format=json"
```

### Ejemplo Python:
```python
import requests

url = "http://localhost:8003/ocr-gpu/process-table"
files = {"file": open("tabla.pdf", "rb")}
data = {
    "page_number": 0,
    "num_cols": 10,
    "use_gpu": True,
    "output_format": "json"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## ⚡ Optimización de Rendimiento

### Comparación CPU vs GPU

| Métrica | CPU (sin GPU) | GPU (T4/RTX) |
|---------|---------------|--------------|
| **Tiempo por página** | 45-120 segundos | 3-8 segundos |
| **Procesamiento batch (10 docs)** | ~15 minutos | ~1-2 minutos |
| **Uso de memoria** | 2-4 GB RAM | 2GB RAM + 2-4GB VRAM |

### Variables de Entorno para Ajustar

Edita `docker-compose.yml` si necesitas ajustar:

```yaml
environment:
  # Especificar GPU a usar (0=primera GPU, 1=segunda, etc.)
  - CUDA_VISIBLE_DEVICES=0
  
  # Usar múltiples GPUs
  # - CUDA_VISIBLE_DEVICES=0,1
```

Para usar TODAS las GPUs disponibles:
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all  # Cambiar de 1 a "all"
          capabilities: [gpu]
```

## 🐛 Resolución de Problemas

### Error: "could not select device driver with capabilities: [[gpu]]"

**Solución:**
1. Verifica que NVIDIA Container Toolkit esté instalado
2. Reinicia el servicio Docker
3. Verifica con: `docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi`

### Error: "CUDA out of memory"

**Soluciones:**
1. Procesa documentos de uno en uno en lugar de lotes grandes
2. Reduce el DPI de conversión PDF (en `TableOCRProcessor`, cambia `dpi=150` a `dpi=100`)
3. Usa una GPU con más VRAM

### El servicio usa CPU en lugar de GPU

**Diagnóstico:**
```python
import torch
print(torch.cuda.is_available())  # Debe ser True
print(torch.cuda.get_device_name(0))  # Debe mostrar tu GPU
```

**Solución:**
1. Verifica que la imagen Docker tenga CUDA instalado
2. Verifica variables de entorno `CUDA_VISIBLE_DEVICES`
3. Reconstruye la imagen: `docker-compose build --no-cache ocr-service`

### GPU no se detecta en Windows con WSL2

**Solución:**
1. Actualiza WSL: `wsl --update`
2. Verifica GPU en WSL: `wsl nvidia-smi`
3. Configura Docker Desktop para usar backend WSL2

## 📈 Monitoreo de GPU

### Durante ejecución, monitorea en tiempo real:

```powershell
# Terminal 1: Ver uso de GPU
watch -n 1 nvidia-smi

# Terminal 2: Ver logs del servicio
docker logs -f sacra360_ocr_service
```

### Verificar temperatura y uso:
```bash
nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used --format=csv --loop=1
```

## 🔧 Configuración Avanzada

### Modo Desarrollo (sin GPU)
Si necesitas desarrollar sin GPU temporalmente:

```yaml
# En docker-compose.yml, comenta la sección deploy:
ocr-service:
  # deploy:
  #   resources:
  #     reservations:
  #       devices:
  #         - driver: nvidia
  #           count: 1
  #           capabilities: [gpu]
```

Y en el código, configura:
```python
processor = TableOCRProcessor(use_gpu=False)
```

### Modo Producción con Alta Disponibilidad

Para mayor rendimiento en producción:

```yaml
ocr-service:
  deploy:
    replicas: 3  # Múltiples instancias
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
  environment:
    - WORKERS=4  # Workers por instancia
```

## 📚 Referencias

- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-docker)
- [Docker GPU Support](https://docs.docker.com/config/containers/resource_constraints/#gpu)
- [PyTorch CUDA](https://pytorch.org/get-started/locally/)
- [EasyOCR Documentation](https://github.com/JaidedAI/EasyOCR)

## 💡 Consejos

1. **Primera ejecución lenta**: La primera vez, EasyOCR descarga modelos (~100MB). Ejecuciones posteriores son más rápidas.

2. **Persistencia de modelos**: Para evitar descargas repetidas, monta un volumen:
   ```yaml
   volumes:
     - ./models/easyocr:/root/.EasyOCR/model
   ```

3. **Calentamiento de GPU**: La primera inferencia puede ser más lenta. Considera hacer una llamada de "warmup" al iniciar.

4. **Batch processing**: Para múltiples documentos, usa el endpoint `/batch-process` para mejor eficiencia.

---

**Nota:** Este servicio está optimizado para GPUs equivalentes a Google Colab T4. Si tienes una GPU más potente (RTX 3090, A100, etc.), el rendimiento será aún mejor.
