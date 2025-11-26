#!/usr/bin/env python3
"""
Wrapper pour exécuter collect_stats.py en boucle
"""
import time
import sys
from collect_stats import main

if __name__ == "__main__":
    print("Starting stats collector daemon...")
    
    # Attendre 30 secondes au premier démarrage pour laisser PostgreSQL démarrer
    print("Waiting 30 seconds for PostgreSQL to be ready...")
    time.sleep(30)
    
    while True:
        print("\n" + "="*50)
        print("Running stats collection...")
        try:
            main()
        except Exception as e:
            print(f"Error during collection: {e}")
        
        print("Sleeping for 24 hours...")
        time.sleep(86400)  # 24 heures
