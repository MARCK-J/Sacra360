"""
Script para crear un libro temporal en PostgreSQL
"""

import psycopg2
import sys

# Conexión
conn_string = "postgresql://postgres:lolsito101@localhost:5433/sacra360"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    # Verificar si existe libro temporal
    cur.execute("SELECT id_libro FROM libros WHERE id_libro = -1")
    if cur.fetchone():
        print("✅ Libro temporal (ID=-1) ya existe")
    else:
        # Crear libro temporal
        cur.execute("""
            INSERT INTO libros (id_libro, nombre, fecha_inicio, fecha_fin, observaciones)
            VALUES (-1, 'Libro Temporal - OCR V2', '2000-01-01', '2099-12-31', 'Libro temporal para documentos sin asignar')
            ON CONFLICT (id_libro) DO NOTHING
        """)
        conn.commit()
        print("✅ Libro temporal creado (ID=-1)")
    
    # Mostrar libros existentes
    cur.execute("SELECT id_libro, nombre FROM libros ORDER BY id_libro LIMIT 10")
    print("\n📚 Libros en base de datos:")
    for row in cur.fetchall():
        print(f"   {row[0]}: {row[1]}")
    
    cur.close()
    conn.close()
    print("\n✅ Operación completada")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
