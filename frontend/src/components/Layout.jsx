import { Link, useLocation } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { to: '/digitalizacion', label: 'Digitalización', icon: 'cloud_upload' },
  { to: '/revision-ocr', label: 'Revisión OCR', icon: 'document_scanner' },
  { to: '/sacramento', label: 'Registro', icon: 'menu_book' },
  { to: '/sacramentos', label: 'Sacramentos', icon: 'auto_stories' },
  { to: '/personas', label: 'Personas', icon: 'group' },
  { to: '/libros', label: 'Libros', icon: 'import_contacts' },
  { to: '/certificados', label: 'Certificados', icon: 'workspace_premium' },
  { to: '#', label: 'Duplicados', icon: 'control_point_duplicate' },
  { to: '/usuarios', label: 'Usuarios', icon: 'manage_accounts' },
  { to: '/auditoria', label: 'Auditoría', icon: 'history' },
  { to: '/reportes', label: 'Reportes', icon: 'bar_chart' },
  { to: '/estadisticas', label: 'Estadísticas', icon: 'analytics' },
]

export default function Layout({ title, children }) {
  const location = useLocation()
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
            {navItems.map(item => {
              const active = item.to !== '#' && location.pathname.startsWith(item.to)
              const cls = active
                ? 'flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary font-semibold'
                : 'flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors'
              return item.to === '#'
                ? (
                    <span key={item.label} className={cls}>
                      <span className="material-symbols-outlined">{item.icon}</span>
                      <span>{item.label}</span>
                    </span>
                  )
                : (
                    <Link key={item.to} to={item.to} className={cls}>
                      <span className="material-symbols-outlined">{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  )
            })}
          </nav>
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
                <img alt="Avatar" className="w-10 h-10 rounded-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBMk_WnYIase354r69oXFK_iITqvn5ay8pAjZj3vmZ-1_vF4_alZOUC2Vic0_EIp_fJyv8OO9Dq6tYxhz6mbKO-chpL61q3_KVXoq7MbMttyd6d0j3H-eVLBGOr1zfmFBOkFB4x8e2Jl_K0srV7poc-C5Mi3PerstL85S7_IKUSZ3YPx6MINDsNonTnIEpu3YdSnN2EySd55GOspBjmnzBoNbtCevPovWpOZNw3pjrritTlrNaGOh07rbFbBiQmUy7KgZ0k6yANP-8" />
                <div>
                  <p className="font-semibold text-sm">Admin</p>
                  <p className="text-xs text-muted-light dark:text-muted-dark">Administrador</p>
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
