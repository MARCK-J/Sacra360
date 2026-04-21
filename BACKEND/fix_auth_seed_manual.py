import psycopg2

DB_URL = "postgresql://postgres.kzgzkhklvemxajgvzgsr:Arzlpz$42026@aws-1-us-east-1.pooler.supabase.com:6543/postgres"
ADMIN_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyJJb3hA7YDe"  # admin123


def ensure_user(cur, email, rol_id, nombre, ap_paterno, ap_materno):
    cur.execute(
        "SELECT id_usuario FROM usuarios WHERE lower(email) = lower(%s) LIMIT 1",
        (email,),
    )
    row = cur.fetchone()

    if row:
        user_id = row[0]
        cur.execute(
            """
            UPDATE usuarios
            SET rol_id = %s,
                nombre = %s,
                apellido_paterno = %s,
                apellido_materno = %s,
                contrasenia = %s,
                activo = TRUE
            WHERE id_usuario = %s
            """,
            (rol_id, nombre, ap_paterno, ap_materno, ADMIN_HASH, user_id),
        )
        print(f"updated: {email} (id={user_id})")
    else:
        cur.execute(
            """
            INSERT INTO usuarios (
                rol_id,
                nombre,
                apellido_paterno,
                apellido_materno,
                email,
                contrasenia,
                fecha_creacion,
                activo
            ) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE, TRUE)
            RETURNING id_usuario
            """,
            (rol_id, nombre, ap_paterno, ap_materno, email, ADMIN_HASH),
        )
        user_id = cur.fetchone()[0]
        print(f"inserted: {email} (id={user_id})")


conn = psycopg2.connect(DB_URL)
conn.autocommit = False

try:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT setval(
                pg_get_serial_sequence('usuarios', 'id_usuario'),
                COALESCE((SELECT MAX(id_usuario) FROM usuarios), 1),
                true
            )
            """
        )
        seq = cur.fetchone()[0]
        print(f"sequence_setval={seq}")

        ensure_user(cur, "admin@sacra360.com", 1, "Admin", "Sistema", "Sacra360")
        ensure_user(cur, "digitalizador@sacra360.com", 3, "Juan", "Perez", "Garcia")

        conn.commit()

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id_usuario, email, rol_id, activo
            FROM usuarios
            WHERE lower(email) IN (lower(%s), lower(%s))
            ORDER BY email
            """,
            ("admin@sacra360.com", "digitalizador@sacra360.com"),
        )
        for r in cur.fetchall():
            print(f"user={r}")
finally:
    conn.close()
