"""
Clients API pour Modrinth et CurseForge
"""
import requests
from typing import Optional, List, Dict, Any
from config import (
    MODRINTH_API_BASE, 
    MODRINTH_PROJECT_SLUG,
    CURSEFORGE_API_BASE,
    CURSEFORGE_MOD_ID,
    CURSEFORGE_API_KEY,
    USER_AGENT
)


class ModrinthClient:
    """Client pour l'API Modrinth"""
    
    def __init__(self):
        self.base_url = MODRINTH_API_BASE
        self.project_slug = MODRINTH_PROJECT_SLUG
        self.headers = {"User-Agent": USER_AGENT}
    
    def get_project_info(self) -> Optional[Dict[str, Any]]:
        """Récupère les informations du projet"""
        try:
            url = f"{self.base_url}/project/{self.project_slug}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Modrinth project: {e}")
            return None
    
    def get_versions(self) -> Optional[List[Dict[str, Any]]]:
        """Récupère toutes les versions"""
        try:
            url = f"{self.base_url}/project/{self.project_slug}/version"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching Modrinth versions: {e}")
            return None
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Récupère les statistiques complètes"""
        project = self.get_project_info()
        versions = self.get_versions()
        
        if not project or not versions:
            return None
        
        total_downloads = sum(v['downloads'] for v in versions)
        
        return {
            'project': project,
            'versions': versions,
            'total_downloads': total_downloads,
            'followers': project['followers'],
            'versions_count': len(versions)
        }


class CurseForgeClient:
    """Client pour l'API CurseForge"""
    
    def __init__(self):
        self.base_url = CURSEFORGE_API_BASE
        self.mod_id = CURSEFORGE_MOD_ID
        self.api_key = CURSEFORGE_API_KEY
        self.headers = {"x-api-key": self.api_key} if self.api_key else {}
    
    def is_available(self) -> bool:
        """Vérifie si l'API est disponible"""
        return bool(self.api_key)
    
    def get_mod_info(self) -> Optional[Dict[str, Any]]:
        """Récupère les informations du mod"""
        if not self.is_available():
            return None
        
        try:
            url = f"{self.base_url}/v1/mods/{self.mod_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"Error fetching CurseForge mod: {e}")
            return None
    
    def get_files(self) -> Optional[List[Dict[str, Any]]]:
        """Récupère tous les fichiers/versions"""
        if not self.is_available():
            return None
        
        try:
            url = f"{self.base_url}/v1/mods/{self.mod_id}/files"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()['data']
        except Exception as e:
            print(f"Error fetching CurseForge files: {e}")
            return None
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Récupère les statistiques complètes"""
        mod_info = self.get_mod_info()
        files = self.get_files()
        
        if not mod_info or not files:
            return None
        
        total_downloads = sum(f['downloadCount'] for f in files)
        
        return {
            'mod': mod_info,
            'files': files,
            'total_downloads': total_downloads,
            'followers': mod_info.get('thumbsUpCount', 0),
            'versions_count': len(files)
        }
    
    def search_modpack(self, slug: str) -> Optional[Dict[str, Any]]:
        """Recherche un modpack par slug"""
        if not self.is_available():
            return None
        
        try:
            url = f"{self.base_url}/v1/mods/search"
            params = {
                "gameId": 432,
                "classId": 4471,
                "slug": slug,
                "pageSize": 1
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                mod = data['data'][0]
                return {
                    'id': mod['id'],
                    'name': mod['name'],
                    'slug': mod['slug'],
                    'downloads': mod['downloadCount'],
                    'link': mod['links']['websiteUrl']
                }
        except Exception as e:
            print(f"Error searching modpack {slug}: {e}")
        
        return None
    
    def get_modpack_by_id(self, mod_id: int) -> Optional[Dict[str, Any]]:
        """Récupère un modpack par ID"""
        if not self.is_available():
            return None
        
        try:
            url = f"{self.base_url}/v1/mods/{mod_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            mod = response.json()['data']
            
            return {
                'id': mod['id'],
                'name': mod['name'],
                'slug': mod['slug'],
                'downloads': mod['downloadCount'],
                'link': mod['links']['websiteUrl']
            }
        except Exception as e:
            print(f"Error fetching modpack {mod_id}: {e}")
        
        return None
