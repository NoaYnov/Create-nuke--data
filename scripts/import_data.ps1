# Script PowerShell pour importer les données CSV/JSON vers PostgreSQL

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Import Data to PostgreSQL" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Vérifier que Docker Compose est en cours d'exécution
$running = docker-compose ps | Select-String "Up"
if (-not $running) {
    Write-Host "⚠️  Docker Compose n'est pas en cours d'exécution" -ForegroundColor Yellow
    Write-Host "Démarrage des conteneurs..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "Attente de 10 secondes pour PostgreSQL..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

Write-Host ""
Write-Host "📊 Importation des données..." -ForegroundColor Green
docker-compose exec -T streamlit-app python scripts/import_to_postgres.py

Write-Host ""
Write-Host "🔍 Vérification de la base de données..." -ForegroundColor Green
docker-compose exec -T streamlit-app python scripts/init_db.py

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Import terminé !" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
