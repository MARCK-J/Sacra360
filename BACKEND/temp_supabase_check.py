import os
import psycopg2

DB_URL = os.getenv("SUPABASE_DB_URL")
sql_file = os.path.join("sql", "Insert_Test_Users.sql")
required = ["admin@sacra360.com", "digitalizador@sacra360.com"]

if not DB_URL:
    raise RuntimeError("Missing SUPABASE_DB_URL environment variable")

conn = psycopg2.connect(DB_URL)
conn.autocommit = False
try:
    with conn.cursor() as cur:
        cur.execute("select email from usuarios where lower(email) in (lower(%s), lower(%s)) order by email;", (required[0], required[1]))
        before = [r[0] for r in cur.fetchall()]
        print(f"before_required_users={before}")

        missing = [e for e in required if e.lower() not in {x.lower() for x in before}]
        print(f"missing_before={missing}")

        if missing:
            with open(sql_file, "r", encoding="utf-8") as f:
                sql = f.read()
            cur.execute(sql)
            conn.commit()
            print("insert_test_users_executed=True")
        else:
            conn.rollback()
            print("insert_test_users_executed=False")

        cur.execute("select email from usuarios where lower(email) in (lower(%s), lower(%s)) order by email;", (required[0], required[1]))
        after = [r[0] for r in cur.fetchall()]
        print(f"after_required_users={after}")
finally:
    conn.close()
