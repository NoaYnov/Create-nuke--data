#!/usr/bin/env python3
"""
Script d'import des données CSV/JSON vers PostgreSQL
Migre les données historiques stockées dans les fichiers
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import StatsDatabase
from src.config import DATABASE_URL, MODPACKS_CSV_PATH, MODPACKS_JSON_PATH


class DataImporter:
    """Importateur de données vers PostgreSQL"""
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or DATABASE_URL
        self.db = None
    
    def connect_database(self) -> bool:
        """Connexion à la base de données"""
        try:
            self.db = StatsDatabase(self.db_url)
            print("✓ Connected to database")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def import_modpacks_from_csv(self, csv_path: str = None) -> bool:
        """Importe les modpacks depuis le fichier CSV"""
        csv_file = Path(csv_path or MODPACKS_CSV_PATH)
        
        if not csv_file.exists():
            print(f"⚠ CSV file not found: {csv_file}")
            return False
        
        print(f"\n📊 Importing modpacks from CSV: {csv_file}")
        
        try:
            modpacks_data = []
            
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    modpacks_data.append({
                        'name': row['name'],
                        'slug': row['slug'],
                        'downloads': int(row['downloads']) if row['downloads'] else 0,
                        'followers': 0  # CSV n'a pas cette info
                    })
            
            if modpacks_data:
                # Sauvegarder dans la base de données
                self.db.save_modpack_stats("curseforge", modpacks_data)
                print(f"✓ Imported {len(modpacks_data)} modpacks from CSV")
                return True
            else:
                print("⚠ No data found in CSV")
                return False
                
        except Exception as e:
            print(f"✗ Error importing CSV: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def import_modpacks_from_json(self, json_path: str = None) -> bool:
        """Importe les modpacks depuis le fichier JSON"""
        json_file = Path(json_path or MODPACKS_JSON_PATH)
        
        if not json_file.exists():
            print(f"⚠ JSON file not found: {json_file}")
            return False
        
        print(f"\n📊 Importing modpacks from JSON: {json_file}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                modpacks_data = json.load(f)
            
            if modpacks_data:
                # Sauvegarder dans la base de données
                self.db.save_modpack_stats("curseforge", modpacks_data)
                print(f"✓ Imported {len(modpacks_data)} modpacks from JSON")
                return True
            else:
                print("⚠ No data found in JSON")
                return False
                
        except Exception as e:
            print(f"✗ Error importing JSON: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_import(self) -> bool:
        """Vérifie les données importées"""
        print(f"\n🔍 Verifying imported data...")
        
        try:
            # Vérifier les modpacks
            modpacks = self.db.get_all_modpacks_latest("curseforge")
            print(f"✓ Found {len(modpacks)} modpacks in database")
            
            if modpacks:
                total_downloads = sum(m[2] for m in modpacks)
                print(f"  Total downloads: {total_downloads:,}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error verifying data: {e}")
            return False
    
    def run(self) -> int:
        """Exécute l'import complet"""
        print("=" * 60)
        print("  Create Nuclear Stats - Data Import to PostgreSQL")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        
        if not self.connect_database():
            return 1
        
        try:
            # Essayer d'importer depuis CSV d'abord
            csv_ok = self.import_modpacks_from_csv()
            
            # Si le CSV échoue, essayer JSON
            json_ok = False
            if not csv_ok:
                json_ok = self.import_modpacks_from_json()
            
            # Vérifier les données importées
            verify_ok = self.verify_import()
            
            # Résumé
            print("\n" + "=" * 60)
            print("Summary:")
            print(f"  CSV Import:   {'✓' if csv_ok else '✗'}")
            print(f"  JSON Import:  {'✓' if json_ok else '✗'}")
            print(f"  Verification: {'✓' if verify_ok else '✗'}")
            print(f"Completed at: {datetime.now()}")
            print("=" * 60)
            
            return 0 if (csv_ok or json_ok) else 1
            
        except Exception as e:
            print(f"\n✗ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        
        finally:
            if self.db:
                self.db.close()


def main():
    """Point d'entrée principal"""
    importer = DataImporter()
    return importer.run()


if __name__ == "__main__":
    sys.exit(main())
