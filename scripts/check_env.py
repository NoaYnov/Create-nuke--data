#!/usr/bin/env python3
"""
Script de vérification de l'environnement
Vérifie que tout est correctement configuré avant le déploiement
"""
import sys
import os
from pathlib import Path
import subprocess


class Colors:
    """Couleurs pour le terminal"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Afficher un en-tête"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text):
    """Afficher un succès"""
    print(f"{Colors.GREEN}[OK]{Colors.END} {text}")


def print_warning(text):
    """Afficher un avertissement"""
    print(f"{Colors.YELLOW}[!]{Colors.END} {text}")


def print_error(text):
    """Afficher une erreur"""
    print(f"{Colors.RED}[X]{Colors.END} {text}")


def print_info(text):
    """Afficher une info"""
    print(f"{Colors.BLUE}[i]{Colors.END} {text}")


def check_command(command, name):
    """Vérifier qu'une commande existe"""
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_success(f"{name} installé: {version}")
            return True
        else:
            print_error(f"{name} non trouvé")
            return False
    except FileNotFoundError:
        print_error(f"{name} non installé")
        return False


def check_file(filepath, name, required=True):
    """Vérifier qu'un fichier existe"""
    if filepath.exists():
        size = filepath.stat().st_size
        print_success(f"{name} trouvé ({size} bytes)")
        return True
    else:
        if required:
            print_error(f"{name} manquant: {filepath}")
        else:
            print_warning(f"{name} manquant (optionnel): {filepath}")
        return not required


def check_env_var(var_name, required=True):
    """Vérifier qu'une variable d'environnement existe"""
    value = os.getenv(var_name)
    if value:
        # Masquer les valeurs sensibles
        if any(secret in var_name.lower() for secret in ['password', 'key', 'secret']):
            display_value = '*' * 8
        else:
            display_value = value[:50] + '...' if len(value) > 50 else value
        print_success(f"{var_name} = {display_value}")
        return True
    else:
        if required:
            print_error(f"{var_name} non définie")
        else:
            print_warning(f"{var_name} non définie (optionnel)")
        return not required


def check_docker_running():
    """Vérifier que Docker est en cours d'exécution"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print_success("Docker daemon en cours d'exécution")
            return True
        else:
            print_error("Docker daemon non accessible")
            return False
    except FileNotFoundError:
        print_error("Docker non installé")
        return False


def check_docker_compose_services():
    """Vérifier l'état des services Docker Compose"""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--services"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            services = result.stdout.strip().split('\n')
            if services and services[0]:
                print_info(f"Services définis: {', '.join(services)}")
                
                # Vérifier l'état de chaque service
                result = subprocess.run(
                    ["docker-compose", "ps"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if "Up" in result.stdout:
                    print_success("Services Docker Compose en cours d'exécution")
                    return True
                else:
                    print_warning("Services Docker Compose définis mais non démarrés")
                    return True
            else:
                print_warning("Aucun service Docker Compose trouvé")
                return True
        else:
            print_warning("Impossible de vérifier les services Docker Compose")
            return True
    except FileNotFoundError:
        print_error("docker-compose non installé")
        return False


def main():
    """Fonction principale"""
    print_header("Create Nuclear Stats - Environment Check")
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    all_ok = True
    
    # 1. Vérifier les commandes requises
    print_header("1. Commandes Requises")
    all_ok &= check_command("docker", "Docker")
    all_ok &= check_command("docker-compose", "Docker Compose")
    all_ok &= check_command("python", "Python")
    
    # 2. Vérifier Docker
    print_header("2. Docker")
    all_ok &= check_docker_running()
    check_docker_compose_services()  # Non bloquant
    
    # 3. Vérifier les fichiers de configuration
    print_header("3. Fichiers de Configuration")
    all_ok &= check_file(project_root / "docker-compose.yml", "docker-compose.yml")
    all_ok &= check_file(project_root / "Dockerfile", "Dockerfile")
    all_ok &= check_file(project_root / "requirements.txt", "requirements.txt")
    check_file(project_root / ".env", ".env", required=True)
    check_file(project_root / ".env.example", ".env.example", required=False)
    
    # 4. Vérifier les scripts
    print_header("4. Scripts")
    check_file(project_root / "scripts" / "init_db.py", "init_db.py", required=False)
    check_file(project_root / "scripts" / "backup.py", "backup.py", required=False)
    check_file(project_root / "scripts" / "restore.py", "restore.py", required=False)
    check_file(project_root / "scripts" / "migrate.py", "migrate.py", required=False)
    
    # 5. Vérifier les scripts PostgreSQL
    print_header("5. Scripts PostgreSQL")
    check_file(
        project_root / "docker" / "postgres" / "init" / "01-init-database.sql",
        "01-init-database.sql",
        required=False
    )
    check_file(
        project_root / "docker" / "postgres" / "init" / "02-create-tables.sql",
        "02-create-tables.sql",
        required=False
    )
    
    # 6. Vérifier les fichiers source
    print_header("6. Fichiers Source")
    all_ok &= check_file(project_root / "config.py", "config.py")
    all_ok &= check_file(project_root / "database.py", "database.py")
    all_ok &= check_file(project_root / "api_clients.py", "api_clients.py")
    all_ok &= check_file(project_root / "collect_stats.py", "collect_stats.py")
    all_ok &= check_file(project_root / "streamlit_app.py", "streamlit_app.py")
    
    # 7. Vérifier les variables d'environnement
    print_header("7. Variables d'Environnement")
    
    # Charger le .env si présent
    env_file = project_root / ".env"
    if env_file.exists():
        print_info(f"Chargement de {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value
    
    env_ok = True
    env_ok &= check_env_var("POSTGRES_PASSWORD", required=True)
    env_ok &= check_env_var("CURSEFORGE_API_KEY", required=True)
    check_env_var("POSTGRES_USER", required=False)
    check_env_var("POSTGRES_DB", required=False)
    check_env_var("DATABASE_URL", required=False)
    
    if not env_ok:
        print_warning("\nCertaines variables d'environnement manquent.")
        print_info("Copiez .env.example vers .env et remplissez les valeurs:")
        print_info("  cp .env.example .env")
        print_info("  notepad .env  # ou nano .env sur Linux/Mac")
    
    # 8. Vérifier la documentation
    print_header("8. Documentation")
    check_file(project_root / "README.md", "README.md", required=False)
    check_file(project_root / "docs" / "QUICKSTART.md", "QUICKSTART.md", required=False)
    check_file(project_root / "docs" / "DATABASE.md", "DATABASE.md", required=False)
    check_file(project_root / "docs" / "ARCHITECTURE.md", "ARCHITECTURE.md", required=False)
    check_file(project_root / "docs" / "REFERENCE.md", "REFERENCE.md", required=False)
    
    # 9. Résumé
    print_header("Résumé")
    
    if all_ok and env_ok:
        print_success("Tous les prérequis sont satisfaits!")
        print_info("\nVous pouvez démarrer le projet avec:")
        print_info("  docker-compose up -d")
        print_info("\nPuis accéder à:")
        print_info("  - Application principale: http://localhost:8501")
        print_info("  - Vue simplifiée: http://localhost:8502")
        return 0
    else:
        print_warning("\nCertains prérequis ne sont pas satisfaits")
        print_info("\nConsultez la documentation:")
        print_info("  - Guide de démarrage: docs/QUICKSTART.md")
        print_info("  - Documentation PostgreSQL: docs/DATABASE.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
