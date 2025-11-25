import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

# Configuration
PROJECT_SLUG = "createnuclear"
API_BASE = "https://api.modrinth.com/v2"
USER_AGENT = "CreateNuclear-Stats/1.0"

def get_project_info():
    """Récupère les informations générales du projet"""
    url = f"{API_BASE}/project/{PROJECT_SLUG}"
    headers = {"User-Agent": USER_AGENT}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_project_versions():
    """Récupère toutes les versions du projet"""
    url = f"{API_BASE}/project/{PROJECT_SLUG}/version"
    headers = {"User-Agent": USER_AGENT}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def search_modpacks_with_dependency():
    """Recherche les modpacks qui incluent ce mod comme dépendance"""
    url = f"{API_BASE}/search"
    headers = {"User-Agent": USER_AGENT}
    params = {
        "facets": f'[["project_type:modpack"]]',
        "limit": 100
    }
    
    modpacks_with_mod = []
    offset = 0
    
    # Récupérer d'abord l'ID du projet
    project_info = get_project_info()
    project_id = project_info['id']
    
    # Chercher les modpacks et vérifier leurs dépendances
    while True:
        params['offset'] = offset
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data['hits']:
            break
            
        for modpack in data['hits']:
            # Vérifier si notre mod est dans les dépendances
            try:
                versions_url = f"{API_BASE}/project/{modpack['project_id']}/version"
                versions_response = requests.get(versions_url, headers=headers)
                if versions_response.status_code == 200:
                    versions = versions_response.json()
                    for version in versions:
                        if 'dependencies' in version:
                            for dep in version['dependencies']:
                                if dep.get('project_id') == project_id:
                                    modpacks_with_mod.append({
                                        'title': modpack['title'],
                                        'slug': modpack['slug'],
                                        'downloads': modpack['downloads'],
                                        'follows': modpack['follows']
                                    })
                                    break
            except:
                pass
        
        offset += len(data['hits'])
        if offset >= data['total_hits']:
            break
    
    return modpacks_with_mod

def analyze_downloads_by_version(versions):
    """Analyse les téléchargements par version"""
    version_stats = []
    
    for version in versions:
        version_stats.append({
            'name': version['name'],
            'version_number': version['version_number'],
            'downloads': version['downloads'],
            'date_published': version['date_published'],
            'game_versions': version['game_versions']
        })
    
    # Trier par date de publication
    version_stats.sort(key=lambda x: x['date_published'])
    return version_stats

