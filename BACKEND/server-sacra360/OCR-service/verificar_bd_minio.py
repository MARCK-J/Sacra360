#!/usr/bin/env python3
"""
Script para verificar los registros guardados en PostgreSQL
con las URLs de Minio
"""

import psycopg2
import json
from datetime import datetime

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'sacra360',
    'user': 'postgres',
    'password': 'password'
}

def verificar_base_datos():
    """Verificar registros en la base de datos"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🗄️ VERIFICACIÓN DE BASE DE DATOS")
        print("=" * 50)
        
        # Verificar documentos digitalizados
        cursor.execute("""
            SELECT 
                id_documento,
                libros_id,
                tipo_sacramento,
                imagen_url,
                modelo_fuente,
                confianza,
                fecha_procesamiento
            FROM documento_digitalizado 
            ORDER BY fecha_procesamiento DESC
            LIMIT 5
        """)
        
        documentos = cursor.fetchall()
        
        print(f"📄 Documentos digitalizados (últimos 5):")
        for doc in documentos:
            id_doc, libro_id, tipo, url, modelo, confianza, fecha = doc
            print(f"   🆔 ID: {id_doc}")
            print(f"   📚 Libro: {libro_id}")
            print(f"   ⛪ Sacramento: {tipo}")
            print(f"   🔗 URL: {url}")
            print(f"   🤖 Modelo: {modelo}")
            print(f"   📊 Confianza: {confianza:.3f}")
            print(f"   📅 Fecha: {fecha}")
            print(f"   {'✅ URL Minio' if 'minio:9000' in url else '❌ URL no válida'}")
            print("   " + "-" * 40)
        
        # Verificar resultados OCR
        cursor.execute("""
            SELECT COUNT(*) as total_campos,
                   AVG(confianza) as confianza_promedio
            FROM ocr_resultado
        """)
        
        stats = cursor.fetchone()
        print(f"\n📊 Estadísticas OCR:")
        print(f"   🔢 Total campos extraídos: {stats[0]}")
        print(f"   📈 Confianza promedio: {stats[1]:.2f}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🔍 Verificando integración en base de datos...\n")
    
    if verificar_base_datos():
        print("\n✅ Verificación completada")
    else:
        print("\n❌ Error en la verificación")

if __name__ == "__main__":
    main()