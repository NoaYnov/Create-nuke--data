-- Création des tables pour Create Nuclear Stats
-- Exécuté automatiquement après 01-init-database.sql

-- Table des statistiques quotidiennes globales
CREATE TABLE IF NOT EXISTS daily_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('modrinth', 'curseforge')),
    total_downloads INTEGER NOT NULL CHECK (total_downloads >= 0),
    followers INTEGER CHECK (followers >= 0),
    versions_count INTEGER CHECK (versions_count >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, platform)
);

-- Index pour améliorer les performances des requêtes par date
CREATE INDEX IF NOT EXISTS idx_daily_stats_date 
ON daily_stats(date DESC);

-- Index pour les requêtes par plateforme
CREATE INDEX IF NOT EXISTS idx_daily_stats_platform 
ON daily_stats(platform, date DESC);

-- Commentaires pour documentation
COMMENT ON TABLE daily_stats IS 'Statistiques quotidiennes globales par plateforme';
COMMENT ON COLUMN daily_stats.platform IS 'Plateforme: modrinth ou curseforge';
COMMENT ON COLUMN daily_stats.total_downloads IS 'Nombre total de téléchargements';
COMMENT ON COLUMN daily_stats.followers IS 'Nombre de followers/abonnés';
COMMENT ON COLUMN daily_stats.versions_count IS 'Nombre de versions disponibles';

-- Table des statistiques par version
CREATE TABLE IF NOT EXISTS version_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('modrinth', 'curseforge')),
    version_name VARCHAR(255) NOT NULL,
    version_number VARCHAR(255),
    downloads INTEGER NOT NULL CHECK (downloads >= 0),
    date_published TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, platform, version_name)
);

-- Index pour les requêtes par date et plateforme
CREATE INDEX IF NOT EXISTS idx_version_stats_date 
ON version_stats(date DESC, platform);

-- Index pour rechercher une version spécifique
CREATE INDEX IF NOT EXISTS idx_version_stats_name 
ON version_stats(platform, version_name, date DESC);

-- Commentaires
COMMENT ON TABLE version_stats IS 'Statistiques par version du mod';
COMMENT ON COLUMN version_stats.version_name IS 'Nom de la version (ex: Create Nuclear 1.0.0)';
COMMENT ON COLUMN version_stats.version_number IS 'Numéro de version technique';
COMMENT ON COLUMN version_stats.downloads IS 'Nombre de téléchargements de cette version';

-- Table des statistiques de modpacks
CREATE TABLE IF NOT EXISTS modpack_stats (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(20) NOT NULL CHECK (platform IN ('curseforge', 'modrinth')),
    modpack_name VARCHAR(255) NOT NULL,
    modpack_slug VARCHAR(255) NOT NULL,
    downloads INTEGER NOT NULL CHECK (downloads >= 0),
    followers INTEGER CHECK (followers >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, platform, modpack_slug)
);

-- Index pour les requêtes par date et plateforme
CREATE INDEX IF NOT EXISTS idx_modpack_stats_date 
ON modpack_stats(date DESC, platform);

-- Index pour rechercher un modpack spécifique
CREATE INDEX IF NOT EXISTS idx_modpack_stats_slug 
ON modpack_stats(platform, modpack_slug, date DESC);

-- Commentaires
COMMENT ON TABLE modpack_stats IS 'Statistiques des modpacks utilisant Create Nuclear';
COMMENT ON COLUMN modpack_stats.modpack_slug IS 'Identifiant unique du modpack';
COMMENT ON COLUMN modpack_stats.downloads IS 'Nombre total de téléchargements du modpack';

-- Fonction pour mettre à jour automatiquement updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour mettre à jour updated_at automatiquement
CREATE TRIGGER update_daily_stats_updated_at 
    BEFORE UPDATE ON daily_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_version_stats_updated_at 
    BEFORE UPDATE ON version_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_modpack_stats_updated_at 
    BEFORE UPDATE ON modpack_stats 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Permissions pour l'utilisateur createnuclear
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO createnuclear;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO createnuclear;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO createnuclear;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Tables created successfully';
    RAISE NOTICE '  - daily_stats';
    RAISE NOTICE '  - version_stats';
    RAISE NOTICE '  - modpack_stats';
END $$;
