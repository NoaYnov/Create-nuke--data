import psycopg2
from psycopg2 import sql
from datetime import datetime, timezone
import os

class StatsDatabase:
    def __init__(self, db_url=None):
        """Initialize database connection"""
        if db_url is None:
            db_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/createnuclear_stats')
        
        self.conn = psycopg2.connect(db_url)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create tables if they don't exist"""
        
        # Table pour les stats globales par jour
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                platform VARCHAR(20) NOT NULL,
                total_downloads INTEGER NOT NULL,
                followers INTEGER,
                versions_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, platform)
            )
        """)
        
        # Table pour les stats par version
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS version_stats (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                platform VARCHAR(20) NOT NULL,
                version_name VARCHAR(255) NOT NULL,
                version_number VARCHAR(255),
                downloads INTEGER NOT NULL,
                date_published TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, platform, version_name)
            )
        """)
        
        # Table pour les modpacks
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS modpack_stats (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                platform VARCHAR(20) NOT NULL,
                modpack_name VARCHAR(255) NOT NULL,
                modpack_slug VARCHAR(255),
                downloads INTEGER NOT NULL,
                followers INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, platform, modpack_slug)
            )
        """)
        
        # Index pour améliorer les performances
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_stats_date 
            ON daily_stats(date DESC)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_version_stats_date 
            ON version_stats(date DESC, platform)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_modpack_stats_date 
            ON modpack_stats(date DESC, platform)
        """)
        
        self.conn.commit()
    
    def save_daily_stats(self, platform, total_downloads, followers, versions_count):
        """Save daily global statistics"""
        today = datetime.now(timezone.utc).date()
        
        self.cursor.execute("""
            INSERT INTO daily_stats (date, platform, total_downloads, followers, versions_count)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (date, platform) 
            DO UPDATE SET 
                total_downloads = EXCLUDED.total_downloads,
                followers = EXCLUDED.followers,
                versions_count = EXCLUDED.versions_count
        """, (today, platform, total_downloads, followers, versions_count))
        
        self.conn.commit()
    
    def save_version_stats(self, platform, versions_data):
        """Save version statistics for today"""
        today = datetime.now(timezone.utc).date()
        
        for version in versions_data:
            date_published = None
            if 'date_published' in version and version['date_published']:
                try:
                    date_published = datetime.fromisoformat(version['date_published'].replace('Z', '+00:00'))
                except:
                    pass
            
            self.cursor.execute("""
                INSERT INTO version_stats 
                (date, platform, version_name, version_number, downloads, date_published)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, platform, version_name)
                DO UPDATE SET 
                    downloads = EXCLUDED.downloads
            """, (
                today,
                platform,
                version['name'],
                version.get('version_number', ''),
                version['downloads'],
                date_published
            ))
        
        self.conn.commit()
    
    def save_modpack_stats(self, platform, modpacks_data):
        """Save modpack statistics for today"""
        today = datetime.now(timezone.utc).date()
        
        for modpack in modpacks_data:
            self.cursor.execute("""
                INSERT INTO modpack_stats 
                (date, platform, modpack_name, modpack_slug, downloads, followers)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (date, platform, modpack_slug)
                DO UPDATE SET 
                    downloads = EXCLUDED.downloads,
                    followers = EXCLUDED.followers
            """, (
                today,
                platform,
                modpack['title'] if 'title' in modpack else modpack.get('name', ''),
                modpack['slug'],
                modpack['downloads'],
                modpack.get('follows', modpack.get('followers', 0))
            ))
        
        self.conn.commit()
    
    def get_daily_stats_history(self, platform, days=30):
        """Get historical daily statistics"""
        self.cursor.execute("""
            SELECT date, total_downloads, followers, versions_count
            FROM daily_stats
            WHERE platform = %s
            ORDER BY date DESC
            LIMIT %s
        """, (platform, days))
        
        return self.cursor.fetchall()
    
    def get_version_stats_history(self, platform, version_name=None, days=30):
        """Get historical version statistics"""
        if version_name:
            self.cursor.execute("""
                SELECT date, version_name, downloads
                FROM version_stats
                WHERE platform = %s AND version_name = %s
                ORDER BY date DESC
                LIMIT %s
            """, (platform, version_name, days))
        else:
            self.cursor.execute("""
                SELECT date, version_name, downloads
                FROM version_stats
                WHERE platform = %s
                ORDER BY date DESC
                LIMIT %s
            """, (platform, days))
        
        return self.cursor.fetchall()
    
    def get_download_growth(self, platform, days=7):
        """Calculate download growth over period"""
        self.cursor.execute("""
            WITH stats AS (
                SELECT date, total_downloads,
                       LAG(total_downloads) OVER (ORDER BY date) as prev_downloads
                FROM daily_stats
                WHERE platform = %s
                ORDER BY date DESC
                LIMIT %s
            )
            SELECT 
                date,
                total_downloads,
                total_downloads - COALESCE(prev_downloads, 0) as daily_growth
            FROM stats
            ORDER BY date DESC
        """, (platform, days))
        
        return self.cursor.fetchall()
    
    def get_all_versions_latest(self, platform):
        """Get latest stats for all versions"""
        self.cursor.execute("""
            SELECT DISTINCT ON (version_name)
                version_name, version_number, downloads, date_published
            FROM version_stats
            WHERE platform = %s
            ORDER BY version_name, date DESC
        """, (platform,))
        
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()
