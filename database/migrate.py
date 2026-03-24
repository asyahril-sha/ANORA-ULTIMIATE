# database/migrate.py
# -*- coding: utf-8 -*-

import logging
from database.connection import get_db

logger = logging.getLogger(__name__)


# =========================================================
# CREATE TABLES (SAFE - NO DROP)
# =========================================================

async def create_registrations_table(db):
    await db.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id TEXT PRIMARY KEY,
        role TEXT NOT NULL,
        sequence INTEGER NOT NULL,
        status TEXT DEFAULT 'active',
        created_at REAL NOT NULL,
        last_updated REAL NOT NULL,
        
        bot_identity TEXT DEFAULT '{}',
        user_identity TEXT DEFAULT '{}',
        
        bot_name TEXT NOT NULL,
        bot_age INTEGER,
        bot_height INTEGER,
        bot_weight INTEGER,
        bot_chest TEXT,
        bot_hijab BOOLEAN DEFAULT 0,
        bot_photo TEXT,
        
        user_name TEXT NOT NULL,
        user_status TEXT DEFAULT 'lajang',
        user_age INTEGER,
        user_height INTEGER,
        user_weight INTEGER,
        user_penis INTEGER,
        user_artist_ref TEXT,
        
        level INTEGER DEFAULT 1,
        total_chats INTEGER DEFAULT 0,
        total_climax_bot INTEGER DEFAULT 0,
        total_climax_user INTEGER DEFAULT 0,
        stamina_bot INTEGER DEFAULT 100,
        stamina_user INTEGER DEFAULT 100,
        
        in_intimacy_cycle BOOLEAN DEFAULT 0,
        intimacy_cycle_count INTEGER DEFAULT 0,
        intimacy_level INTEGER DEFAULT 0,
        last_climax_time REAL,
        cooldown_until REAL,
        
        weighted_memory_score REAL DEFAULT 0.5,
        weighted_memory_data TEXT DEFAULT '{}',
        emotional_bias TEXT DEFAULT '{}',
        emotional_state TEXT DEFAULT '{}',
        
        secondary_emotion TEXT,
        secondary_arousal INTEGER DEFAULT 0,
        secondary_emotion_reason TEXT,
        
        physical_sensation TEXT DEFAULT 'biasa aja',
        physical_hunger INTEGER DEFAULT 30,
        physical_thirst INTEGER DEFAULT 30,
        physical_temperature INTEGER DEFAULT 25,
        
        metadata TEXT DEFAULT '{}',
        last_active REAL
    )
    """)


async def create_working_memory_table(db):
    await db.execute("""
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
    """)


async def create_long_term_memory_table(db):
    await db.execute("""
    CREATE TABLE IF NOT EXISTS long_term_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registration_id TEXT NOT NULL,
        memory_type TEXT NOT NULL,
        content TEXT NOT NULL,
        importance REAL DEFAULT 0.5,
        timestamp REAL NOT NULL,
        status TEXT,
        emotional_tag TEXT,
        metadata TEXT DEFAULT '{}',
        FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
    )
    """)


async def create_state_tracker_table(db):
    await db.execute("""
    CREATE TABLE IF NOT EXISTS state_tracker (
        registration_id TEXT PRIMARY KEY,
        
        location_bot TEXT,
        location_user TEXT,
        position_bot TEXT,
        position_user TEXT,
        position_relative TEXT,
        
        clothing_bot_outer TEXT,
        clothing_bot_outer_bottom TEXT,
        clothing_bot_inner_top TEXT,
        clothing_bot_inner_bottom TEXT,
        clothing_user_outer TEXT,
        clothing_user_outer_bottom TEXT,
        clothing_user_inner_bottom TEXT,
        clothing_history TEXT,
        
        family_status TEXT,
        family_location TEXT,
        family_activity TEXT,
        family_estimate_return TEXT,
        
        activity_bot TEXT,
        activity_user TEXT,
        
        current_time TEXT,
        time_override_history TEXT DEFAULT '[]',
        time_data TEXT,
        
        updated_at REAL NOT NULL,
        FOREIGN KEY (registration_id) REFERENCES registrations(id) ON DELETE CASCADE
    )
    """)


async def create_backups_table(db):
    await db.execute("""
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        size INTEGER,
        created_at REAL NOT NULL,
        type TEXT DEFAULT 'auto',
        status TEXT DEFAULT 'completed',
        metadata TEXT DEFAULT '{}'
    )
    """)


# =========================================================
# ADD MISSING COLUMNS (SAFE MIGRATION)
# =========================================================

async def fix_missing_columns(db):
    try:
        # Fix registrations table
        columns = await db.fetch_all("PRAGMA table_info(registrations)")
        existing = [col["name"] for col in columns]

        needed = {
            "bot_identity": "TEXT DEFAULT '{}'",
            "user_identity": "TEXT DEFAULT '{}'",
            "stamina_bot": "INTEGER DEFAULT 100",
            "stamina_user": "INTEGER DEFAULT 100",
            "physical_sensation": "TEXT DEFAULT 'biasa aja'",
            "physical_hunger": "INTEGER DEFAULT 30",
            "physical_thirst": "INTEGER DEFAULT 30",
            "physical_temperature": "INTEGER DEFAULT 25",
            "weighted_memory_score": "REAL DEFAULT 0.5",
            "weighted_memory_data": "TEXT DEFAULT '{}'",
            "emotional_bias": "TEXT DEFAULT '{}'",
            "secondary_emotion": "TEXT",
            "secondary_arousal": "INTEGER DEFAULT 0",
            "in_intimacy_cycle": "BOOLEAN DEFAULT 0",
            "intimacy_cycle_count": "INTEGER DEFAULT 0",
            "last_climax_time": "REAL",
            "cooldown_until": "REAL",
            "bot_photo": "TEXT",
            "intimacy_level": "INTEGER DEFAULT 0",
            "emotional_state": "TEXT DEFAULT '{}'",
            "last_active": "REAL",
        }

        for col, definition in needed.items():
            if col not in existing:
                try:
                    await db.execute(f"ALTER TABLE registrations ADD COLUMN {col} {definition}")
                    logger.info(f"✅ Added column: {col}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed add column {col}: {e}")
        
        # Fix state_tracker table
        columns = await db.fetch_all("PRAGMA table_info(state_tracker)")
        existing = [col["name"] for col in columns]
        
        state_needed = {
            "position_bot": "TEXT",
            "position_user": "TEXT",
            "position_relative": "TEXT",
            "clothing_bot_outer": "TEXT",
            "clothing_bot_outer_bottom": "TEXT",
            "clothing_bot_inner_top": "TEXT",
            "clothing_bot_inner_bottom": "TEXT",
            "clothing_user_outer": "TEXT",
            "clothing_user_outer_bottom": "TEXT",
            "clothing_user_inner_bottom": "TEXT",
            "clothing_history": "TEXT",
            "family_status": "TEXT",
            "family_location": "TEXT",
            "family_activity": "TEXT",
            "family_estimate_return": "TEXT",
            "current_time": "TEXT",
            "time_override_history": "TEXT DEFAULT '[]'",
            "time_data": "TEXT",
        }
        
        for col, definition in state_needed.items():
            if col not in existing:
                try:
                    await db.execute(f"ALTER TABLE state_tracker ADD COLUMN {col} {definition}")
                    logger.info(f"✅ Added column: {col}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed add column {col}: {e}")

    except Exception as e:
        logger.warning(f"⚠️ Column migration skipped: {e}")


# =========================================================
# INDEXES (OPTIONAL)
# =========================================================

async def create_indexes(db):
    try:
        await db.execute("CREATE INDEX IF NOT EXISTS idx_registrations_role ON registrations(role)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_registrations_status ON registrations(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_working_memory_reg ON working_memory(registration_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_state_tracker_updated ON state_tracker(updated_at)")
        logger.info("✅ Indexes created")
    except Exception as e:
        logger.warning(f"⚠️ Index creation skipped: {e}")


# =========================================================
# MAIN MIGRATION
# =========================================================

async def run_migrations():
    logger.info("=" * 60)
    logger.info("🚀 SQLITE SAFE MIGRATION")
    logger.info("=" * 60)

    try:
        db = await get_db()

        # Create tables
        await create_registrations_table(db)
        await create_working_memory_table(db)
        await create_long_term_memory_table(db)
        await create_state_tracker_table(db)
        await create_backups_table(db)

        # Fix missing columns
        await fix_missing_columns(db)

        # Index
        await create_indexes(db)

        # Commit changes
        await db.commit()

        # VERIFY
        tables = await db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        table_names = [t["name"] for t in tables]

        logger.info("\n📊 TABLES:")
        for table in sorted(table_names):
            try:
                count = await db.fetch_one(f"SELECT COUNT(*) as count FROM {table}")
                row_count = count["count"] if count else 0
                logger.info(f"   • {table}: {row_count} rows")
            except Exception as e:
                logger.warning(f"⚠️ Could not read {table}: {e}")

        logger.info("=" * 60)
        logger.info("✅ Migration Complete")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


# =========================================================
# EXPORT (WAJIB ADA BIAR GAK ERROR IMPORT)
# =========================================================

async def migrate():
    return await run_migrations()
