# ============================================
# Create Nuclear Stats - Application Image
# ============================================
# Multi-stage build pour optimiser la taille
# ============================================

FROM python:3.10-slim as base

# Métadonnées
LABEL maintainer="Create Nuclear Stats Team"
LABEL description="Statistics dashboard for Create Nuclear mod"
LABEL version="2.0"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser

# Définir le répertoire de travail
WORKDIR /app

# ============================================
# Stage: Dependencies
# ============================================
FROM base as dependencies

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage: Application
# ============================================
FROM dependencies as application

# Copier le code source
COPY --chown=appuser:appuser . .

# Créer les répertoires nécessaires
RUN mkdir -p data backups logs && \
    chown -R appuser:appuser data backups logs

# Passer à l'utilisateur non-root
USER appuser

# Healthcheck pour Streamlit
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Port par défaut (peut être overridé)
EXPOSE 8501

# Commande par défaut (overridée par docker-compose)
CMD ["python", "-m", "streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
