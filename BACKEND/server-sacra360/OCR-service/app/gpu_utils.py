"""
Utilidades para detección de GPU AMD/NVIDIA
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def detect_gpu_type() -> Dict[str, any]:
    """
    Detecta el tipo de GPU disponible (AMD, NVIDIA o ninguna).
    
    Returns:
        Diccionario con información de GPU detectada
    """
    import torch
    
    gpu_info = {
        "has_gpu": False,
        "gpu_type": "CPU",
        "device_name": None,
        "backend": None,
        "can_use_gpu": False,
        "vram_gb": 0
    }
    
    # Verificar CUDA (NVIDIA)
    if torch.cuda.is_available():
        gpu_info["has_gpu"] = True
        gpu_info["gpu_type"] = "NVIDIA"
        gpu_info["device_name"] = torch.cuda.get_device_name(0)
        gpu_info["backend"] = "CUDA"
        gpu_info["can_use_gpu"] = True
        try:
            gpu_info["vram_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        except:
            pass
        logger.info(f"GPU NVIDIA detectada: {gpu_info['device_name']}")
        return gpu_info
    
    # Verificar ROCm (AMD)
    try:
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            gpu_info["has_gpu"] = True
            gpu_info["gpu_type"] = "AMD"
            gpu_info["backend"] = "ROCm"
            gpu_info["can_use_gpu"] = True
            logger.info("GPU AMD detectada con ROCm")
            return gpu_info
    except Exception as e:
        logger.debug(f"ROCm no disponible: {e}")
    
    # Verificar OpenCL (alternativa para AMD)
    try:
        import pyopencl as cl
        platforms = cl.get_platforms()
        if platforms:
            for platform in platforms:
                devices = platform.get_devices()
                for device in devices:
                    if device.type == cl.device_type.GPU:
                        gpu_info["has_gpu"] = True
                        gpu_info["gpu_type"] = "AMD/Other"
                        gpu_info["device_name"] = device.name
                        gpu_info["backend"] = "OpenCL"
                        # EasyOCR con PyTorch puede usar GPU si está disponible
                        gpu_info["can_use_gpu"] = True  # Intentar usar GPU
                        try:
                            gpu_info["vram_gb"] = device.global_mem_size / (1024**3)
                        except:
                            pass
                        logger.info(f"GPU detectada via OpenCL: {device.name} ({gpu_info['vram_gb']:.1f}GB)")
                        return gpu_info
    except ImportError:
        logger.debug("PyOpenCL no disponible")
    except Exception as e:
        logger.debug(f"Error detectando OpenCL: {e}")
    
    # No se detectó GPU compatible
    logger.info("No se detectó GPU compatible. Usando CPU.")
    gpu_info["backend"] = "CPU"
    return gpu_info


def get_optimal_device():
    """
    Obtiene el dispositivo óptimo para PyTorch.
    
    Returns:
        torch.device: Dispositivo a usar
    """
    import torch
    
    if torch.cuda.is_available():
        return torch.device("cuda")
    
    # Intentar detectar AMD/ROCm
    try:
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            return torch.device("cuda")  # ROCm usa sintaxis CUDA en PyTorch
    except:
        pass
    
    return torch.device("cpu")


def print_gpu_info():
    """Imprime información detallada de GPU disponible."""
    info = detect_gpu_type()
    
    print("\n" + "="*60)
    print("INFORMACION DE GPU")
    print("="*60)
    print(f"GPU Detectada: {info['has_gpu']}")
    print(f"Tipo: {info['gpu_type']}")
    print(f"Nombre: {info['device_name']}")
    print(f"Backend: {info['backend']}")
    print(f"Puede usar GPU: {info['can_use_gpu']}")
    if info['vram_gb'] > 0:
        print(f"VRAM: {info['vram_gb']:.1f} GB")
    print("="*60 + "\n")
    
    return info
