#!/usr/bin/env python3
"""
Script de collecte quotidienne des statistiques
Utilise les classes modulaires pour une meilleure organisation
"""
import sys
import time
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from database import StatsDatabase
from api_clients import ModrinthClient, CurseForgeClient
from scraper import CurseForgeScraper
from modpack_manager import ModpackManager
from config import DATABASE_URL, API_DELAY, BATCH_SIZE


class StatsCollector:
    """Collecteur principal de statistiques"""
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or DATABASE_URL
        self.db = None
        self.modrinth = ModrinthClient()
        self.curseforge = CurseForgeClient()
        self.scraper = CurseForgeScraper()
        self.modpack_manager = ModpackManager()
    
    def connect_database(self) -> bool:
        """Connexion à la base de données"""
        try:
            self.db = StatsDatabase(self.db_url)
            print("✓ Connected to database")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def collect_modrinth_stats(self) -> bool:
        """Collecte les stats Modrinth"""
        print(f"[{datetime.now()}] Collecting Modrinth stats...")
        
        try:
            stats = self.modrinth.get_stats()
            if not stats:
                print("✗ Failed to fetch Modrinth stats")
                return False
            
            # Sauvegarder les stats quotidiennes
            self.db.save_daily_stats(
                platform="modrinth",
                total_downloads=stats['total_downloads'],
                followers=stats['followers'],
                versions_count=stats['versions_count']
            )
            
            # Sauvegarder les stats par version
            versions_data = [{
                'name': v['name'],
                'version_number': v['version_number'],
                'downloads': v['downloads'],
                'date_published': v['date_published'],
                'game_versions': v['game_versions']
            } for v in stats['versions']]
            
            self.db.save_version_stats("modrinth", versions_data)
            
            print(f"✓ Modrinth: {stats['total_downloads']:,} downloads, {stats['versions_count']} versions")
            return True
            
        except Exception as e:
            print(f"✗ Error collecting Modrinth stats: {e}")
            return False
    
    def collect_curseforge_stats(self) -> bool:
        """Collecte les stats CurseForge"""
        print(f"[{datetime.now()}] Collecting CurseForge stats...")
        
        if not self.curseforge.is_available():
            print("⚠ CurseForge API key not set")
            return False
        
        try:
            stats = self.curseforge.get_stats()
            if not stats:
                print("✗ Failed to fetch CurseForge stats")
                return False
            
            # Sauvegarder les stats quotidiennes
            self.db.save_daily_stats(
                platform="curseforge",
                total_downloads=stats['total_downloads'],
                followers=stats['followers'],
                versions_count=stats['versions_count']
            )
            
            # Sauvegarder les stats par version
            versions_data = [{
                'name': f['displayName'],
                'version_number': f['fileName'],
                'downloads': f['downloadCount'],
                'date_published': f['fileDate'],
                'game_versions': f.get('gameVersions', [])
            } for f in stats['files']]
            
            self.db.save_version_stats("curseforge", versions_data)
            
            print(f"✓ CurseForge: {stats['total_downloads']:,} downloads, {stats['versions_count']} files")
            return True
            
        except Exception as e:
            print(f"✗ Error collecting CurseForge stats: {e}")
            return False
    
    def update_modpacks(self) -> bool:
        """Met à jour la liste des modpacks"""
        print(f"[{datetime.now()}] Updating modpacks list...")
        
        if not self.curseforge.is_available():
            print("⚠ CurseForge API not available for enrichment")
            return False
            
        try:
            # Liste des modpacks à mettre à jour
            unique_slugs = set()
            modpacks_to_process = []
            
            # 1. Charger les modpacks existants
            existing = self.modpack_manager.load_modpacks()
            for m in existing:
                if m.get('slug'):
                    unique_slugs.add(m['slug'])
                    modpacks_to_process.append({'slug': m['slug'], 'id': m.get('id')})
            
            print(f"  Loaded {len(modpacks_to_process)} existing modpacks")

            # 2. Scraper les nouveaux (si possible)
            if self.scraper.is_available():
                print("  Scraping for new modpacks...")
                scraped = self.scraper.scrape_all()
                if scraped:
                    new_count = 0
                    for m in scraped:
                        if m['slug'] not in unique_slugs:
                            unique_slugs.add(m['slug'])
                            modpacks_to_process.append(m)
                            new_count += 1
                    print(f"  Found {new_count} new modpacks via scraping")
                else:
                    print("  ⚠ Scraping failed or returned no results (skipping)")
            
            if not modpacks_to_process:
                print("✗ No modpacks to update")
                return False
            
            # 3. Enrichir/Mettre à jour avec l'API
            print(f"  Updating stats for {len(modpacks_to_process)} modpacks...")
            enriched = []
            
            for i, modpack in enumerate(modpacks_to_process):
                api_data = None
                
                # Essayer par ID d'abord
                if 'id' in modpack and modpack['id']:
                    api_data = self.curseforge.get_modpack_by_id(modpack['id'])
                
                # Fallback sur slug si pas d'ID ou échec ID
                if not api_data and 'slug' in modpack:
                    api_data = self.curseforge.search_modpack(modpack['slug'])
                
                if api_data:
                    enriched.append(api_data)
                
                # Délai toutes les N requêtes
                if (i + 1) % BATCH_SIZE == 0:
                    time.sleep(API_DELAY)
            
            # 4. Sauvegarder
            if enriched:
                # Sauvegarder en CSV
                success = self.modpack_manager.save_to_csv(enriched)
                
                # Sauvegarder en base de données
                try:
                    self.db.save_modpack_stats("curseforge", enriched)
                    print(f"  ✓ Saved {len(enriched)} modpacks to database")
                except Exception as e:
                    print(f"  ✗ Failed to save modpacks to database: {e}")
                
                if success:
                    stats = self.modpack_manager.get_stats()
                    print(f"✓ Modpacks: {stats['total']} saved, {stats['total_downloads']:,} total downloads")
                    return True
            
            print("✗ No modpacks updated")
            return False
            
        except Exception as e:
            print(f"✗ Error updating modpacks: {e}")
            return False
    
    def run(self) -> int:
        """Exécute la collecte complète"""
        print("=" * 60)
        print("  Create Nuclear Stats Collection")
        print("=" * 60)
        print(f"Started at: {datetime.now()}")
        
        if not self.connect_database():
            return 1
        
        try:
            # Collecter les stats
            modrinth_ok = self.collect_modrinth_stats()
            curseforge_ok = self.collect_curseforge_stats()
            modpacks_ok = self.update_modpacks()
            
            # Résumé
            print("\n" + "=" * 60)
            print("Summary:")
            print(f"  Modrinth:   {'✓' if modrinth_ok else '✗'}")
            print(f"  CurseForge: {'✓' if curseforge_ok else '✗'}")
            print(f"  Modpacks:   {'✓' if modpacks_ok else '✗'}")
            print(f"Completed at: {datetime.now()}")
            print("=" * 60)
            
            return 0 if (modrinth_ok or curseforge_ok) else 1
            
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
    collector = StatsCollector()
    return collector.run()


if __name__ == "__main__":
    sys.exit(main())
