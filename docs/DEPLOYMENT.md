# Create Nuclear - Guide de déploiement

## 🐳 Déploiement Docker (Recommandé)

### Prérequis
- Docker et Docker Compose installés

### Installation rapide

1. **Cloner le projet**
```bash
git clone https://github.com/NoaYnov/Create-nuke--data.git
cd Create-nuke--data
```

2. **Configurer la clé API**
```bash
cp .env.example .env
# Éditez .env avec votre vraie clé CurseForge
```

3. **Lancer avec Docker Compose**
```bash
docker-compose up -d
```

L'application sera accessible sur `http://localhost:8501`

### Commandes utiles
```bash
# Voir les logs
docker-compose logs -f

# Arrêter l'application
docker-compose down

# Redémarrer
docker-compose restart

# Rebuild après modifications
docker-compose up -d --build
```

---

## 🖥️ Déploiement sur Windows (Service)

### Option 1: NSSM (Non-Sucking Service Manager)

1. **Télécharger NSSM**
   - https://nssm.cc/download

2. **Installer le service**
```powershell
# Naviguer vers le dossier NSSM
cd C:\nssm\win64

# Installer le service
.\nssm.exe install CreateNuclearStats "C:\Python311\Scripts\streamlit.exe" "run C:\path\to\app.py"

# Configurer le répertoire de travail
.\nssm.exe set CreateNuclearStats AppDirectory "C:\path\to\Create-nuke--data"

# Démarrer le service
.\nssm.exe start CreateNuclearStats
```

### Option 2: Tâche planifiée Windows

1. Créer un script `start.bat`:
```batch
@echo off
cd /d "C:\Users\Gambey\Documents\CN DATA\Create-nuke--data"
streamlit run app.py --server.port=8501 --server.headless=true
```

2. Créer une tâche planifiée qui exécute ce script au démarrage

---

## 🐧 Déploiement sur Linux (Systemd)

### Créer un service systemd

1. **Créer le fichier service**
```bash
sudo nano /etc/systemd/system/createnuclear.service
```

2. **Contenu du service**
```ini
[Unit]
Description=Create Nuclear Stats Dashboard
After=network.target

[Service]
Type=simple
User=votre_utilisateur
WorkingDirectory=/home/votre_utilisateur/Create-nuke--data
Environment="PATH=/home/votre_utilisateur/.local/bin"
ExecStart=/usr/local/bin/streamlit run app.py --server.port=8501 --server.headless=true
Restart=always

[Install]
WantedBy=multi-user.target
```

3. **Activer et démarrer**
```bash
sudo systemctl daemon-reload
sudo systemctl enable createnuclear
sudo systemctl start createnuclear

# Voir les logs
sudo journalctl -u createnuclear -f
```

---

## 🌐 Exposition sur Internet

### Option 1: Nginx Reverse Proxy

**Configuration Nginx**:
```nginx
server {
    listen 80;
    server_name stats.votredomaine.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: Cloudflare Tunnel (Gratuit, sans ouvrir de ports)

1. **Installer cloudflared**
```bash
# Windows
winget install Cloudflare.cloudflared

# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb
```

2. **Créer le tunnel**
```bash
cloudflared tunnel login
cloudflared tunnel create createnuclear
cloudflared tunnel route dns createnuclear stats.votredomaine.com
```

3. **Configurer et lancer**
```bash
cloudflared tunnel --url http://localhost:8501 run createnuclear
```

---

## 📊 Solutions alternatives

### 1. **Portainer** (Interface Docker web)
- Interface graphique pour gérer Docker
- `docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer-ce`
- Accès: `http://localhost:9000`

### 2. **Traefik** (Reverse proxy automatique)
- Gestion automatique HTTPS avec Let's Encrypt
- Découverte automatique des services Docker

### 3. **Coolify** (PaaS auto-hébergé)
- Alternative à Heroku/Vercel
- https://coolify.io

### 4. **Caprover** (PaaS simple)
- Déploiement en un clic
- https://caprover.com

---

## ⚡ Comparaison des solutions

| Solution | Complexité | Ressources | Avantages |
|----------|-----------|-----------|-----------|
| **Docker Compose** | ⭐⭐ | Faibles | Portable, facile |
| **Service Windows** | ⭐⭐⭐ | Très faibles | Natif Windows |
| **Systemd Linux** | ⭐⭐ | Très faibles | Natif Linux, robuste |
| **Cloudflare Tunnel** | ⭐ | Très faibles | Gratuit, sécurisé, pas de ports |
| **Docker + Nginx** | ⭐⭐⭐ | Moyennes | Production-ready |

---

## 🔒 Sécurité

### Ajouter un .dockerignore
```
.git
.env
__pycache__
*.pyc
.streamlit/secrets.toml
```

### Ajouter au .gitignore
```
.env
.streamlit/secrets.toml
```

---

## 💡 Recommandation

**Pour un usage personnel/local**: 
- Docker Compose (le plus simple)

**Pour partager avec d'autres**:
- Cloudflare Tunnel (gratuit, sécurisé, pas de config réseau)

**Pour un déploiement professionnel**:
- Docker + Nginx + SSL (le plus robuste)
