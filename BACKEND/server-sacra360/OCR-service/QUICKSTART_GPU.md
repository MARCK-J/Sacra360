# 🚀 Guía Rápida - OCR con GPU

## Inicio Rápido (5 minutos)

### 1. Prerrequisitos Verificados
```powershell
# Verificar GPU
nvidia-smi

# Verificar Docker
docker --version
docker run --rm --gpus all nvidia/cuda:11.8.0-base nvidia-smi
```

### 2. Construir y Ejecutar
```powershell
# Navegar al directorio
cd d:\MARCK-J\TRABAJOS\GITHUB\Sacra360\BACKEND

# Construir servicio OCR
docker-compose build ocr-service

# Iniciar servicio
docker-compose up ocr-service
```

### 3. Verificar Funcionamiento
```powershell
# En otra terminal, verificar GPU
curl http://localhost:8003/ocr-gpu/gpu-status
```

### 4. Probar con Documento
```powershell
# Usando PowerShell
$file = "ruta\a\tu\documento.pdf"
curl -X POST http://localhost:8003/ocr-gpu/process-table `
  -F "file=@$file" `
  -F "use_gpu=true"
```

---

## Comandos Útiles

### Gestión de Contenedores
```powershell
# Ver logs
docker logs -f sacra360_ocr_service

# Entrar al contenedor
docker exec -it sacra360_ocr_service bash

# Reiniciar servicio
docker-compose restart ocr-service

# Reconstruir desde cero
docker-compose build --no-cache ocr-service

# Detener todo
docker-compose down
```

### Monitoreo GPU
```powershell
# Ver uso de GPU en tiempo real
watch -n 1 nvidia-smi

# Dentro del contenedor
docker exec sacra360_ocr_service nvidia-smi
```

### Pruebas
```powershell
# Ejecutar test dentro del contenedor
docker exec -it sacra360_ocr_service python test_gpu_ocr.py

# Con documento específico
docker exec -it sacra360_ocr_service python test_gpu_ocr.py /path/to/doc.pdf
```

---

## Solución Rápida de Problemas

| Problema | Solución Rápida |
|----------|----------------|
| GPU no detectada | `nvidia-smi` → Instalar drivers |
| Docker sin GPU | Instalar NVIDIA Container Toolkit |
| Error CUDA out of memory | Reducir DPI o procesar 1 documento a la vez |
| Servicio muy lento | Verificar que `use_gpu=true` y GPU esté activa |
| Primera ejecución lenta | Normal, descarga modelos (~2min primera vez) |

---

## Endpoints Principales

### Verificar GPU
```
GET http://localhost:8003/ocr-gpu/gpu-status
```

### Procesar Tabla
```
POST http://localhost:8003/ocr-gpu/process-table
Content-Type: multipart/form-data

{
  "file": [PDF],
  "use_gpu": true,
  "num_cols": 10
}
```

---

## Rendimiento Esperado

| GPU | Tiempo/Página | Memoria |
|-----|---------------|---------|
| **CPU** | 45-120s | 2-4GB RAM |
| **T4** | 5-8s | 4GB VRAM |
| **RTX 3060** | 3-5s | 4GB VRAM |
| **RTX 4090** | 2-3s | 4GB VRAM |

---

## Checklist de Configuración

- [ ] Drivers NVIDIA instalados (`nvidia-smi` funciona)
- [ ] Docker con soporte GPU (`docker run --gpus all nvidia/cuda`)
- [ ] Imagen construida (`docker-compose build ocr-service`)
- [ ] Servicio ejecutándose (`docker ps | grep ocr-service`)
- [ ] GPU detectada en servicio (`curl .../gpu-status`)
- [ ] Test de procesamiento exitoso

---

## Configuración Avanzada

### Usar GPU específica
```yaml
# docker-compose.yml
environment:
  - CUDA_VISIBLE_DEVICES=0  # Primera GPU
  # - CUDA_VISIBLE_DEVICES=1  # Segunda GPU
```

### Múltiples GPUs
```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all  # Usar todas
          capabilities: [gpu]
```

### Ajustar workers
```yaml
environment:
  - WORKERS=4  # Número de workers concurrentes
```

---

## Próximos Pasos

1. ✅ **Configuración completada** → Ver [README_GPU.md](README_GPU.md)
2. 📊 **Integrar con tu API** → Ver [app/ocr_endpoints_gpu.py](app/ocr_endpoints_gpu.py)
3. 🔧 **Personalizar procesamiento** → Editar [app/ocr_gpu_processor.py](app/ocr_gpu_processor.py)
4. 🚀 **Producción** → Configurar load balancing y escalado

---

**Documentación completa:** [README_GPU.md](README_GPU.md)
