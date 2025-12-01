import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { canAccessModule } from '../config/permissions'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: 'dashboard', module: null }, // Siempre visible
  { to: '/digitalizacion', label: 'Digitalización', icon: 'cloud_upload', module: 'digitalizacion' },
  { to: '/revision-ocr', label: 'Revisión OCR', icon: 'document_scanner', module: 'revisionOCR' },
  { to: '/registros', label: 'Registros', icon: 'menu_book', module: 'registros' },
  { to: '/personas', label: 'Personas', icon: 'group', module: 'personas' },
  { to: '/libros', label: 'Libros', icon: 'import_contacts', module: 'libros' },
  { to: '/certificados', label: 'Certificados', icon: 'workspace_premium', module: 'certificados' },
  { to: '/usuarios', label: 'Usuarios', icon: 'manage_accounts', module: 'usuarios' },
  { to: '/auditoria', label: 'Auditoría', icon: 'history', module: 'auditoria' },
  { to: '/reportes', label: 'Reportes', icon: 'bar_chart', module: 'reportes' },
]

export default function Layout({ title, children }) {
  const location = useLocation()
  const { user, getUserRole, logout } = useAuth()
  const userRole = getUserRole()

  // Filtrar items de navegación según permisos
  const visibleNavItems = navItems.filter(item => {
    // Dashboard siempre visible
    if (!item.module) return true
    // Verificar permisos del módulo
    return canAccessModule(userRole, item.module)
  })
  return (
    <div className="font-display bg-background-light dark:bg-background-dark text-foreground-light dark:text-foreground-dark min-h-screen">
      <div className="flex min-h-screen">
        <aside className="w-64 flex-shrink-0 bg-card-light dark:bg-card-dark border-r border-border-light dark:border-border-dark flex-col hidden lg:flex">
          <div className="h-16 flex items-center justify-center border-b border-border-light dark:border-border-dark gap-3 px-4">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <span className="material-symbols-outlined text-white">health_cross</span>
            </div>
            <h1 className="text-lg font-bold">Sacramentos</h1>
          </div>
          <nav className="flex-1 px-3 py-4 space-y-1">
            {visibleNavItems.map(item => {
              const active = item.to !== '#' && location.pathname.startsWith(item.to)
              const cls = active
                ? 'flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary font-semibold'
                : 'flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors'
              return (
                <Link key={item.to} to={item.to} className={cls}>
                  <span className="material-symbols-outlined">{item.icon}</span>
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>
          
          {/* Usuario logueado */}
          <div className="p-4 border-t border-border-light dark:border-border-dark">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white font-bold">
                {user?.nombre?.charAt(0) || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm truncate">
                  {user?.nombre} {user?.apellido_paterno}
                </p>
                <p className="text-xs text-muted-light dark:text-muted-dark truncate">
                  {user?.nombre_rol || 'Usuario'}
                </p>
              </div>
            </div>
            <button
              onClick={logout}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition-colors"
            >
              <span className="material-symbols-outlined text-sm">logout</span>
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </aside>
        <main className="flex-1">
          <header className="h-16 bg-card-light dark:bg-card-dark border-b border-border-light dark:border-border-dark flex items-center justify-between px-6">
            <h2 className="text-2xl font-bold tracking-tight">{title}</h2>
            <div className="flex items-center gap-4">
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-muted-light dark:text-muted-dark">search</span>
                <input type="text" placeholder="Buscar..." className="bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark rounded-full w-64 pl-10 pr-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary" />
              </div>
              <button className="relative text-muted-light dark:text-muted-dark hover:text-foreground-light dark:hover:text-foreground-dark">
                <span className="material-symbols-outlined">notifications</span>
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-primary"></span>
                </span>
              </button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white font-bold">
                  {user?.nombre?.charAt(0) || 'U'}
                </div>
                <div>
                  <p className="font-semibold text-sm">{user?.nombre || 'Usuario'}</p>
                  <p className="text-xs text-muted-light dark:text-muted-dark">{user?.nombre_rol || 'Rol'}</p>
                </div>
              </div>
            </div>
          </header>
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}