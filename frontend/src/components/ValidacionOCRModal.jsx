export default function ValidacionOCRModal({ isOpen, onClose, ocrData, onValidate }) {
  if (!isOpen) return null
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full">
        <h2 className="text-xl font-bold mb-4">ValidaciÃ³n OCR</h2>
        <p className="text-gray-600 mb-4">Funcionalidad en desarrollo...</p>
        <button 
          onClick={onClose}
          className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Cerrar
        </button>
      </div>
    </div>
  )
}
