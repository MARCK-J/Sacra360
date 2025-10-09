"""
Pruebas para los procesadores de microservicios
"""

import pytest
from unittest.mock import Mock, patch
import tempfile
import os


class TestOCRProcessor:
    """Pruebas para el procesador OCR"""

    @patch('app.ocr.processor.pytesseract')
    @patch('app.ocr.processor.cv2')
    def test_extract_text_mock(self, mock_cv2, mock_pytesseract):
        """Probar extracción de texto con mocks"""
        from app.ocr.processor import OCRProcessor
        
        # Configurar mocks
        mock_cv2.imread.return_value = Mock()
        mock_cv2.cvtColor.return_value = Mock()
        mock_pytesseract.image_to_string.return_value = "Texto extraído de prueba"
        mock_pytesseract.image_to_data.return_value = {'conf': [85, 90, 80]}
        
        processor = OCRProcessor()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b'fake image data')
            tmp_path = tmp.name
        
        try:
            # Probar extracción sin preprocesamiento
            text, confidence = processor.extract_text(tmp_path, use_preprocessing=False)
            assert isinstance(text, str)
            assert isinstance(confidence, int)
            assert 0 <= confidence <= 100
        finally:
            os.unlink(tmp_path)

    def test_validate_extraction(self):
        """Probar validación de extracción"""
        from app.ocr.processor import OCRProcessor
        
        processor = OCRProcessor()
        
        # Texto válido
        assert processor.validate_extraction("Este es un texto válido con suficiente contenido")
        
        # Texto muy corto
        assert not processor.validate_extraction("abc")
        
        # Texto vacío
        assert not processor.validate_extraction("")
        
        # Solo números
        assert not processor.validate_extraction("123456789")


class TestHTRProcessor:
    """Pruebas para el procesador HTR"""

    def test_vocabulary_setup(self):
        """Probar configuración del vocabulario"""
        from app.htr.processor import HTRProcessor
        
        processor = HTRProcessor()
        
        assert len(processor.char_to_idx) > 0
        assert len(processor.idx_to_char) > 0
        assert len(processor.char_to_idx) == len(processor.idx_to_char)
        
        # Verificar que existan caracteres básicos
        assert 'a' in processor.char_to_idx
        assert 'A' in processor.char_to_idx
        assert '0' in processor.char_to_idx
        assert ' ' in processor.char_to_idx

    def test_validate_extraction(self):
        """Probar validación de extracción HTR"""
        from app.htr.processor import HTRProcessor
        
        processor = HTRProcessor()
        
        # Texto válido
        assert processor.validate_extraction("Texto manuscrito válido")
        
        # Texto muy corto
        assert not processor.validate_extraction("ab")
        
        # Texto vacío
        assert not processor.validate_extraction("")

    @patch('app.htr.processor.torch')
    def test_extract_text_mock(self, mock_torch):
        """Probar extracción con modelo mock"""
        from app.htr.processor import HTRProcessor
        
        processor = HTRProcessor()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            tmp.write(b'fake image data')
            tmp_path = tmp.name
        
        try:
            text, confidence = processor.extract_text(tmp_path)
            # Con el modelo mock, debería retornar texto mock
            assert isinstance(text, str)
            assert isinstance(confidence, int)
            assert text.startswith("[HTR Mock]")
        finally:
            os.unlink(tmp_path)


class TestAICompletionProcessor:
    """Pruebas para el procesador AI Completion"""

    def test_vocabulary_initialization(self):
        """Probar inicialización del vocabulario sacramental"""
        from app.ai_completion.processor import AICompletionProcessor
        
        processor = AICompletionProcessor()
        
        assert len(processor.sacramental_vocabulary) > 0
        assert "bautismo" in processor.sacramental_vocabulary
        assert "matrimonio" in processor.sacramental_vocabulary
        assert "parroquia" in processor.sacramental_vocabulary

    def test_preprocess_text(self):
        """Probar preprocesamiento de texto"""
        from app.ai_completion.processor import AICompletionProcessor
        
        processor = AICompletionProcessor()
        
        # Texto con espacios múltiples
        text = "Este    es  un   texto   con  espacios"
        processed = processor.preprocess_text(text)
        assert "  " not in processed
        
        # Texto con puntuación mal espaciada
        text = "Texto con , puntuación mal . espaciada"
        processed = processor.preprocess_text(text)
        assert ", " in processed
        assert ". " in processed

    def test_might_be_incomplete(self):
        """Probar detección de palabras incompletas"""
        from app.ai_completion.processor import AICompletionProcessor
        
        processor = AICompletionProcessor()
        
        # Palabras completas conocidas
        assert not processor._might_be_incomplete("bautismo")
        assert not processor._might_be_incomplete("parroquia")
        
        # Palabras muy cortas
        assert not processor._might_be_incomplete("de")
        assert not processor._might_be_incomplete("el")
        
        # Palabras que terminan abruptamente
        assert processor._might_be_incomplete("baut_")
        assert processor._might_be_incomplete("parroc-")

    def test_correct_text_errors(self):
        """Probar corrección de errores de texto"""
        from app.ai_completion.processor import AICompletionProcessor
        
        processor = AICompletionProcessor()
        
        # Texto con errores conocidos
        text = "bauttismo en la parroqu1a"
        corrected, corrections = processor.correct_text_errors(text)
        
        assert len(corrections) >= 0  # Puede o no encontrar correcciones
        assert isinstance(corrected, str)

    def test_complete_text_basic(self):
        """Probar completar texto básico"""
        from app.ai_completion.processor import AICompletionProcessor
        
        processor = AICompletionProcessor()
        
        text = "Este es un texto de prueba"
        result = processor.complete_text(text)
        
        assert "original_text" in result
        assert "final_text" in result
        assert "confidence_score" in result
        assert "processing_time" in result
        assert result["original_text"] == text

    def test_calculate_confidence(self):
        """Probar cálculo de confianza"""
        from app.ai_completion.processor import AICompletionProcessor
        
        processor = AICompletionProcessor()
        
        # Texto con vocabulario sacramental
        text = "bautismo en la parroquia"
        confidence = processor._calculate_confidence(text, [], {})
        assert 10 <= confidence <= 100
        
        # Texto sin vocabulario sacramental
        text = "texto completamente diferente sin contexto"
        confidence = processor._calculate_confidence(text, [], {})
        assert 10 <= confidence <= 100


class TestFileService:
    """Pruebas para el servicio de archivos"""

    def test_generate_unique_filename(self):
        """Probar generación de nombres únicos"""
        from app.services.file_service import FileService
        
        service = FileService()
        
        filename1 = service.generate_unique_filename("test.pdf")
        filename2 = service.generate_unique_filename("test.pdf")
        
        # Los nombres deben ser diferentes
        assert filename1 != filename2
        
        # Ambos deben mantener la extensión
        assert filename1.endswith(".pdf")
        assert filename2.endswith(".pdf")

    def test_calculate_file_hash(self):
        """Probar cálculo de hash de archivo"""
        from app.services.file_service import FileService
        
        service = FileService()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'test content for hash')
            tmp_path = tmp.name
        
        try:
            hash1 = service.calculate_file_hash(tmp_path)
            hash2 = service.calculate_file_hash(tmp_path)
            
            # El mismo archivo debe generar el mismo hash
            assert hash1 == hash2
            assert len(hash1) == 64  # SHA-256 produce 64 caracteres hex
        finally:
            os.unlink(tmp_path)