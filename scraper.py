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
        # Nouvelle URL du site CurseForge
        self.base_url = "https://www.curseforge.com/minecraft/mc-mods/createnuclear/relations/dependents"
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
        """Établit une session avec CurseForge avec retry"""
        if not self.is_available():
            return False
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Headers plus complets pour ressembler à un vrai navigateur
                self.scraper.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"'
                })

                print(f"  Connecting to CurseForge (Attempt {attempt+1}/{max_retries})...")
                # On teste sur la page principale
                response = self.scraper.get(
                    "https://www.curseforge.com/minecraft/mc-mods/createnuclear",
                    timeout=30
                )
                
                if response.status_code == 200:
                    time.sleep(2)
                    return True
                
                print(f"  Failed with status {response.status_code}")
                time.sleep(5)
                
            except Exception as e:
                print(f"  Error establishing session: {e}")
                time.sleep(5)
        
        return False
    
    def _extract_slug_from_url(self, url: str) -> Optional[str]:
        """Extrait le slug depuis une URL"""
        # Supporte /minecraft/modpacks/slug
        match = re.search(r'/minecraft/modpacks/([^/\?]+)', url)
        if match:
            slug = match.group(1)
            return slug
        return None
    
    def _extract_id_from_url(self, url: str) -> Optional[int]:
        """Extrait l'ID depuis une URL"""
        # Sur le nouveau site, l'ID n'est pas toujours dans l'URL
        # On essaie de le trouver s'il est présent
        match = re.search(r'-(\d+)$', url)
        if match:
            return int(match.group(1))
        return None
    
    def _scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape une page spécifique"""
        # Paramètre filter-related-dependents=6 pour les modpacks
        params = {"filter-related-dependents": "6"}
        if page_num > 1:
            params["page"] = str(page_num)
            
        try:
            response = self.scraper.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 404:
                return None  # Fin des pages
            
            # Vérifier Cloudflare
            if 'cloudflare' in response.text.lower() and 'checking your browser' in response.text.lower():
                print(f"  Blocked by Cloudflare on page {page_num}")
                return None
            
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Chercher tous les liens vers des modpacks
            # Sur le nouveau site, les liens sont souvent dans des cartes
            links = soup.find_all('a', href=re.compile(r'/minecraft/modpacks/[^/]+$'))
            
            modpacks = []
            seen_slugs = set()
            
            for link in links:
                href = link.get('href', '')
                # Le nom est souvent dans un h3 ou similaire à l'intérieur du lien, ou le texte du lien lui-même
                name = link.text.strip()
                if not name:
                    # Essayer de trouver un titre à l'intérieur
                    title_elem = link.find(['h3', 'h4', 'span'], class_=re.compile('name|title'))
                    if title_elem:
                        name = title_elem.text.strip()
                
                if not href or not name:
                    continue
                
                slug = self._extract_slug_from_url(href)
                if not slug or slug in seen_slugs:
                    continue
                
                seen_slugs.add(slug)
                
                modpack_data = {
                    'name': name,
                    'slug': slug,
                    'legacy_url': f"https://www.curseforge.com{href}" if href.startswith('/') else href
                }
                
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
