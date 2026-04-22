import psycopg2
import os

DB_URL = os.getenv("SUPABASE_DB_URL")

if not DB_URL:
    raise RuntimeError("Missing SUPABASE_DB_URL environment variable")

conn = psycopg2.connect(DB_URL)
try:
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT setval(pg_get_serial_sequence('libros','id_libro'), COALESCE((SELECT MAX(id_libro) FROM libros),1), true);")
            value = cur.fetchone()[0]
            print(f"setval_result={value}")
finally:
    conn.close()
