export default function Dashboard() {
  return (
    <div className="font-display bg-background-light dark:bg-background-dark text-foreground-light dark:text-foreground-dark">
      <div className="flex min-h-screen">
        <aside className="w-64 flex-shrink-0 bg-card-light dark:bg-card-dark border-r border-border-light dark:border-border-dark flex flex-col">
          <div className="h-16 flex items-center justify-center border-b border-border-light dark:border-border-dark">
            <h1 className="text-xl font-bold text-primary">Sacramentos</h1>
          </div>
          <nav className="flex-1 px-4 py-6 space-y-2">
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary font-semibold">
              <span className="material-symbols-outlined">dashboard</span>
              <span>Dashboard</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">add_box</span>
              <span>Digitalización</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">document_scanner</span>
              <span>Revisión OCR</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">menu_book</span>
              <span>Registros</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">group</span>
              <span>Personas</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">import_contacts</span>
              <span>Libros</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">search</span>
              <span>Búsqueda</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">workspace_premium</span>
              <span>Certificados</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">control_point_duplicate</span>
              <span>Duplicados</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">manage_accounts</span>
              <span>Usuarios</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">policy</span>
              <span>Auditoría</span>
            </a>
            <a href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-primary/10 dark:hover:bg-primary/20 transition-colors">
              <span className="material-symbols-outlined">bar_chart</span>
              <span>Reportes</span>
            </a>
          </nav>
        </aside>

        <main className="flex-1">
          <header className="h-16 bg-card-light dark:bg-card-dark border-b border-border-light dark:border-border-dark flex items-center justify-between px-6">
            <h2 className="text-2xl font-bold tracking-tight">Panel de Control</h2>
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

          <div className="p-6 space-y-8">
            <section>
              <h3 className="text-xl font-semibold mb-4">KPIs</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-card-light dark:bg-card-dark p-6 rounded-lg border border-border-light dark:border-border-dark">
                  <p className="text-muted-light dark:text-muted-dark text-sm font-medium">Pendientes de Revisión</p>
                  <p className="text-3xl font-bold mt-1">123</p>
                </div>
                <div className="bg-card-light dark:bg-card-dark p-6 rounded-lg border border-border-light dark:border-border-dark">
                  <p className="text-muted-light dark:text-muted-dark text-sm font-medium">% Validados</p>
                  <p className="text-3xl font-bold mt-1 text-primary">85%</p>
                </div>
                <div className="bg-card-light dark:bg-card-dark p-6 rounded-lg border border-border-light dark:border-border-dark">
                  <p className="text-muted-light dark:text-muted-dark text-sm font-medium">Duplicados Detectados</p>
                  <p className="text-3xl font-bold mt-1 text-accent-gold">5</p>
                </div>
                <div className="bg-card-light dark:bg-card-dark p-6 rounded-lg border border-border-light dark:border-border-dark">
                  <p className="text-muted-light dark:text-muted-dark text-sm font-medium">Libro Más Consultado</p>
                  <p className="text-xl font-bold mt-2 truncate">Bautismos 2023</p>
                </div>
              </div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <section className="lg:col-span-2">
                <h3 className="text-xl font-semibold mb-4">Línea de Tiempo de Auditoría</h3>
                <div className="bg-card-light dark:bg-card-dark p-6 rounded-lg border border-border-light dark:border-border-dark">
                  <div className="flow-root">
                    <ul className="-mb-8">
                      <li>
                        <div className="relative pb-8">
                          <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-border-light dark:bg-border-dark" aria-hidden="true"></span>
                          <div className="relative flex items-start space-x-3">
                            <div>
                              <div className="relative px-1">
                                <div className="h-8 w-8 bg-primary/10 rounded-full ring-8 ring-card-light dark:ring-card-dark flex items-center justify-center">
                                  <span className="material-symbols-outlined text-primary text-base">edit_note</span>
                                </div>
                              </div>
                            </div>
                            <div className="min-w-0 flex-1 py-1.5">
                              <div className="text-sm">
                                <span className="font-semibold">Ana García</span> realizó cambios en el registro de matrimonio de Carlos Pérez y Sofía Rodríguez
                              </div>
                              <div className="mt-1 text-xs text-muted-light dark:text-muted-dark">
                                <p>Hace 2 horas</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                      <li>
                        <div className="relative pb-8">
                          <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-border-light dark:bg-border-dark" aria-hidden="true"></span>
                          <div className="relative flex items-start space-x-3">
                            <div>
                              <div className="relative px-1">
                                <div className="h-8 w-8 bg-accent-gold/10 rounded-full ring-8 ring-card-light dark:ring-card-dark flex items-center justify-center">
                                  <span className="material-symbols-outlined text-accent-gold text-base">warning</span>
                                </div>
                              </div>
                            </div>
                            <div className="min-w-0 flex-1 py-1.5">
                              <div className="text-sm">
                                Sistema detectó posible duplicado en el registro de bautismo de Juan Martínez.
                              </div>
                              <div className="mt-1 text-xs text-muted-light dark:text-muted-dark">
                                <p>Hace 5 horas</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                      <li>
                        <div className="relative">
                          <div className="relative flex items-start space-x-3">
                            <div>
                              <div className="relative px-1">
                                <div className="h-8 w-8 bg-primary/10 rounded-full ring-8 ring-card-light dark:ring-card-dark flex items-center justify-center">
                                  <span className="material-symbols-outlined text-primary text-base">search</span>
                                </div>
                              </div>
                            </div>
                            <div className="min-w-0 flex-1 py-1.5">
                              <div className="text-sm">
                                <span className="font-semibold">Luis Fernández</span> consultó el libro de defunciones 2022
                              </div>
                              <div className="mt-1 text-xs text-muted-light dark:text-muted-dark">
                                <p>Ayer</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <div className="space-y-8">
                <section>
                  <h3 className="text-xl font-semibold mb-4">Acceso Rápido</h3>
                  <div className="space-y-4">
                    <button className="w-full flex items-center justify-center gap-2 h-12 px-6 rounded-lg bg-primary text-white font-semibold shadow-md hover:bg-primary/90 transition-colors">
                      <span className="material-symbols-outlined">add_box</span>
                      <span>Digitalización</span>
                    </button>
                    <button className="w-full flex items-center justify-center gap-2 h-12 px-6 rounded-lg bg-primary/20 dark:bg-primary/30 text-primary font-semibold hover:bg-primary/30 dark:hover:bg-primary/40 transition-colors">
                      <span className="material-symbols-outlined">document_scanner</span>
                      <span>Revisión</span>
                    </button>
                    <button className="w-full flex items-center justify-center gap-2 h-12 px-6 rounded-lg bg-primary/20 dark:bg-primary/30 text-primary font-semibold hover:bg-primary/30 dark:hover:bg-primary/40 transition-colors">
                      <span className="material-symbols-outlined">workspace_premium</span>
                      <span>Certificados</span>
                    </button>
                  </div>
                </section>
                <section>
                  <h3 className="text-xl font-semibold mb-4">Auditoría por Usuario</h3>
                  <div className="bg-card-light dark:bg-card-dark p-6 rounded-lg border border-border-light dark:border-border-dark space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <img alt="Avatar de Ana García" className="w-10 h-10 rounded-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBZYNZXTkUVY03t1EfwJQUdekZ9HUafc3BFL9ec0WQ-WKQLpoi_gkSGqirr6xKDRfnTL29gW-L-cqe-gniYtkCNAIrtS_XW-4YJg9NJ3mNc1thR5Dldjz3FSemyBoBertXnJKpP3GOpAVcOQy3ldNpf59wfBfY_uoDKqRBo_6Y06TBUIA2ZdkUWTPHyBOKbzM_CcXEP-TSwSEFcpGGEL0mk_fsffmdYYJEC_BktAdmdeRsZrce44sbSHt2TNURSbkPQVVzr4dn4gz0" />
                        <div>
                          <p className="font-semibold text-sm">Ana García</p>
                          <p className="text-xs text-muted-light dark:text-muted-dark">Digitalizadora</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-sm">12</p>
                        <p className="text-xs text-muted-light dark:text-muted-dark">acciones hoy</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <img alt="Avatar de Luis Fernández" className="w-10 h-10 rounded-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuCB69WGepNhZgzvTM9JeZs82KOsI2KCn4cjCJ6MdFlHGTMDeBqkwzGeVNHc4SalbApAco0IkIfq7P1ePBmVKBWDR17gYEDO1lSwy5mnIBxMzSA4M7KaCsKJAlrW30J5swZLNwnWJMU3QNip9B8bR6L_OMo4gTIxbCv1J0q-cUrwDp4L1vQ0gWk4LGfcG1F9OZHo89xsdB9QPQPRfa1UY4DQVV6tuxY3xqIR8EB8V0RwyO-aOVWYJjLXyoyVECrzwVsIj72eny7Wa0c" />
                        <div>
                          <p className="font-semibold text-sm">Luis Fernández</p>
                          <p className="text-xs text-muted-light dark:text-muted-dark">Revisor</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-sm">8</p>
                        <p className="text-xs text-muted-light dark:text-muted-dark">acciones hoy</p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <img alt="Avatar de Administrador" className="w-10 h-10 rounded-full object-cover" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBMk_WnYIase354r69oXFK_iITqvn5ay8pAjZj3vmZ-1_vF4_alZOUC2Vic0_EIp_fJyv8OO9Dq6tYxhz6mbKO-chpL61q3_KVXoq7MbMttyd6d0j3H-eVLBGOr1zfmFBOkFB4x8e2Jl_K0srV7poc-C5Mi3PerstL85S7_IKUSZ3YPx6MINDsNonTnIEpu3YdSnN2EySd55GOspBjmnzBoNbtCevPovWpOZNw3pjrritTlrNaGOh07rbFbBiQmUy7KgZ0k6yANP-8" />
                        <div>
                          <p className="font-semibold text-sm">Admin</p>
                          <p className="text-xs text-muted-light dark:text-muted-dark">Administrador</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-sm">5</p>
                        <p className="text-xs text-muted-light dark:text-muted-dark">acciones hoy</p>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