def plot_downloads_timeline(version_stats):
    """Crée un graphique de l'évolution des téléchargements"""
    dates = [datetime.fromisoformat(v['date_published'].replace('Z', '+00:00')) for v in version_stats]
    downloads = [v['downloads'] for v in version_stats]
    
    plt.figure(figsize=(14, 6))
    plt.plot(dates, downloads, marker='o', linestyle='-', linewidth=2)
    plt.title('Évolution des téléchargements par version', fontsize=16, fontweight='bold')
    plt.xlabel('Date de publication', fontsize=12)
    plt.ylabel('Téléchargements', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('downloads_timeline.png', dpi=300)
    print("✅ Graphique sauvegardé: downloads_timeline.png")

def plot_downloads_by_minecraft_version(version_stats):
    """Crée un graphique des téléchargements par version de Minecraft"""
    mc_version_downloads = defaultdict(int)
    
    for version in version_stats:
        for mc_version in version['game_versions']:
            mc_version_downloads[mc_version] += version['downloads']
    
    # Trier par nombre de téléchargements
    sorted_versions = sorted(mc_version_downloads.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_versions:
        mc_versions = [v[0] for v in sorted_versions[:15]]  # Top 15
        downloads = [v[1] for v in sorted_versions[:15]]
        
        plt.figure(figsize=(12, 6))
        plt.barh(mc_versions, downloads, color='#1bd96a')
        plt.title('Téléchargements par version de Minecraft (Top 15)', fontsize=16, fontweight='bold')
        plt.xlabel('Téléchargements', fontsize=12)
        plt.ylabel('Version Minecraft', fontsize=12)
        plt.tight_layout()
        plt.savefig('downloads_by_mc_version.png', dpi=300)
        print("✅ Graphique sauvegardé: downloads_by_mc_version.png")

def print_project_summary(project_info):
    """Affiche un résumé du projet"""
    print("\n" + "="*60)
    print(f"📊 STATISTIQUES - {project_info['title']}")
    print("="*60)
    print(f"\n📝 Description: {project_info['description']}")
    print(f"\n📦 Total téléchargements: {project_info['downloads']:,}")
    print(f"⭐ Followers: {project_info['followers']:,}")
    print(f"🔗 Slug: {project_info['slug']}")
    print(f"📅 Date de création: {project_info['published'][:10]}")
    print(f"🔄 Dernière mise à jour: {project_info['updated'][:10]}")
    print(f"📁 Statut: {project_info['status']}")

def print_version_details(version_stats):
    """Affiche les détails des versions"""
    print("\n" + "-"*60)
    print("📋 DÉTAILS PAR VERSION")
    print("-"*60)
    
    total_downloads = sum(v['downloads'] for v in version_stats)
    
    for i, version in enumerate(reversed(version_stats), 1):
        percentage = (version['downloads'] / total_downloads * 100) if total_downloads > 0 else 0
        print(f"\n{i}. {version['name']} (v{version['version_number']})")
        print(f"   📥 Téléchargements: {version['downloads']:,} ({percentage:.1f}%)")
        print(f"   📅 Date: {version['date_published'][:10]}")
        print(f"   🎮 Versions MC: {', '.join(version['game_versions'][:5])}")

def print_modpack_info(modpacks):
    """Affiche les informations sur les modpacks"""
    print("\n" + "-"*60)
    print(f"📦 MODPACKS INCLUANT CREATE NUCLEAR ({len(modpacks)} trouvés)")
    print("-"*60)
    
    if not modpacks:
        print("\n⚠️  Aucun modpack trouvé ou recherche limitée.")
        print("   Note: La recherche peut être incomplète selon les dépendances.")
    else:
        # Dédupliquer les modpacks
        unique_modpacks = {mp['slug']: mp for mp in modpacks}.values()
        sorted_modpacks = sorted(unique_modpacks, key=lambda x: x['downloads'], reverse=True)
        
        for i, modpack in enumerate(sorted_modpacks[:20], 1):  # Top 20
            print(f"\n{i}. {modpack['title']}")
            print(f"   📥 Téléchargements: {modpack['downloads']:,}")
            print(f"   ⭐ Followers: {modpack['follows']:,}")
            print(f"   🔗 https://modrinth.com/modpack/{modpack['slug']}")

def save_stats_to_file(project_info, version_stats, modpacks):
    """Sauvegarde les statistiques dans un fichier JSON"""
    stats = {
        'generated_at': datetime.now().isoformat(),
        'project': {
            'title': project_info['title'],
            'slug': project_info['slug'],
            'total_downloads': project_info['downloads'],
            'followers': project_info['followers'],
            'published': project_info['published'],
            'updated': project_info['updated']
        },
        'versions': version_stats,
        'modpacks': [dict(mp) for mp in {mp['slug']: mp for mp in modpacks}.values()]
    }
    
    with open('createnuclear_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Statistiques sauvegardées dans: createnuclear_stats.json")

def main():
    print("🚀 Récupération des statistiques Create Nuclear...\n")
    
    try:
        # 1. Récupérer les informations du projet
        print("📡 Récupération des informations du projet...")
        project_info = get_project_info()
        
        # 2. Récupérer les versions
        print("📡 Récupération des versions...")
        versions = get_project_versions()
        version_stats = analyze_downloads_by_version(versions)
        
        # 3. Rechercher les modpacks
        print("📡 Recherche des modpacks incluant Create Nuclear...")
        print("   (Cela peut prendre quelques minutes...)")
        modpacks = search_modpacks_with_dependency()
        
        # 4. Afficher les résumés
        print_project_summary(project_info)
        print_version_details(version_stats)
        print_modpack_info(modpacks)
        
        # 5. Créer les graphiques
        print("\n📊 Génération des graphiques...")
        plot_downloads_timeline(version_stats)
        plot_downloads_by_minecraft_version(version_stats)
        
        # 6. Sauvegarder les statistiques
        save_stats_to_file(project_info, version_stats, modpacks)
        
        print("\n" + "="*60)
        print("✨ Analyse terminée avec succès!")
        print("="*60)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête API: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
