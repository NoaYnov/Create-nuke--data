#!/usr/bin/env python3
"""
Script de migration de la base de données
Gère les migrations de schéma de manière sécurisée
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import StatsDatabase
from config import DATABASE_URL


class Migration:
    """Classe de base pour les migrations"""
    
    def __init__(self, db: StatsDatabase):
        self.db = db
        self.cursor = db.cursor
        self.conn = db.conn
    
    def up(self):
        """Appliquer la migration"""
        raise NotImplementedError
    
    def down(self):
        """Annuler la migration"""
        raise NotImplementedError


class AddUpdatedAtColumns(Migration):
    """
    Migration: Ajouter les colonnes updated_at
    Version: 2024-01-01
    """
    
    def up(self):
        """Ajouter updated_at à toutes les tables"""
        print("  Adding updated_at columns...")
        
        tables = ['daily_stats', 'version_stats', 'modpack_stats']
        
        for table in tables:
            # Vérifier si la colonne existe déjà
            self.cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = '{table}' AND column_name = 'updated_at'
            """)
            
            if not self.cursor.fetchone():
                self.cursor.execute(f"""
                    ALTER TABLE {table} 
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                print(f"    ✓ Added updated_at to {table}")
            else:
                print(f"    ⊘ Column updated_at already exists in {table}")
        
        # Créer la fonction trigger si elle n'existe pas
        self.cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
        print("    ✓ Created/updated trigger function")
        
        # Créer les triggers
        for table in tables:
            trigger_name = f"update_{table}_updated_at"
            
            # Supprimer le trigger s'il existe
            self.cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table}")
            
            # Créer le trigger
            self.cursor.execute(f"""
                CREATE TRIGGER {trigger_name}
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
            """)
            print(f"    ✓ Created trigger for {table}")
    
    def down(self):
        """Supprimer les colonnes updated_at"""
        print("  Removing updated_at columns...")
        
        tables = ['daily_stats', 'version_stats', 'modpack_stats']
        
        for table in tables:
            # Supprimer le trigger
            trigger_name = f"update_{table}_updated_at"
            self.cursor.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table}")
            
            # Supprimer la colonne
            self.cursor.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS updated_at")
            print(f"    ✓ Removed updated_at from {table}")
        
        # Supprimer la fonction
        self.cursor.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
        print("    ✓ Removed trigger function")


class AddIndexes(Migration):
    """
    Migration: Ajouter des index supplémentaires pour les performances
    Version: 2024-01-02
    """
    
    def up(self):
        """Ajouter les index"""
        print("  Adding performance indexes...")
        
        indexes = [
            ("idx_daily_stats_platform", "daily_stats", "(platform, date DESC)"),
            ("idx_version_stats_name", "version_stats", "(platform, version_name, date DESC)"),
            ("idx_modpack_stats_slug", "modpack_stats", "(platform, modpack_slug, date DESC)"),
        ]
        
        for idx_name, table, columns in indexes:
            self.cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {idx_name} 
                ON {table} {columns}
            """)
            print(f"    ✓ Created index {idx_name}")
    
    def down(self):
        """Supprimer les index"""
        print("  Removing performance indexes...")
        
        indexes = [
            "idx_daily_stats_platform",
            "idx_version_stats_name",
            "idx_modpack_stats_slug",
        ]
        
        for idx_name in indexes:
            self.cursor.execute(f"DROP INDEX IF EXISTS {idx_name}")
            print(f"    ✓ Removed index {idx_name}")


# Liste des migrations dans l'ordre
MIGRATIONS = [
    AddUpdatedAtColumns,
    AddIndexes,
]


def get_migration_table(db):
    """Créer la table de suivi des migrations"""
    db.cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.conn.commit()


def get_applied_migrations(db):
    """Récupérer la liste des migrations appliquées"""
    db.cursor.execute("SELECT migration_name FROM schema_migrations")
    return {row[0] for row in db.cursor.fetchall()}


def apply_migration(db, migration_class):
    """Appliquer une migration"""
    migration_name = migration_class.__name__
    
    print(f"\n📋 Applying migration: {migration_name}")
    print(f"   {migration_class.__doc__.strip() if migration_class.__doc__ else 'No description'}")
    
    try:
        migration = migration_class(db)
        migration.up()
        
        # Enregistrer la migration
        db.cursor.execute(
            "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
            (migration_name,)
        )
        db.conn.commit()
        
        print(f"✓ Migration {migration_name} applied successfully")
        return True
        
    except Exception as e:
        db.conn.rollback()
        print(f"✗ Migration {migration_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def rollback_migration(db, migration_class):
    """Annuler une migration"""
    migration_name = migration_class.__name__
    
    print(f"\n📋 Rolling back migration: {migration_name}")
    
    try:
        migration = migration_class(db)
        migration.down()
        
        # Supprimer l'enregistrement
        db.cursor.execute(
            "DELETE FROM schema_migrations WHERE migration_name = %s",
            (migration_name,)
        )
        db.conn.commit()
        
        print(f"✓ Migration {migration_name} rolled back successfully")
        return True
        
    except Exception as e:
        db.conn.rollback()
        print(f"✗ Rollback {migration_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Point d'entrée principal"""
    print("=" * 60)
    print("  Create Nuclear Stats - Database Migration")
    print("=" * 60)
    
    # Parser les arguments
    command = sys.argv[1] if len(sys.argv) > 1 else "up"
    
    if command not in ["up", "down", "status"]:
        print(f"\n✗ Unknown command: {command}")
        print("Usage: python migrate.py [up|down|status]")
        return 1
    
    try:
        print(f"\n📊 Connecting to database...")
        db = StatsDatabase(DATABASE_URL)
        print("✓ Connected successfully")
        
        # Créer la table de migrations
        get_migration_table(db)
        
        # Récupérer les migrations appliquées
        applied = get_applied_migrations(db)
        
        if command == "status":
            print(f"\n📋 Migration Status:")
            print(f"   Total migrations: {len(MIGRATIONS)}")
            print(f"   Applied: {len(applied)}")
            print(f"   Pending: {len(MIGRATIONS) - len(applied)}")
            
            print(f"\n📝 Details:")
            for migration_class in MIGRATIONS:
                name = migration_class.__name__
                status = "✓ Applied" if name in applied else "⊘ Pending"
                print(f"   {status} - {name}")
            
            return 0
        
        elif command == "up":
            print(f"\n⬆️  Running migrations...")
            
            success_count = 0
            for migration_class in MIGRATIONS:
                if migration_class.__name__ not in applied:
                    if apply_migration(db, migration_class):
                        success_count += 1
                    else:
                        print(f"\n✗ Migration failed, stopping")
                        return 1
                else:
                    print(f"\n⊘ Skipping {migration_class.__name__} (already applied)")
            
            if success_count > 0:
                print(f"\n✓ Applied {success_count} migration(s)")
            else:
                print(f"\n⊘ No pending migrations")
            
            return 0
        
        elif command == "down":
            print(f"\n⬇️  Rolling back last migration...")
            
            # Trouver la dernière migration appliquée
            last_applied = None
            for migration_class in reversed(MIGRATIONS):
                if migration_class.__name__ in applied:
                    last_applied = migration_class
                    break
            
            if last_applied:
                if rollback_migration(db, last_applied):
                    print(f"\n✓ Rollback successful")
                    return 0
                else:
                    return 1
            else:
                print(f"\n⊘ No migrations to rollback")
                return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    sys.exit(main())
