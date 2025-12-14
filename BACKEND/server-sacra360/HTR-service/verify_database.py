"""
Script para verificar la conexión a la base de datos
"""

import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verify_database_connection():
    """Verificar conexión a PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL no configurado en .env")
        return False
    
    print(f"🔍 Verificando conexión a: {database_url}")
    
    try:
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Conexión exitosa!")
            print(f"📦 PostgreSQL version: {version}")
            
            # Verificar tablas relevantes
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"\n📊 Tablas disponibles ({len(tables)}):")
            for table in tables:
                print(f"  - {table}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("HTR Service - Database Verification")
    print("=" * 60)
    verify_database_connection()
