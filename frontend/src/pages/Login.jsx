import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    contrasenia: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(formData.email, formData.contrasenia);
      
      if (result.success) {
        // Redirigir al dashboard
        navigate('/dashboard');
      } else {
        setError(result.error);
      }
      
    } catch (err) {
      console.error('Error en login:', err);
      setError('Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-background-light dark:bg-background-dark font-display text-foreground-light dark:text-foreground-dark min-h-screen flex flex-col">
      <header className="border-b border-border-light dark:border-border-dark shadow-sm">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 text-primary">
                <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                  <path d="M24 4C12.95 4 4 12.95 4 24C4 35.05 12.95 44 24 44C35.05 44 44 35.05 44 24C44 12.95 35.05 4 24 4ZM24 41C14.61 41 7 33.39 7 24C7 14.61 14.61 7 24 7C33.39 7 41 14.61 41 24C41 33.39 33.39 41 24 41Z" fill="currentColor"></path>
                  <path d="M22.5 15H25.5V25.5H36V28.5H25.5V36H22.5V28.5H12V25.5H22.5V15Z" fill="currentColor"></path>
                </svg>
              </div>
              <h1 className="text-xl font-bold">Sacra360</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold tracking-tight">Iniciar Sesión</h2>
            <p className="mt-2 text-sm text-muted-light dark:text-muted-dark">Sistema de Gestión de Archivos Sacramentales</p>
          </div>
          
          <div className="bg-card-light dark:bg-card-dark p-8 shadow-xl rounded-lg border border-border-light dark:border-border-dark">
            {error && (
              <div className="mb-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-3 rounded">
                <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
              </div>
            )}

            <form className="space-y-6" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-muted-light dark:text-muted-dark">
                  Correo Electrónico
                </label>
                <div className="mt-1">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="admin@sacra360.com"
                    disabled={loading}
                    className="form-input block w-full rounded border-border-light dark:border-border-dark bg-background-light dark:bg-gray-800 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm h-12 px-4"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="contrasenia" className="block text-sm font-medium text-muted-light dark:text-muted-dark">
                  Contraseña
                </label>
                <div className="mt-1">
                  <input
                    id="contrasenia"
                    name="contrasenia"
                    type="password"
                    required
                    value={formData.contrasenia}
                    onChange={handleChange}
                    placeholder="••••••••"
                    disabled={loading}
                    className="form-input block w-full rounded border-border-light dark:border-border-dark bg-background-light dark:bg-gray-800 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm h-12 px-4"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end">
                <div className="text-sm">
                  <a href="#" className="font-medium text-primary hover:text-primary/80">¿Olvidaste tu contraseña?</a>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Iniciando sesión...
                    </>
                  ) : (
                    'Iniciar Sesión'
                  )}
                </button>  
              </div>
            </form>

            <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                Credenciales de prueba: admin@sacra360.com
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
