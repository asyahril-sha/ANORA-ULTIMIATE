# database/connection.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Database Connection
=============================================================================
"""

import time
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

import aiosqlite

from config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manajemen koneksi database SQLite
    Support async operations dengan connection pooling
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.pool_size = settings.database.pool_size
        self.timeout = settings.database.timeout
        self._connection = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize database and create tables"""
        try:
            # Buat directory jika belum ada
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Koneksi pertama untuk setup
            self._connection = await aiosqlite.connect(
                str(self.db_path),
                timeout=self.timeout
            )
            
            # Enable foreign keys
            await self._connection.execute("PRAGMA foreign_keys = ON")
            
            # Optimize SQLite for performance
            await self._connection.execute("PRAGMA journal_mode = WAL")
            await self._connection.execute("PRAGMA synchronous = NORMAL")
            await self._connection.execute("PRAGMA cache_size = 10000")
            await self._connection.execute("PRAGMA temp_store = MEMORY")
            
            self._initialized = True
            logger.info(f"✅ Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def _create_tables(self):
        """Create all database tables"""
        
        # ===== REGISTRATIONS TABLE (Multi-Identity) =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                sequence INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                created_at REAL NOT NULL,
                last_updated REAL NOT NULL,
                
                -- Bot Identity
                bot_name TEXT NOT NULL,
                bot_age INTEGER,
                bot_height INTEGER,
                bot_weight INTEGER,
                bot_chest TEXT,
                bot_hijab BOOLEAN DEFAULT 0,
                
                -- User Identity
                user_name TEXT NOT NULL,
                user_status TEXT DEFAULT 'lajang',
                user_age INTEGER,
                user_height INTEGER,
                user_weight INTEGER,
                user_penis INTEGER,
                user_artist_ref TEXT,
                
                -- Progress
                level INTEGER DEFAULT 1,
                total_chats INTEGER DEFAULT 0,
                total_climax_bot INTEGER DEFAULT 0,
                total_climax_user INTEGER DEFAULT 0,
                stamina_bot INTEGER DEFAULT 100,
                stamina_user INTEGER DEFAULT 100,
                
                -- Intimacy Cycle
                in_intimacy_cycle BOOLEAN DEFAULT 0,
                intimacy_cycle_count INTEGER DEFAULT 0,
                last_climax_time REAL,
                cooldown_until REAL,
                
                -- Metadata
                metadata TEXT DEFAULT '{}'
            )
        ''')
        
        # ===== WORKING MEMORY TABLE (1000 chat terakhir) =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS working_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id TEXT NOT NULL,
                chat_index INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                user_message TEXT,
                bot_response TEXT,
                context TEXT,  -- JSON
                FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
            )
        ''')
        
        # ===== LONG TERM MEMORY TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,  -- milestone, promise, plan, preference, topic
                content TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                timestamp REAL NOT NULL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
            )
        ''')
        
        # ===== STATE TRACKER TABLE =====
        await self._connection.execute('''
            CREATE TABLE IF NOT EXISTS state_tracker (
                registration_id TEXT PRIMARY KEY,
                
                -- Location & Position
                location_bot TEXT,
                location_user TEXT,
                position_bot TEXT,
                position_user TEXT,
                position_relative TEXT,
                
                -- Clothing (hierarchy)
                clothing_bot_outer TEXT,
                clothing_bot_inner_top TEXT,
                clothing_bot_inner_bottom TEXT,
                clothing_user_outer TEXT,
                clothing_user_inner_bottom TEXT,
                clothing_history TEXT,  -- JSON array
                
                -- Emotion & Arousal
                emotion_bot TEXT,
                arousal_bot INTEGER DEFAULT 0,
                mood_bot TEXT,
                emotion_user TEXT,
                arousal_user INTEGER DEFAULT 0,
                
                -- Family State (IPAR & PELAKOR)
                family_status TEXT,
                family_location TEXT,
                family_activity TEXT,
                family_estimate_return TEXT,
                
                -- Activity
                activity_bot TEXT,
                activity_user TEXT,
                
                -- Time
                current_time TEXT,
                time_override_history TEXT,  -- JSON array
                
                updated_at REAL,
                FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
            )
        ''')
        
        # ===== INDEXES =====
        await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_registrations_role ON registrations(role, status)")
        await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_registrations_updated ON registrations(last_updated)")
        await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_working_memory_reg ON working_memory(registration_id)")
        await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_working_memory_chat ON working_memory(registration_id, chat_index)")
        await self._connection.execute("CREATE INDEX IF NOT EXISTS idx_long_term_memory_reg ON long_term_memory(registration_id, memory_type)")
        
        await self._connection.commit()
        logger.info("✅ Database tables created")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self._initialized:
            await self.initialize()
            await self._create_tables()
            
        conn = None
        try:
            conn = await aiosqlite.connect(
                str(self.db_path),
                timeout=self.timeout
            )
            await conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        finally:
            if conn:
                await conn.close()
    
    async def execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        """Execute query and return cursor"""
        async with self.get_connection() as conn:
            cursor = await conn.execute(query, params)
            await conn.commit()
            return cursor
    
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one row as dict"""
        async with self.get_connection() as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all rows as list of dicts"""
        async with self.get_connection() as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def execute_many(self, query: str, params_list: List[tuple]):
        """Execute many inserts/updates"""
        async with self.get_connection() as conn:
            await conn.executemany(query, params_list)
            await conn.commit()
    
    async def vacuum(self):
        """Vacuum database (optimize)"""
        async with self.get_connection() as conn:
            await conn.execute("VACUUM")
            logger.info("✅ Database vacuum completed")
    
    async def backup(self, backup_path: Path) -> bool:
        """Backup database to file"""
        try:
            async with self.get_connection() as conn:
                await conn.backup(aiosqlite.connect(str(backup_path)))
            logger.info(f"✅ Database backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {}
        
        tables = ['registrations', 'working_memory', 'long_term_memory', 'state_tracker']
        
        for table in tables:
            try:
                result = await self.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = result['count'] if result else 0
            except:
                stats[f"{table}_count"] = 0
        
        # Active registrations
        active = await self.fetch_one(
            "SELECT COUNT(*) as count FROM registrations WHERE status = 'active'"
        )
        stats['active_registrations'] = active['count'] if active else 0
        
        # Total chats
        total_chats = await self.fetch_one(
            "SELECT SUM(total_chats) as total FROM registrations"
        )
        stats['total_chats_all_time'] = total_chats['total'] if total_chats and total_chats['total'] else 0
        
        if self.db_path.exists():
            stats['db_size_mb'] = round(self.db_path.stat().st_size / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
            
        return stats
    
    async def close(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._initialized = False
            logger.info("📁 Database connection closed")


# =============================================================================
# GLOBAL DATABASE INSTANCE
# =============================================================================

_db_instance: Optional[DatabaseConnection] = None


async def get_db() -> DatabaseConnection:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection(settings.database.path)
        await _db_instance.initialize()
        await _db_instance._create_tables()
    return _db_instance


async def init_db():
    """Initialize database (for startup)"""
    db = await get_db()
    return db


async def close_db():
    """Close global database connection"""
    global _db_instance
    if _db_instance:
        await _db_instance.close()
        _db_instance = None
        logger.info("📁 Global database connection closed")


__all__ = [
    'DatabaseConnection',
    'get_db',
    'init_db',
    'close_db',
]
