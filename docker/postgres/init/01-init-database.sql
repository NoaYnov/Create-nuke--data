-- Script d'initialisation PostgreSQL
-- Exécuté automatiquement au premier démarrage du conteneur

-- Création des extensions utiles
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Configuration de la base de données
ALTER DATABASE createnuclear_stats SET timezone TO 'UTC';
ALTER DATABASE createnuclear_stats SET client_encoding TO 'UTF8';

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully';
END $$;
