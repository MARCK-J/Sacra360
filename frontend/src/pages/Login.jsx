import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()
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
              <h1 className="text-xl font-bold">Sacramentos Digitales</h1>
            </div>
            <div className="flex items-center gap-4">
              <a href="#" className="text-sm font-medium text-muted-light dark:text-muted-dark hover:text-primary dark:hover:text-primary transition-colors">Crear cuenta</a>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8">
          <div className="text-center">
            <h2 className="text-3xl font-extrabold tracking-tight">Iniciar Sesión</h2>
            <p className="mt-2 text-sm text-muted-light dark:text-muted-dark">Accede a tu cuenta para continuar</p>
          </div>
          <div className="bg-card-light dark:bg-card-dark p-8 shadow-xl rounded-lg border border-border-light dark:border-border-dark">
            <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); navigate('/Dashboard') }}>
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-muted-light dark:text-muted-dark">Usuario</label>
                <div className="mt-1">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="username"
                    required
                    placeholder="Nombre de usuario"
                    className="form-input block w-full rounded border-border-light dark:border-border-dark bg-background-light dark:bg-gray-800 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm h-12 px-4"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-muted-light dark:text-muted-dark">Contraseña</label>
                <div className="mt-1">
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    placeholder="Contraseña"
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
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                  onClick={() => navigate('/dashboard')}
                >
                  Iniciar Sesión
                </button>  
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
