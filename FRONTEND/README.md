# Frontend Sacra360 (Vite + React)

## Variables de entorno

Este frontend está preparado para usar variables públicas de Vite en Vercel.

1. Copia `.env.example` a `.env` para desarrollo local.
2. En Vercel, configura estas variables en `Project Settings -> Environment Variables`:

- `VITE_API_BASE_URL`
- `VITE_AUTH_API_URL`
- `VITE_API_URL` (alias legacy opcional)

Importante:

- Nunca subas secretos reales al repositorio.
- Todo valor sensible (tokens, passwords, keys) debe vivir solo en variables de entorno del proveedor.

## Deploy en Vercel

- Build command: `npm run build`
- Output directory: `dist`

El frontend ya no depende de `localhost` ni del proxy de desarrollo para consumir el backend.
