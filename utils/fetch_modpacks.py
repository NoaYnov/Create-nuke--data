"""
Script pour récupérer tous les modpacks qui incluent Create Nuclear
Utilise le scraping pour obtenir les slugs, puis l'API CurseForge pour les détails (ID, downloads)
"""
import cloudscraper
import requests
import csv
import time
import re
from bs4 import BeautifulSoup
import os

# Configuration
CURSEFORGE_API_KEY = os.getenv('CURSEFORGE_API_KEY', '')
CURSEFORGE_API_BASE = "https://api.curseforge.com"
BASE_URL = "https://legacy.curseforge.com/minecraft/mc-mods/createnuclear/relations/dependents"
OUTPUT_FILE = "curseforge_modpacks.csv"

def extract_modpack_id_from_url(url):
    """Extrait l'ID du modpack depuis différents formats d'URL"""
    # Format: /minecraft/modpacks/name-123456
    # ou: https://www.curseforge.com/minecraft/modpacks/name
    match = re.search(r'/modpacks/([^/\?]+)', url)
    if match:
        slug = match.group(1)
        # Si le slug contient un ID à la fin
        id_match = re.search(r'-(\d+)$', slug)
        if id_match:
            return int(id_match.group(1)), slug.rsplit('-', 1)[0]
        return None, slug
    return None, None

def scrape_modpack_ids():
    """Scrape les IDs et slugs des modpacks depuis CurseForge Legacy"""
    print("🔍 Démarrage du scraping des modpacks...")
    
    try:
        # Créer le scraper cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            },
            delay=10,
            interpreter='native'
        )
        
        print("✓ Scraper initialisé")
        
        # Établir la session
        print("📡 Connexion à CurseForge Legacy...")
        initial_response = scraper.get(
            "https://legacy.curseforge.com/minecraft/mc-mods/createnuclear",
            timeout=30
        )
        print(f"✓ Session établie (Status: {initial_response.status_code})")
        time.sleep(2)
        
        all_modpacks = []
        seen_slugs = set()
        
        # Parcourir les pages
        for page_num in range(1, 35):
            page_url = f"{BASE_URL}?page={page_num}" if page_num > 1 else BASE_URL
            
            print(f"\n📄 Page {page_num}...")
            
            try:
                response = scraper.get(page_url, timeout=30)
                
                if response.status_code == 404:
                    print(f"  ⚠️  404 - Fin des pages")
                    break
                
                # Vérifier Cloudflare
                if 'cloudflare' in response.text.lower() and 'checking your browser' in response.text.lower():
                    print(f"  ❌ Bloqué par Cloudflare")
                    break
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Chercher tous les liens vers des modpacks
                links = soup.find_all('a', href=re.compile(r'/minecraft/modpacks/[^/]+'))
                
                page_count = 0
                for link in links:
                    href = link.get('href', '')
                    name = link.text.strip()
                    
                    if not href or not name:
                        continue
                    
                    # Extraire ID et slug
                    mod_id, slug = extract_modpack_id_from_url(href)
                    
                    if not slug:
                        continue
                    
                    # Éviter les doublons
                    if slug in seen_slugs:
                        continue
                    
                    seen_slugs.add(slug)
                    
                    modpack_data = {
                        'name': name,
                        'slug': slug,
                        'legacy_url': f"https://legacy.curseforge.com{href}" if href.startswith('/') else href
                    }
                    
                    if mod_id:
                        modpack_data['id'] = mod_id
                    
                    all_modpacks.append(modpack_data)
                    page_count += 1
                
                print(f"  ✓ {page_count} modpacks trouvés (Total: {len(all_modpacks)})")
                
                # Si aucun modpack trouvé après la page 1, arrêter
                if page_count == 0 and page_num > 1:
                    print(f"  ⚠️  Aucun modpack sur cette page, arrêt")
                    break
                
                # Délai entre les pages
                if page_num < 34:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"  ❌ Erreur: {e}")
                if page_num == 1:
                    raise
                break
        
        print(f"\n✅ Scraping terminé: {len(all_modpacks)} modpacks uniques trouvés")
        return all_modpacks
        
    except Exception as e:
        print(f"\n❌ Erreur de scraping: {e}")
        return []

