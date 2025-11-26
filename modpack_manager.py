"""
Gestionnaire de modpacks CurseForge
"""
import csv
import json
from typing import List, Dict, Optional
from pathlib import Path
from config import MODPACKS_CSV_PATH, MODPACKS_JSON_PATH


class ModpackManager:
    """Gestionnaire pour charger et manipuler les modpacks"""
    
    def __init__(self):
        self.csv_path = Path(MODPACKS_CSV_PATH)
        self.json_path = Path(MODPACKS_JSON_PATH)
        self._modpacks: List[Dict] = []
    
    def load_from_csv(self) -> List[Dict]:
        """Charge les modpacks depuis le CSV"""
        if not self.csv_path.exists():
            return []
        
        try:
            modpacks = []
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    modpacks.append({
                        'id': int(row['id']) if row['id'] else None,
                        'name': row['name'],
                        'slug': row['slug'],
                        'downloads': int(row['downloads']) if row['downloads'] else 0,
                        'link': row['link']
                    })
            
            self._modpacks = modpacks
            return modpacks
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []
    
    def load_from_json(self) -> List[Dict]:
        """Charge les modpacks depuis le JSON (fallback)"""
        if not self.json_path.exists():
            return []
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                modpacks = json.load(f)
            
            self._modpacks = modpacks
            return modpacks
        except Exception as e:
            print(f"Error loading JSON: {e}")
            return []
    
    def load(self) -> List[Dict]:
        """Charge les modpacks (priorité CSV > JSON)"""
        modpacks = self.load_from_csv()
        if not modpacks:
            modpacks = self.load_from_json()
        return modpacks
    
    def save_to_csv(self, modpacks: List[Dict]) -> bool:
        """Sauvegarde les modpacks en CSV"""
        if not modpacks:
            return False
        
        try:
            with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['id', 'name', 'slug', 'downloads', 'link']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                for modpack in modpacks:
                    writer.writerow({
                        'id': modpack.get('id', ''),
                        'name': modpack.get('name', ''),
                        'slug': modpack.get('slug', ''),
                        'downloads': modpack.get('downloads', 0),
                        'link': modpack.get('link', '')
                    })
            
            self._modpacks = modpacks
            return True
        except Exception as e:
            print(f"Error saving CSV: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Calcule les statistiques des modpacks"""
        if not self._modpacks:
            self.load()
        
        total = len(self._modpacks)
        with_downloads = sum(1 for m in self._modpacks if m.get('downloads', 0) > 0)
        total_downloads = sum(m.get('downloads', 0) for m in self._modpacks)
        with_ids = sum(1 for m in self._modpacks if m.get('id'))
        
        return {
            'total': total,
            'with_downloads': with_downloads,
            'total_downloads': total_downloads,
            'with_ids': with_ids
        }
    
    def get_modpacks(self) -> List[Dict]:
        """Retourne la liste des modpacks"""
        if not self._modpacks:
            self.load()
        return self._modpacks
    
    def sort_by_downloads(self, reverse: bool = True) -> List[Dict]:
        """Trie par nombre de téléchargements"""
        if not self._modpacks:
            self.load()
        return sorted(self._modpacks, key=lambda x: x.get('downloads', 0), reverse=reverse)
    
    def filter_by_name(self, query: str) -> List[Dict]:
        """Filtre par nom"""
        if not self._modpacks:
            self.load()
        query_lower = query.lower()
        return [m for m in self._modpacks if query_lower in m.get('name', '').lower()]
