"""
Script para actualizar contraseñas de usuarios de prueba
"""
import psycopg2
from passlib.context import CryptContext

# Configuración
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Conexión a la base de datos
conn = psycopg2.connect(
    host="sacra360-postgres",
    port=5432,
    database="sacra360",
    user="postgres",
    password="lolsito101"
)

cur = conn.cursor()

# Generar nuevos hashes
admin_hash = pwd_context.hash("admin123")
digitalizador_hash = pwd_context.hash("digitalizador123")

print(f"Hash admin: {admin_hash}")
print(f"Hash digitalizador: {digitalizador_hash}")

# Deshabilitar trigger temporalmente
cur.execute("ALTER TABLE usuarios DISABLE TRIGGER update_usuarios_updated_at")
print("Trigger deshabilitado")

# Actualizar usuarios
cur.execute(
    "UPDATE usuarios SET contrasenia = %s WHERE email = %s",
    (admin_hash, "admin@sacra360.com")
)
print(f"Admin actualizado: {cur.rowcount} filas")

cur.execute(
    "UPDATE usuarios SET contrasenia = %s WHERE email = %s",
    (digitalizador_hash, "digitalizador@sacra360.com")
)
print(f"Digitalizador actualizado: {cur.rowcount} filas")

# Rehabilitar trigger
cur.execute("ALTER TABLE usuarios ENABLE TRIGGER update_usuarios_updated_at")
print("Trigger rehabilitado")

# Commit y cerrar
conn.commit()
cur.close()
conn.close()

print("✅ Contraseñas actualizadas exitosamente")
