#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Vérifie la connexion et initialise les tables si nécessaire
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import StatsDatabase
from src.config import DATABASE_URL


def main():
    """Initialise la base de données"""
    print("=" * 60)
    print("  Create Nuclear Stats - Database Initialization")
    print("=" * 60)
    
    try:
        print(f"\n📊 Connecting to database...")
        print(f"   URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
        
        db = StatsDatabase(DATABASE_URL)
        print("✓ Connected successfully")
        
        print("\n📋 Creating tables...")
        db.create_tables()
        print("✓ Tables created/verified")
        
        # Vérifier les tables
        print("\n🔍 Verifying tables...")
        db.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = db.cursor.fetchall()
        
        if tables:
            print("✓ Found tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("⚠ No tables found")
        
        # Vérifier les index
        print("\n📊 Checking indexes...")
        db.cursor.execute("""
            SELECT indexname, tablename 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        indexes = db.cursor.fetchall()
        
        if indexes:
            print(f"✓ Found {len(indexes)} indexes")
            current_table = None
            for idx_name, table_name in indexes:
                if table_name != current_table:
                    print(f"\n   {table_name}:")
                    current_table = table_name
                print(f"      - {idx_name}")
        
        # Statistiques
        print("\n📈 Database statistics:")
        db.cursor.execute("SELECT COUNT(*) FROM daily_stats")
        daily_count = db.cursor.fetchone()[0]
        print(f"   Daily stats: {daily_count} records")
        
        db.cursor.execute("SELECT COUNT(*) FROM version_stats")
        version_count = db.cursor.fetchone()[0]
        print(f"   Version stats: {version_count} records")
        
        db.cursor.execute("SELECT COUNT(*) FROM modpack_stats")
        modpack_count = db.cursor.fetchone()[0]
        print(f"   Modpack stats: {modpack_count} records")
        
        db.close()
        
        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
