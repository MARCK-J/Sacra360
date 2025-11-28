"""
Script para crear usuarios de prueba para todos los roles
Sistema Sacra360
"""
import psycopg2
from passlib.context import CryptContext
from datetime import date

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

print("=" * 60)
print("CREANDO USUARIOS PARA CADA ROL")
print("=" * 60)
print()

# Definir usuarios para cada rol
usuarios = [
    {
        "rol_id": 1,
        "nombre": "Carlos",
        "apellido_paterno": "Mendoza",
        "apellido_materno": "López",
        "email": "admin@sacra360.com",
        "password": "Admin123!",
        "rol_nombre": "Administrador"
    },
    {
        "rol_id": 2,
        "nombre": "Ana",
        "apellido_paterno": "Rodríguez",
        "apellido_materno": "Martínez",
        "email": "revisor@sacra360.com",
        "password": "Revisor123!",
        "rol_nombre": "Revisor"
    },
    {
        "rol_id": 3,
        "nombre": "Juan",
        "apellido_paterno": "Pérez",
        "apellido_materno": "García",
        "email": "digitalizador@sacra360.com",
        "password": "Digita123!",
        "rol_nombre": "Digitalizador"
    },
    {
        "rol_id": 4,
        "nombre": "Sofía",
        "apellido_paterno": "Gómez",
        "apellido_materno": "Torres",
        "email": "consultor@sacra360.com",
        "password": "Consul123!",
        "rol_nombre": "Consultor"
    }
]

# Deshabilitar trigger temporalmente
cur.execute("ALTER TABLE usuarios DISABLE TRIGGER update_usuarios_updated_at")
print("✓ Trigger deshabilitado")
print()

# Crear o actualizar cada usuario
for usuario in usuarios:
    # Generar hash de contraseña
    hash_password = pwd_context.hash(usuario["password"])
    
    # Verificar si el usuario ya existe
    cur.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (usuario["email"],))
    existing = cur.fetchone()
    
    if existing:
        # Actualizar usuario existente
        cur.execute("""
            UPDATE usuarios 
            SET rol_id = %s,
                nombre = %s,
                apellido_paterno = %s,
                apellido_materno = %s,
                contrasenia = %s,
                activo = TRUE
            WHERE email = %s
        """, (
            usuario["rol_id"],
            usuario["nombre"],
            usuario["apellido_paterno"],
            usuario["apellido_materno"],
            hash_password,
            usuario["email"]
        ))
        print(f"✓ {usuario['rol_nombre']}: Usuario actualizado")
    else:
        # Insertar nuevo usuario
        cur.execute("""
            INSERT INTO usuarios (
                rol_id, nombre, apellido_paterno, apellido_materno,
                email, contrasenia, fecha_creacion, activo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            usuario["rol_id"],
            usuario["nombre"],
            usuario["apellido_paterno"],
            usuario["apellido_materno"],
            usuario["email"],
            hash_password,
            date.today(),
            True
        ))
        print(f"✓ {usuario['rol_nombre']}: Usuario creado")
    
    print(f"  Email: {usuario['email']}")
    print(f"  Password: {usuario['password']}")
    print()

# Rehabilitar trigger
cur.execute("ALTER TABLE usuarios ENABLE TRIGGER update_usuarios_updated_at")
print("✓ Trigger rehabilitado")
print()

# Commit
conn.commit()

# Mostrar resumen
print("=" * 60)
print("RESUMEN DE USUARIOS CREADOS")
print("=" * 60)
print()

cur.execute("""
    SELECT 
        u.id_usuario,
        u.nombre || ' ' || u.apellido_paterno as nombre_completo,
        u.email,
        r.nombre as rol,
        u.activo
    FROM usuarios u
    LEFT JOIN roles r ON u.rol_id = r.id_rol
    WHERE u.email IN ('admin@sacra360.com', 'revisor@sacra360.com', 
                      'digitalizador@sacra360.com', 'consultor@sacra360.com')
    ORDER BY u.rol_id
""")

usuarios_creados = cur.fetchall()
for user in usuarios_creados:
    print(f"ID: {user[0]} | {user[1]} | {user[2]} | Rol: {user[3]} | Activo: {user[4]}")

print()
print("=" * 60)
print("✅ PROCESO COMPLETADO EXITOSAMENTE")
print("=" * 60)

# Cerrar conexión
cur.close()
conn.close()
