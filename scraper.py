"""
Scraper pour CurseForge Legacy
"""
import re
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from config import MAX_PAGES, PAGE_DELAY, CLOUDFLARE_DELAY


class CurseForgeScraper:
    """Scraper pour la page CurseForge Legacy des dépendances"""
    
    def __init__(self):
        self.base_url = "https://legacy.curseforge.com/minecraft/mc-mods/createnuclear/relations/dependents"
        self.scraper = None
        self._init_scraper()
    
    def _init_scraper(self):
        """Initialise cloudscraper"""
        try:
            import cloudscraper
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                },
                delay=CLOUDFLARE_DELAY,
                interpreter='native'
            )
        except ImportError:
            print("Warning: cloudscraper not available")
            self.scraper = None
    
    def is_available(self) -> bool:
        """Vérifie si le scraper est disponible"""
        return self.scraper is not None
    
    def _establish_session(self) -> bool:
        """Établit une session avec CurseForge"""
        if not self.is_available():
            return False
        
        try:
            response = self.scraper.get(
                "https://legacy.curseforge.com/minecraft/mc-mods/createnuclear",
                timeout=30
            )
            time.sleep(2)
            return response.status_code == 200
        except Exception as e:
            print(f"Error establishing session: {e}")
            return False
    
    def _extract_slug_from_url(self, url: str) -> Optional[str]:
        """Extrait le slug depuis une URL"""
        match = re.search(r'/modpacks/([^/\?]+)', url)
        if match:
            slug = match.group(1)
            # Retirer l'ID à la fin si présent
            id_match = re.search(r'-(\d+)$', slug)
            if id_match:
                return slug.rsplit('-', 1)[0]
            return slug
        return None
    
    def _extract_id_from_url(self, url: str) -> Optional[int]:
        """Extrait l'ID depuis une URL"""
        match = re.search(r'/modpacks/[^/]*-(\d+)', url)
        if match:
            return int(match.group(1))
        return None
    
    def _scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape une page spécifique"""
        page_url = f"{self.base_url}?page={page_num}" if page_num > 1 else self.base_url
        
        try:
            response = self.scraper.get(page_url, timeout=30)
            
            if response.status_code == 404:
                return None  # Fin des pages
            
            # Vérifier Cloudflare
            if 'cloudflare' in response.text.lower() and 'checking your browser' in response.text.lower():
                print(f"  Blocked by Cloudflare on page {page_num}")
                return None
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Chercher tous les liens vers des modpacks
            links = soup.find_all('a', href=re.compile(r'/minecraft/modpacks/[^/]+'))
            
            modpacks = []
            seen_slugs = set()
            
            for link in links:
                href = link.get('href', '')
                name = link.text.strip()
                
                if not href or not name:
                    continue
                
                slug = self._extract_slug_from_url(href)
                if not slug or slug in seen_slugs:
                    continue
                
                seen_slugs.add(slug)
                
                modpack_data = {
                    'name': name,
                    'slug': slug,
                    'legacy_url': f"https://legacy.curseforge.com{href}" if href.startswith('/') else href
                }
                
                mod_id = self._extract_id_from_url(href)
                if mod_id:
                    modpack_data['id'] = mod_id
                
                modpacks.append(modpack_data)
            
            return modpacks
            
        except Exception as e:
            print(f"  Error on page {page_num}: {e}")
            return []
    
    def scrape_all(self) -> List[Dict]:
        """Scrape toutes les pages"""
        if not self.is_available():
            print("Scraper not available")
            return []
        
        if not self._establish_session():
            print("Failed to establish session")
            return []
        
        all_modpacks = []
        seen_slugs = set()
        
        print(f"Scraping up to {MAX_PAGES} pages...")
        
        for page_num in range(1, MAX_PAGES + 1):
            print(f"  Page {page_num}...", end=" ")
            
            modpacks = self._scrape_page(page_num)
            
            if modpacks is None:
                print("End of pages")
                break
            
            if not modpacks:
                if page_num == 1:
                    print("Failed")
                    break
                print("Empty, stopping")
                break
            
            # Dédupliquer
            new_count = 0
            for modpack in modpacks:
                if modpack['slug'] not in seen_slugs:
                    seen_slugs.add(modpack['slug'])
                    all_modpacks.append(modpack)
                    new_count += 1
            
            print(f"{new_count} new (Total: {len(all_modpacks)})")
            
            # Délai entre les pages
            if page_num < MAX_PAGES:
                time.sleep(PAGE_DELAY)
        
        return all_modpacks
