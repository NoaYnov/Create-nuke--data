"""
Script pour convertir JSON en CSV et enrichir avec l'API CurseForge
"""
import csv
import json
import os
import requests
import time

CURSEFORGE_API_KEY = os.getenv('CURSEFORGE_API_KEY', '')
CURSEFORGE_API_BASE = "https://api.curseforge.com"

def get_modpack_by_slug(slug):
    """Récupère les détails d'un modpack par son slug via l'API"""
    if not CURSEFORGE_API_KEY:
        return None
    
    url = f"{CURSEFORGE_API_BASE}/v1/mods/search"
    headers = {"x-api-key": CURSEFORGE_API_KEY}
    params = {
        "gameId": 432,
        "classId": 4471,
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
        print(f"  Error for {slug}: {e}")
    
    return None

def main():
    print("=" * 60)
    print("Converting JSON to CSV with API enrichment")
    print("=" * 60)
    
    if not CURSEFORGE_API_KEY:
        print("\nERROR: CURSEFORGE_API_KEY not set!")
        return
    
    # Charger le JSON
    json_path = 'curseforge_modpacks.json'
    if not os.path.exists(json_path):
        print(f"\nERROR: {json_path} not found!")
        return
    
    print(f"\nLoading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        modpacks = json.load(f)
    
    print(f"Found {len(modpacks)} modpacks")
    
    # Enrichir avec l'API
    print("\nEnriching with CurseForge API...")
    enriched = []
    
    for i, modpack in enumerate(modpacks, 1):
        slug = modpack.get('slug', '')
        print(f"[{i}/{len(modpacks)}] {modpack.get('name', 'Unknown')}...", end=" ")
        
        api_data = get_modpack_by_slug(slug)
        if api_data:
            enriched.append(api_data)
            print(f"OK (ID: {api_data['id']}, Downloads: {api_data['downloads']:,})")
        else:
            print("SKIP")
        
        # Delai toutes les 10 requetes
        if i % 10 == 0:
            time.sleep(1)
    
    # Sauvegarder en CSV
    csv_path = 'curseforge_modpacks.csv'
    print(f"\nSaving to {csv_path}...")
    
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['id', 'name', 'slug', 'downloads', 'link']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for modpack in enriched:
            writer.writerow(modpack)
    
    # Stats
    total_downloads = sum(m['downloads'] for m in enriched)
    print("\n" + "=" * 60)
    print(f"SUCCESS!")
    print(f"  Total modpacks: {len(enriched)}")
    print(f"  Total downloads: {total_downloads:,}")
    print(f"  File: {csv_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
