# 🚀 OCR con GPU - Sacra360

Ver documentación completa en:
- **[README_GPU.md](README_GPU.md)** - Guía completa de configuración
- **[QUICKSTART_GPU.md](QUICKSTART_GPU.md)** - Inicio rápido
- **[../CAMBIOS_GPU.md](../CAMBIOS_GPU.md)** - Resumen de cambios

## ⚡ Inicio Rápido

```powershell
# 1. Verificar requisitos
cd ../../
.\check_requirements.ps1

# 2. Construir y ejecutar
.\build_and_run.ps1

# 3. Verificar
curl http://localhost:8003/ocr-gpu/gpu-status
```

## 📊 Rendimiento

| | CPU | GPU T4 | Mejora |
|---|-----|--------|--------|
| **Por página** | 45-120s | 5-8s | **15-20x** |
| **10 docs** | ~15 min | ~1-2 min | **10x** |

## 📚 Documentación Completa

- [README_GPU.md](README_GPU.md) - Instalación, configuración, troubleshooting
- [QUICKSTART_GPU.md](QUICKSTART_GPU.md) - Guía rápida de 5 minutos
