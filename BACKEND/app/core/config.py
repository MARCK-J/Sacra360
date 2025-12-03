from types import SimpleNamespace

# Minimal settings object used by tests and by a shim FastAPI app
settings = SimpleNamespace(
    service_name="Sacra360 Test Service",
    service_version="0.0.0",
    service_port=8000,
    cors_origins=["*"],
    ocr_language="spa",
    max_file_size=10 * 1024 * 1024,
    allowed_file_types=["pdf", "jpg", "png"],
    log_level="INFO"
)
