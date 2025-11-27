#!/usr/bin/env python3
"""
Script de restauration de la base de données PostgreSQL
Restaure une sauvegarde SQL dans la base de données
"""
import sys
import os
from pathlib import Path
import subprocess
from datetime import datetime


def list_backups(backup_dir):
    """Liste toutes les sauvegardes disponibles"""
    backups = sorted(backup_dir.glob("backup_*.sql*"), reverse=True)
    return backups


def main():
    """Restaure une sauvegarde de la base de données"""
    print("=" * 60)
    print("  Create Nuclear Stats - Database Restore")
    print("=" * 60)
    
    # Configuration
    backup_dir = Path(__file__).parent.parent / "backups"
    
    if not backup_dir.exists():
        print(f"\n✗ Backup directory not found: {backup_dir}")
        return 1
    
    # Lister les sauvegardes
    backups = list_backups(backup_dir)
    
    if not backups:
        print(f"\n✗ No backups found in {backup_dir}")
        return 1
    
    print(f"\n📁 Available backups:")
    for i, backup in enumerate(backups, 1):
        size_mb = backup.stat().st_size / (1024 * 1024)
        # Extraire la date du nom de fichier
        try:
            timestamp = backup.stem.replace('backup_', '').replace('.sql', '')
            date = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            date_str = "Unknown date"
        
        print(f"   {i}. {backup.name} ({size_mb:.2f} MB) - {date_str}")
    
    # Sélectionner une sauvegarde
    if len(sys.argv) > 1:
        # Fichier spécifié en argument
        backup_file = Path(sys.argv[1])
        if not backup_file.exists():
            print(f"\n✗ Backup file not found: {backup_file}")
            return 1
    else:
        # Sélection interactive
        print(f"\n📋 Select backup to restore (1-{len(backups)}, or 0 to cancel):")
        try:
            choice = int(input("Choice: "))
            if choice == 0:
                print("Cancelled")
                return 0
            if choice < 1 or choice > len(backups):
                print("✗ Invalid choice")
                return 1
            backup_file = backups[choice - 1]
        except (ValueError, KeyboardInterrupt):
            print("\n✗ Cancelled")
            return 1
    
    print(f"\n⚠️  WARNING: This will REPLACE all data in the database!")
    print(f"   Backup: {backup_file.name}")
    
    confirm = input("\nType 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("✗ Cancelled")
        return 0
    
    # Récupérer les variables d'environnement
    db_name = os.getenv("POSTGRES_DB", "createnuclear_stats")
    db_user = os.getenv("POSTGRES_USER", "createnuclear")
    db_password = os.getenv("POSTGRES_PASSWORD", "")
    db_host = os.getenv("POSTGRES_HOST", "localhost")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    
    try:
        # Vérifier si on utilise Docker
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=createnuclear-postgres", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=False
        )
        
        # Décompresser si nécessaire
        if backup_file.suffix == '.gz':
            print(f"\n📦 Decompressing backup...")
            import gzip
            import shutil
            
            decompressed = backup_file.with_suffix('')
            with gzip.open(backup_file, 'rb') as f_in:
                with open(decompressed, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            backup_file = decompressed
            print(f"✓ Decompressed to {backup_file.name}")
        
        if "createnuclear-postgres" in result.stdout:
            # Utiliser Docker
            print(f"\n🐳 Using Docker container...")
            
            # Lire le fichier de sauvegarde
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            
            # Restaurer via Docker
            cmd = [
                "docker", "compose", "exec", "-T", "postgres",
                "psql", "-U", db_user, "-d", db_name
            ]
            
            print(f"⏳ Restoring backup...")
            result = subprocess.run(
                cmd,
                input=backup_content,
                capture_output=True,
                text=True,
                check=True
            )
            
        else:
            # Utiliser psql local
            print(f"\n💻 Using local psql...")
            env = os.environ.copy()
            env["PGPASSWORD"] = db_password
            
            cmd = [
                "psql",
                "-h", db_host,
                "-p", db_port,
                "-U", db_user,
                "-d", db_name,
                "-f", str(backup_file)
            ]
            
            print(f"⏳ Restoring backup...")
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
        
        print(f"✓ Restore completed successfully")
        
        # Vérifier les données
        print(f"\n🔍 Verifying data...")
        
        if "createnuclear-postgres" in result.stdout:
            verify_cmd = [
                "docker", "compose", "exec", "-T", "postgres",
                "psql", "-U", db_user, "-d", db_name,
                "-c", "SELECT COUNT(*) FROM daily_stats;"
            ]
        else:
            verify_cmd = [
                "psql",
                "-h", db_host,
                "-p", db_port,
                "-U", db_user,
                "-d", db_name,
                "-c", "SELECT COUNT(*) FROM daily_stats;"
            ]
        
        result = subprocess.run(
            verify_cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print("✓ Database verified")
        
        # Nettoyer le fichier décompressé si nécessaire
        if backup_file.suffix == '.sql' and backup_file.with_suffix('.sql.gz').exists():
            backup_file.unlink()
            print(f"✓ Cleaned up temporary file")
        
        print("\n" + "=" * 60)
        print("✓ Restore completed successfully")
        print("=" * 60)
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Restore failed: {e}")
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
