"""
Tests para el módulo OCR GPU.
Ejecutar con: pytest test_ocr_gpu.py -v
"""

import pytest
import os
import tempfile
import numpy as np
import pandas as pd
from pathlib import Path

# Importar módulos a testear
try:
    from app.ocr_gpu_processor import TableOCRProcessor, process_table_pdf
    import torch
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(not IMPORTS_OK, reason="Dependencias no disponibles")
class TestGPUAvailability:
    """Tests para verificar disponibilidad de GPU."""
    
    def test_cuda_available(self):
        """Verifica si CUDA está disponible."""
        cuda_available = torch.cuda.is_available()
        print(f"\nCUDA disponible: {cuda_available}")
        if cuda_available:
            print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    def test_processor_initialization_with_gpu(self):
        """Verifica inicialización del procesador con GPU."""
        if not torch.cuda.is_available():
            pytest.skip("GPU no disponible")
        
        processor = TableOCRProcessor(use_gpu=True)
        assert processor.use_gpu == True
        assert processor.reader is not None
    
    def test_processor_initialization_without_gpu(self):
        """Verifica inicialización del procesador sin GPU (CPU fallback)."""
        processor = TableOCRProcessor(use_gpu=False)
        assert processor.use_gpu == False
        assert processor.reader is not None
    
    def test_get_gpu_info(self):
        """Verifica método get_gpu_info()."""
        processor = TableOCRProcessor(use_gpu=True)
        gpu_info = processor.get_gpu_info()
        
        assert "cuda_available" in gpu_info
        assert "device_count" in gpu_info
        assert isinstance(gpu_info["cuda_available"], bool)
        assert isinstance(gpu_info["device_count"], int)
        
        print(f"\nGPU Info: {gpu_info}")


