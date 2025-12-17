#!/bin/bash
# Script pour importer les données CSV/JSON vers PostgreSQL

echo "=========================================="
echo "  Import Data to PostgreSQL"
echo "=========================================="

# Vérifier que Docker Compose est en cours d'exécution
if ! docker-compose ps | grep -q "Up"; then
    echo "⚠️  Docker Compose n'est pas en cours d'exécution"
    echo "Démarrage des conteneurs..."
    docker-compose up -d
    echo "Attente de 10 secondes pour PostgreSQL..."
    sleep 10
fi

echo ""
echo "📊 Importation des données..."
docker-compose exec -T streamlit-app python scripts/import_to_postgres.py

echo ""
echo "🔍 Vérification de la base de données..."
docker-compose exec -T streamlit-app python scripts/init_db.py

echo ""
echo "=========================================="
echo "✅ Import terminé !"
echo "=========================================="
