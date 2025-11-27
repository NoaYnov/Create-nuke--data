#!/usr/bin/env python3
"""
Script de sauvegarde de la base de données PostgreSQL
Crée une sauvegarde complète au format SQL
"""
import sys
import os
from datetime import datetime
from pathlib import Path
import subprocess


def main():
    """Crée une sauvegarde de la base de données"""
    print("=" * 60)
    print("  Create Nuclear Stats - Database Backup")
    print("=" * 60)
    
    # Configuration
    backup_dir = Path(__file__).parent.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"backup_{timestamp}.sql"
    
    # Récupérer les variables d'environnement
    db_name = os.getenv("POSTGRES_DB", "createnuclear_stats")
    db_user = os.getenv("POSTGRES_USER", "createnuclear")
    db_password = os.getenv("POSTGRES_PASSWORD", "")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    
    print(f"\n📊 Database: {db_name}")
    print(f"📁 Backup file: {backup_file}")
    
    try:
        # Vérifier si on utilise Docker
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=createnuclear-postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if "createnuclear-postgres" in result.stdout:
            # Utiliser Docker
            print("\n🐳 Using Docker container...")
            cmd = [
                "docker", "compose", "exec", "-T", "postgres",
                "pg_dump", "-U", db_user, db_name
            ]
        else:
            # Utiliser pg_dump local
            print("\n💻 Using local pg_dump...")
            env = os.environ.copy()
            env["PGPASSWORD"] = db_password
            cmd = [
                "pg_dump",
                "-h", db_host,
                "-p", db_port,
                "-U", db_user,
                "-d", db_name,
                "--no-password"
            ]
        
        print(f"⏳ Creating backup...")
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
        
        # Vérifier la taille du fichier
        size_bytes = backup_file.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        print(f"✓ Backup created successfully")
        print(f"   Size: {size_mb:.2f} MB")
        
        # Compression optionnelle
        try:
            import gzip
            import shutil
            
            print(f"\n📦 Compressing backup...")
            compressed_file = backup_file.with_suffix('.sql.gz')
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = compressed_file.stat().st_size / (1024 * 1024)
            compression_ratio = (1 - compressed_size / size_mb) * 100
            
            print(f"✓ Compressed: {compressed_size:.2f} MB ({compression_ratio:.1f}% reduction)")
            
            # Supprimer le fichier non compressé
            backup_file.unlink()
            print(f"✓ Removed uncompressed file")
            
            final_file = compressed_file
        except ImportError:
            print("⚠ gzip module not available, skipping compression")
            final_file = backup_file
        
        # Nettoyer les anciennes sauvegardes (garder les 7 dernières)
        print(f"\n🧹 Cleaning old backups...")
        backups = sorted(backup_dir.glob("backup_*.sql*"), reverse=True)
        
        if len(backups) > 7:
            for old_backup in backups[7:]:
                old_backup.unlink()
                print(f"   Removed: {old_backup.name}")
        
        print(f"\n✓ Kept {min(len(backups), 7)} most recent backups")
        
        print("\n" + "=" * 60)
        print(f"✓ Backup completed: {final_file.name}")
        print("=" * 60)
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Backup failed: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
