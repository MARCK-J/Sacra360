import psycopg2

DB_URL = "postgresql://postgres.kzgzkhklvemxajgvzgsr:Arzlpz$42026@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

conn = psycopg2.connect(DB_URL)
try:
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT setval(pg_get_serial_sequence('libros','id_libro'), COALESCE((SELECT MAX(id_libro) FROM libros),1), true);")
            value = cur.fetchone()[0]
            print(f"setval_result={value}")
finally:
    conn.close()
