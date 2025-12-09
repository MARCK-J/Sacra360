"""
Script para verificar schema de tabla ocr_resultado
"""

import psycopg2

conn_string = "postgresql://postgres:lolsito101@localhost:5433/sacra360"

try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    print("=" * 70)
    print("📋 SCHEMA DE TABLA 'ocr_resultado'")
    print("=" * 70)
    
    # Ver columnas
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'ocr_resultado'
        ORDER BY ordinal_position
    """)
    
    for row in cur.fetchall():
        nullable = "NULL" if row[2] == "YES" else "NOT NULL"
        default = f"DEFAULT {row[3]}" if row[3] else ""
        print(f"  {row[0]:<25} {row[1]:<20} {nullable:<10} {default}")
    
    # Mostrar un ejemplo de datos
    cur.execute("""
        SELECT id_ocr, documento_id, tupla_numero, datos_ocr, confianza, fuente_modelo, validado
        FROM ocr_resultado 
        WHERE documento_id = 42 
        LIMIT 1
    """)
    
    print("\n" + "=" * 70)
    print("📊 EJEMPLO DE DATOS (Documento 42, Tupla 1)")
    print("=" * 70)
    
    row = cur.fetchone()
    if row:
        print(f"ID OCR: {row[0]}")
        print(f"Documento ID: {row[1]}")
        print(f"Tupla número: {row[2]}")
        print(f"Confianza: {row[4]}")
        print(f"Modelo: {row[5]}")
        print(f"Validado: {row[6]}")
        print(f"\nDatos OCR (JSON):")
        import json
        print(json.dumps(row[3], indent=2, ensure_ascii=False))
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
