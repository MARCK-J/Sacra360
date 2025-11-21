import { useState } from 'react';

export default function DigitalizacionDemo() {
  const [files, setFiles] = useState([]);
  const [sacramento, setSacramento] = useState(0);  // Cambio: '' -> 0
  const [libro, setLibro] = useState(0);  // Cambio: '' -> 0
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const sacramentos = [
    { value: 1, label: 'Bautismo', name: 'bautismo' },
    { value: 2, label: 'Confirmación', name: 'confirmacion' },
    { value: 4, label: 'Matrimonio', name: 'matrimonio' },
  ];

  const libros = [
    { value: 1, label: 'Bautismos 2024 Updated' },
    { value: 2, label: 'Bautismos 2024' },
    { value: 4, label: 'Matrimonios 2024' },
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (newFiles) => {
    const validFiles = Array.from(newFiles).filter(file => {
      const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
      const maxSize = 50 * 1024 * 1024; // 50MB
      return validTypes.includes(file.type) && file.size <= maxSize;
    });

    setFiles(prev => [...prev, ...validFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0 || sacramento === 0 || libro === 0) {
      alert('Por favor, selecciona archivos, sacramento y libro');
      return;
    }

    console.log('Debug - Iniciando upload:', {
      files: files.length,
      sacramento: parseInt(sacramento),
      libro: parseInt(libro),
      uploading
    });

    setUploading(true);
    const newUploadedFiles = [];

    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('archivo', file);  // Cambio: 'file' -> 'archivo'
        formData.append('tipo_sacramento', sacramento);  // Cambio: 'sacramento' -> 'tipo_sacramento'
        formData.append('libro_id', libro);  // Cambio: 'libro' -> 'libro_id'
        formData.append('institucion_id', '1');  // Agregar institucion_id
        formData.append('procesar_automaticamente', 'true');  // Agregar procesamiento automático

        const response = await fetch('http://localhost:8002/api/v1/digitalizacion/upload', {
          method: 'POST',
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          newUploadedFiles.push({
            ...result,
            fileName: file.name,
            status: 'uploaded',
            timestamp: new Date().toLocaleString()
          });
        } else {
          const errorText = await response.text();
          console.error('Error uploading file:', file.name, 'Status:', response.status, 'Error:', errorText);
          newUploadedFiles.push({
            fileName: file.name,
            status: 'error',
            timestamp: new Date().toLocaleString(),
            error: `Error ${response.status}: ${errorText}`
          });
        }
      }

      setUploadedFiles(prev => [...prev, ...newUploadedFiles]);
      setFiles([]);
      setSacramento(0);
      setLibro(0);
    } catch (error) {
      console.error('Error during upload:', error);
      alert('Error durante la subida de archivos');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Demo Digitalización de Documentos</h1>
        
        {/* Formulario de Subida */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Subir Documentos</h2>
          
          {/* Selectores */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sacramento
              </label>
              <select
                value={sacramento}
                onChange={(e) => setSacramento(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={0}>Seleccionar sacramento</option>
                {sacramentos.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Libro
              </label>
              <select
                value={libro}
                onChange={(e) => setLibro(parseInt(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={0}>Seleccionar libro</option>
                {libros.map((l) => (
                  <option key={l.value} value={l.value}>
                    {l.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Área de Drop */}
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center ${
              dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            } ${uploading ? 'opacity-50' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="text-gray-600">
              <p className="text-lg font-medium mb-2">
                Arrastra archivos aquí o
              </p>
              <input
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png"
                onChange={(e) => handleFiles(e.target.files)}
                className="hidden"
                id="file-upload"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload"
                className="inline-block px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 cursor-pointer"
              >
                Seleccionar archivos
              </label>
              <p className="text-sm text-gray-500 mt-2">
                Soporta PDF, JPG, PNG (máx. 50MB cada uno)
              </p>
            </div>
          </div>

          {/* Lista de archivos seleccionados */}
          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                Archivos seleccionados ({files.length})
              </h3>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-md">
                    <div className="flex items-center">
                      <div className="text-sm">
                        <span className="font-medium text-gray-900">{file.name}</span>
                        <span className="text-gray-500 ml-2">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-red-500 hover:text-red-700"
                      disabled={uploading}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Botón de subida */}
          <div className="mt-6">
            {/* Debug info */}
            <div className="mb-2 text-xs text-gray-500">
              Debug: files={files.length}, sacramento="{sacramento}", libro="{libro}", uploading={uploading.toString()}
            </div>
            <button
              onClick={uploadFiles}
              disabled={files.length === 0 || sacramento === 0 || libro === 0 || uploading}
              className={`w-full py-3 px-4 rounded-md text-white font-medium ${
                files.length === 0 || sacramento === 0 || libro === 0 || uploading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-500 hover:bg-green-600'
              }`}
            >
              {uploading ? 'Subiendo archivos...' : `Subir ${files.length} archivo(s)`}
            </button>
          </div>
        </div>

        {/* Lista de archivos subidos */}
        {uploadedFiles.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Documentos Procesados</h2>
            <div className="space-y-3">
              {uploadedFiles.map((file, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{file.fileName}</h3>
                      <p className="text-sm text-gray-600">{file.timestamp}</p>
                      {file.documento_id && (
                        <p className="text-xs text-gray-500">ID: {file.documento_id}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${
                        file.status === 'uploaded' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {file.status === 'uploaded' ? 'Subido' : 'Error'}
                      </span>
                      {file.error && (
                        <p className="text-xs text-red-600 mt-1">{file.error}</p>
                      )}
                    </div>
                  </div>
                  
                  {file.minio_url && (
                    <div className="mt-3 text-sm text-gray-600">
                      <strong>Almacenado en MinIO:</strong> {file.minio_url}
                    </div>
                  )}
                  
                  {file.mensaje && (
                    <div className="mt-2 text-sm text-blue-600">
                      {file.mensaje}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}