def search_modpack_on_curseforge(slug):
    """Recherche un modpack par son slug sur l'API CurseForge"""
    if not CURSEFORGE_API_KEY:
        return None
    
    url = f"{CURSEFORGE_API_BASE}/v1/mods/search"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    params = {
        "gameId": 432,  # Minecraft
        "classId": 4471,  # Modpacks
        "slug": slug,
        "pageSize": 1
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
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
        print(f"    ⚠️  Erreur API pour {slug}: {e}")
    
    return None

def get_modpack_by_id(mod_id):
    """Récupère les détails d'un modpack par son ID"""
    if not CURSEFORGE_API_KEY:
        return None
    
    url = f"{CURSEFORGE_API_BASE}/v1/mods/{mod_id}"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
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
        print(f"    ⚠️  Erreur API pour ID {mod_id}: {e}")
    
    return None

def enrich_modpacks_with_api(modpacks):
    """Enrichit les données des modpacks avec l'API CurseForge"""
    if not CURSEFORGE_API_KEY:
        print("\n⚠️  Pas de clé API CurseForge, impossible d'obtenir les IDs et downloads")
        return []
    
    print(f"\n🔄 Enrichissement avec l'API CurseForge ({len(modpacks)} modpacks)...")
    
    enriched = []
    
    for i, modpack in enumerate(modpacks, 1):
        print(f"  [{i}/{len(modpacks)}] {modpack['name']}...", end=" ")
        
        # Si on a un ID, utiliser l'API directe
        if 'id' in modpack and modpack['id']:
            api_data = get_modpack_by_id(modpack['id'])
            if api_data:
                enriched.append(api_data)
                print("✓")
            else:
                # Essayer par slug en fallback
                api_data = search_modpack_on_curseforge(modpack['slug'])
                if api_data:
                    enriched.append(api_data)
                    print("✓ (via slug)")
                else:
                    print("✗")
        else:
            # Chercher par slug
            api_data = search_modpack_on_curseforge(modpack['slug'])
            
            if api_data:
                enriched.append(api_data)
                print("✓")
            else:
                print("✗")
        
        # Délai pour ne pas surcharger l'API
        if i % 10 == 0:
            time.sleep(1)
    
    return enriched

def save_modpacks_csv(modpacks, filename):
    """Sauvegarde les modpacks dans un fichier CSV"""
    if not modpacks:
        print("\n⚠️  Aucun modpack à sauvegarder")
        return
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
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
    
    print(f"\n💾 Données sauvegardées dans {filename}")
    print(f"   Format: CSV avec colonnes [id, name, slug, downloads, link]")

def main():
    print("=" * 60)
    print("  Récupération des modpacks incluant Create Nuclear")
    print("=" * 60)
    
    if not CURSEFORGE_API_KEY:
        print("\n❌ CURSEFORGE_API_KEY non définie!")
        print("   Impossible de récupérer les IDs et downloads sans clé API")
        print("   Définissez la variable d'environnement CURSEFORGE_API_KEY")
        return
    
    # Étape 1: Scraper les slugs
    modpacks = scrape_modpack_ids()
    
    if not modpacks:
        print("\n❌ Aucun modpack trouvé par scraping")
        return
    
    # Étape 2: Enrichir avec l'API (obligatoire pour ID et downloads)
    enriched_modpacks = enrich_modpacks_with_api(modpacks)
    
    if not enriched_modpacks:
        print("\n❌ Impossible d'enrichir les données avec l'API")
        return
    
    # Étape 3: Sauvegarder en CSV
    save_modpacks_csv(enriched_modpacks, OUTPUT_FILE)
    
    # Statistiques
    print("\n" + "=" * 60)
    print(f"✅ TERMINÉ!")
    print(f"   Total: {len(enriched_modpacks)} modpacks avec données complètes")
    print(f"   IDs récupérés: {len([m for m in enriched_modpacks if m.get('id')])}")
    total_downloads = sum(m.get('downloads', 0) for m in enriched_modpacks)
    print(f"   Téléchargements totaux: {total_downloads:,}")
    print(f"   Fichier: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
