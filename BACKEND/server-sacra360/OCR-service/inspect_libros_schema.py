"""
Script para ver el schema de la tabla libros
"""

import psycopg2

conn_string = "postgresql://postgres:lolsito101@localhost:5433/sacra360"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    # Ver columnas de libros
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'libros'
        ORDER BY ordinal_position
    """)
    
    print("📋 Schema de tabla 'libros':")
    print("-" * 60)
    for row in cur.fetchall():
        print(f"  {row[0]:<25} {row[1]:<20} NULL: {row[2]}")
    
    # Ver libros existentes
    cur.execute("SELECT * FROM libros LIMIT 3")
    colnames = [desc[0] for desc in cur.description]
    print(f"\n📚 Libros existentes (primeros 3):")
    print("-" * 60)
    print("Columnas:", colnames)
    for row in cur.fetchall():
        print(row)
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