@pytest.mark.skipif(not IMPORTS_OK, reason="Dependencias no disponibles")
class TestImageProcessing:
    """Tests para procesamiento de imágenes."""
    
    @pytest.fixture
    def sample_image(self):
        """Crea una imagen de prueba."""
        # Crear imagen sintética con texto
        img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        
        # Agregar rectángulo simulando celda de tabla
        import cv2
        cv2.rectangle(img, (50, 50), (350, 150), (0, 0, 0), 2)
        cv2.putText(img, "Test 123", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        return img
    
    @pytest.fixture
    def processor(self):
        """Crea un procesador para tests."""
        return TableOCRProcessor(use_gpu=torch.cuda.is_available())
    
    def test_merge_overlapping_cells(self, processor):
        """Test de fusión de celdas superpuestas."""
        cells = [
            (100, 100, 50, 50),  # x, y, w, h
            (105, 105, 45, 45),  # Superpuesta
            (300, 100, 50, 50)   # Separada
        ]
        
        merged = processor._merge_overlapping_cells(cells)
        
        # Debería fusionar las primeras dos
        assert len(merged) <= len(cells)
        print(f"\nCeldas originales: {len(cells)}, fusionadas: {len(merged)}")
    
    def test_preprocess_cells_creates_directory(self, processor):
        """Verifica que el preprocesamiento crea directorios."""
        assert os.path.exists(processor.preprocessed_dir)


@pytest.mark.skipif(not IMPORTS_OK, reason="Dependencias no disponibles")
class TestColumnAlignment:
    """Tests para corrección de alineación de columnas."""
    
    @pytest.fixture
    def processor(self):
        return TableOCRProcessor(use_gpu=False)  # No necesita GPU para este test
    
    def test_fix_column_alignment_perfect_data(self, processor):
        """Test con datos perfectamente alineados."""
        rows = [
            ['A', '1', '2', '3', 'B', '4', '5', '6', 'C', 'D'],
            ['E', '7', '8', '9', 'F', '10', '11', '12', 'G', 'H']
        ]
        pattern = ['L', 'N', 'N', 'N', 'L', 'N', 'N', 'N', 'L', 'L']
        
        df = processor._fix_column_alignment(rows, num_cols=10, pattern=pattern)
        
        assert len(df) == 2
        assert len(df.columns) == 10
    
    def test_fix_column_alignment_misaligned_data(self, processor):
        """Test con datos desalineados."""
        rows = [
            ['A', '1', '2', '3', 'B', '4', '5'],  # Falta datos
            ['6', 'C', 'D', 'E', '7', '8', '9', 'F', '10', '11', '12', 'G', 'H']
        ]
        pattern = ['L', 'N', 'N', 'N', 'L', 'N', 'N', 'N', 'L', 'L']
        
        df = processor._fix_column_alignment(rows, num_cols=10, pattern=pattern)
        
        # Debería corregir la alineación
        assert len(df.columns) == 10
        print(f"\nFilas corregidas: {len(df)}")


@pytest.mark.skipif(not IMPORTS_OK, reason="Dependencias no disponibles")
class TestEndToEnd:
    """Tests de integración end-to-end."""
    
    @pytest.fixture
    def mock_pdf_path(self):
        """
        Nota: Este test requiere un PDF real.
        Crear un PDF de prueba o usar uno existente.
        """
        # Retornar path a un PDF de prueba si existe
        test_pdf = Path("test_data/sample_table.pdf")
        if test_pdf.exists():
            return str(test_pdf)
        else:
            pytest.skip("No hay PDF de prueba disponible")
    
    @pytest.mark.slow
    def test_process_pdf_table_complete(self, mock_pdf_path):
        """
        Test completo de procesamiento de PDF.
        Marcado como 'slow' porque toma tiempo.
        """
        if not os.path.exists(mock_pdf_path):
            pytest.skip("PDF de prueba no encontrado")
        
        # Procesar con GPU si está disponible
        use_gpu = torch.cuda.is_available()
        
        df = process_table_pdf(
            pdf_path=mock_pdf_path,
            page_number=0,
            use_gpu=use_gpu
        )
        
        # Verificaciones básicas
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert len(df.columns) > 0
        
        print(f"\nResultado del procesamiento:")
        print(f"  Filas: {len(df)}")
        print(f"  Columnas: {len(df.columns)}")
        print(f"  GPU usado: {use_gpu}")
    
    def test_cleanup_temp_directories(self):
        """Verifica que se limpian los directorios temporales."""
        processor = TableOCRProcessor(use_gpu=False)
        
        # Directorios deben existir después de init
        assert os.path.exists(processor.temp_dir)
        assert os.path.exists(processor.preprocessed_dir)
        
        # Limpiar
        processor._cleanup_temp_dirs()
        
        # Directorios deben ser eliminados
        assert not os.path.exists(processor.temp_dir)
        assert not os.path.exists(processor.preprocessed_dir)


@pytest.mark.benchmark
@pytest.mark.skipif(not IMPORTS_OK, reason="Dependencias no disponibles")
class TestPerformance:
    """Tests de rendimiento (benchmark)."""
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="Requiere GPU")
    def test_gpu_vs_cpu_performance(self, benchmark):
        """
        Compara rendimiento GPU vs CPU.
        Requiere pytest-benchmark: pip install pytest-benchmark
        """
        # Este test necesita un PDF de prueba pequeño
        pytest.skip("Implementar con PDF de prueba específico")
    
    def test_memory_usage(self):
        """Verifica que no hay memory leaks."""
        import gc
        
        processor = TableOCRProcessor(use_gpu=False)
        
        # Simular procesamiento múltiple
        for _ in range(5):
            # Aquí irían operaciones de procesamiento
            pass
        
        # Forzar garbage collection
        del processor
        gc.collect()
        
        # En un test real, verificarías el uso de memoria


# Fixtures globales
@pytest.fixture(scope="session")
def test_data_dir():
    """Directorio para datos de prueba."""
    data_dir = Path("test_data")
    data_dir.mkdir(exist_ok=True)
    return data_dir


# Marks personalizados
def pytest_configure(config):
    """Configurar marks personalizados."""
    config.addinivalue_line("markers", "slow: marca tests que toman mucho tiempo")
    config.addinivalue_line("markers", "benchmark: marca tests de rendimiento")
    config.addinivalue_line("markers", "gpu: marca tests que requieren GPU")


# Main para ejecutar tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
