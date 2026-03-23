# database/migrate.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Database Migration
=============================================================================
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from database.connection import get_db, close_db

logger = logging.getLogger(__name__)


async def create_registrations_table(db):
    """Create registrations table"""
    await db.execute('''
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
    
    # Indexes
    await db.execute("CREATE INDEX IF NOT EXISTS idx_registrations_role ON registrations(role, status)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_registrations_updated ON registrations(last_updated)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_registrations_level ON registrations(level)")
    
    logger.info("✅ Table 'registrations' created")


async def create_working_memory_table(db):
    """Create working_memory table (1000 chat terakhir)"""
    await db.execute('''
        CREATE TABLE IF NOT EXISTS working_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id TEXT NOT NULL,
            chat_index INTEGER NOT NULL,
            timestamp REAL NOT NULL,
            user_message TEXT,
            bot_response TEXT,
            context TEXT,
            FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
        )
    ''')
    
    # Indexes
    await db.execute("CREATE INDEX IF NOT EXISTS idx_working_memory_reg ON working_memory(registration_id)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_working_memory_chat ON working_memory(registration_id, chat_index)")
    
    logger.info("✅ Table 'working_memory' created")


async def create_long_term_memory_table(db):
    """Create long_term_memory table"""
    await db.execute('''
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration_id TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            timestamp REAL NOT NULL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
        )
    ''')
    
    # Indexes
    await db.execute("CREATE INDEX IF NOT EXISTS idx_long_term_memory_reg ON long_term_memory(registration_id, memory_type)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_long_term_memory_importance ON long_term_memory(importance)")
    
    logger.info("✅ Table 'long_term_memory' created")


async def create_state_tracker_table(db):
    """Create state_tracker table"""
    await db.execute('''
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
            clothing_history TEXT,
            
            -- Emotion & Arousal
            emotion_bot TEXT DEFAULT 'netral',
            arousal_bot INTEGER DEFAULT 0,
            mood_bot TEXT DEFAULT 'normal',
            emotion_user TEXT DEFAULT 'netral',
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
            time_override_history TEXT DEFAULT '[]',
            
            updated_at REAL NOT NULL,
            FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
        )
    ''')
    
    # Indexes
    await db.execute("CREATE INDEX IF NOT EXISTS idx_state_tracker_updated ON state_tracker(updated_at)")
    
    logger.info("✅ Table 'state_tracker' created")


async def create_indexes(db):
    """Create additional indexes for performance"""
    
    # Registration indexes
    await db.execute("CREATE INDEX IF NOT EXISTS idx_registrations_status ON registrations(status)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_registrations_role_status ON registrations(role, status)")
    
    # Working memory indexes
    await db.execute("CREATE INDEX IF NOT EXISTS idx_working_memory_timestamp ON working_memory(timestamp)")
    
    # Long term memory indexes
    await db.execute("CREATE INDEX IF NOT EXISTS idx_long_term_memory_type ON long_term_memory(memory_type)")
    
    logger.info("✅ All indexes created")


async def fix_missing_columns(db):
    """Fix missing columns in existing tables"""
    
    # Check and add missing columns to registrations
    columns = await db.fetch_all("PRAGMA table_info(registrations)")
    column_names = [col['name'] for col in columns]
    
    # Columns to add if missing
    columns_to_add = {
        'in_intimacy_cycle': "BOOLEAN DEFAULT 0",
        'intimacy_cycle_count': "INTEGER DEFAULT 0",
        'last_climax_time': "REAL",
        'cooldown_until': "REAL",
        'user_penis': "INTEGER",
        'user_artist_ref': "TEXT",
        'stamina_bot': "INTEGER DEFAULT 100",
        'stamina_user': "INTEGER DEFAULT 100",
        'bot_hijab': "BOOLEAN DEFAULT 0",
    }
    
    added = 0
    for col_name, col_def in columns_to_add.items():
        if col_name not in column_names:
            try:
                await db.execute(f"ALTER TABLE registrations ADD COLUMN {col_name} {col_def}")
                logger.info(f"✅ Added missing column: {col_name}")
                added += 1
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {col_name}: {e}")
    
    if added > 0:
        logger.info(f"📊 Fixed {added} missing columns in registrations")
    else:
        logger.info("✅ No missing columns found in registrations")
    
    # Check state_tracker columns
    columns = await db.fetch_all("PRAGMA table_info(state_tracker)")
    column_names = [col['name'] for col in columns]
    
    state_columns_to_add = {
        'mood_bot': "TEXT DEFAULT 'normal'",
        'family_status': "TEXT",
        'family_location': "TEXT",
        'family_activity': "TEXT",
        'family_estimate_return': "TEXT",
        'time_override_history': "TEXT DEFAULT '[]'",
        'clothing_history': "TEXT",
    }
    
    added = 0
    for col_name, col_def in state_columns_to_add.items():
        if col_name not in column_names:
            try:
                await db.execute(f"ALTER TABLE state_tracker ADD COLUMN {col_name} {col_def}")
                logger.info(f"✅ Added missing column: {col_name}")
                added += 1
            except Exception as e:
                logger.warning(f"⚠️ Could not add column {col_name}: {e}")
    
    if added > 0:
        logger.info(f"📊 Fixed {added} missing columns in state_tracker")
    
    return added


async def run_migrations():
    """Run all database migrations"""
    logger.info("=" * 60)
    logger.info("🚀 AMORIA - Database Migration")
    logger.info("=" * 60)
    
    try:
        # Get database connection
        db = await get_db()
        
        # Create all tables
        await create_registrations_table(db)
        await create_working_memory_table(db)
        await create_long_term_memory_table(db)
        await create_state_tracker_table(db)
        await create_indexes(db)
        
        # Fix missing columns
        await fix_missing_columns(db)
        
        # Verify tables
        tables = await db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [t['name'] for t in tables]
        
        logger.info("")
        logger.info("📊 TABLES CREATED:")
        for table in sorted(table_names):
            # Get row count
            count = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
            row_count = count['count'] if count else 0
            logger.info(f"   • {table}: {row_count} rows")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ AMORIA Database Migration Complete!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def migrate():
    """Main migration function (alias for run_migrations)"""
    return await run_migrations()


def run_migration_sync():
    """Run migration synchronously (for scripts)"""
    success = asyncio.run(run_migrations())
    return success


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migration
    success = run_migration_sync()
    
    if success:
        print("\n✅ Database ready for AMORIA!")
        sys.exit(0)
    else:
        print("\n❌ Database migration failed!")
        sys.exit(1)


__all__ = ['run_migrations', 'migrate', 'run_migration_sync']
