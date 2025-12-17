#!/usr/bin/env python3
"""
Wrapper pour exécuter collect_stats.py en boucle
"""
import sys
import time
import os
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.collectors.collect_stats import main

if __name__ == "__main__":
    print("Starting stats collector daemon...")
    
    # Attendre 30 secondes au premier démarrage pour laisser PostgreSQL démarrer
    print("Waiting 30 seconds for PostgreSQL to be ready...")
    time.sleep(30)
    
    # Récupérer l'intervalle de collecte depuis les variables d'environnement
    interval = int(os.getenv('COLLECTION_INTERVAL', '21600'))  # 6 heures par défaut
    
    while True:
        print("\n" + "="*50)
        print("Running stats collection...")
        try:
            main()
        except Exception as e:
            print(f"Error during collection: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"Sleeping for {interval} seconds ({interval/3600:.1f} hours)...")
        time.sleep(interval)
