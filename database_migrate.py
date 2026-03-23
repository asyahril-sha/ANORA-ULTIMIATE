# database_migrate.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Database Migration Script (Railway Compatible)
=============================================================================
"""

import asyncio
import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def run_migration():
    """
    Jalankan migrasi database lengkap
    """
    print("=" * 70)
    print("💜 AMORIA - DATABASE MIGRATION")
    print("=" * 70)
    
    try:
        # 1. Initialize database connection
        print("📁 Initializing database connection...")
        from database.connection import init_db, close_db
        await init_db()
        print("✅ Database connection established")
        
        # 2. Run migrations
        print("📊 Running migrations...")
        from database.migrate import run_migrations, fix_missing_columns
        await run_migrations()
        print("✅ Migrations completed")
        
        # 3. Fix missing columns
        print("🔍 Fixing missing columns...")
        await fix_missing_columns()
        print("✅ Missing columns fixed")
        
        # 4. Verify tables
        print("🔍 Verifying database...")
        from database.connection import get_db
        db = await get_db()
        
        # Check registrations table
        result = await db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='registrations'"
        )
        if result:
            count = await db.fetch_one("SELECT COUNT(*) as count FROM registrations")
            print(f"📋 registrations: {count['count']} rows")
        else:
            print("❌ registrations table not found!")
            return False
        
        # Check working_memory table
        result = await db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='working_memory'"
        )
        if result:
            count = await db.fetch_one("SELECT COUNT(*) as count FROM working_memory")
            print(f"📋 working_memory: {count['count']} rows")
        else:
            print("⚠️ working_memory table not found (will be created when needed)")
        
        # Check long_term_memory table
        result = await db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='long_term_memory'"
        )
        if result:
            count = await db.fetch_one("SELECT COUNT(*) as count FROM long_term_memory")
            print(f"📋 long_term_memory: {count['count']} rows")
        else:
            print("⚠️ long_term_memory table not found (will be created when needed)")
        
        # Check state_tracker table
        result = await db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='state_tracker'"
        )
        if result:
            count = await db.fetch_one("SELECT COUNT(*) as count FROM state_tracker")
            print(f"📋 state_tracker: {count['count']} rows")
        else:
            print("⚠️ state_tracker table not found (will be created when needed)")
        
        # 5. Check indexes
        print("🔍 Checking indexes...")
        indexes = await db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        print(f"📋 Indexes: {len(indexes)} indexes found")
        
        # 6. Database stats
        print("\n📊 DATABASE STATS:")
        
        # Database size
        db_path = settings.database.path
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"   • Database size: {size_mb:.2f} MB")
        
        # Table counts
        tables = await db.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        print(f"   • Total tables: {len(tables)}")
        
        print("=" * 70)
        print("✅ DATABASE MIGRATION COMPLETE!")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            await close_db()
            print("📁 Database connection closed")
        except:
            pass


def main():
    """Main entry point"""
    success = asyncio.run(run_migration())
    
    if success:
        print("\n✅ Database ready for AMORIA!")
        sys.exit(0)
    else:
        print("\n❌ Database migration failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
