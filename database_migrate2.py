#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Safe quick fix for database - handles existing columns gracefully
"""

import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

async def safe_fix():
    """Add missing columns safely without duplicate errors"""
    
    print("=" * 60)
    print("🔧 AMORIA - SAFE DATABASE FIX")
    print("=" * 60)
    
    try:
        from database.connection import init_db, get_db, close_db
        
        # Initialize
        await init_db()
        db = await get_db()
        
        print("\n📊 Checking existing columns...")
        
        # Get current columns
        columns = await db.fetch_all("PRAGMA table_info(registrations)")
        existing = [col['name'] for col in columns]
        
        print(f"   Current columns: {len(existing)}")
        print(f"   Existing: {', '.join(existing[:10])}...")
        
        # Define columns to add (only those that don't exist)
        columns_to_add = {
            # Identity
            "bot_identity": "TEXT DEFAULT '{}'",
            "user_identity": "TEXT DEFAULT '{}'",
            
            # Bot Physical
            "bot_age": "INTEGER",
            "bot_height": "INTEGER",
            "bot_weight": "INTEGER",
            "bot_chest": "TEXT",
            "bot_hijab": "BOOLEAN DEFAULT 0",
            
            # User Physical
            "user_status": "TEXT DEFAULT 'lajang'",
            "user_age": "INTEGER",
            "user_height": "INTEGER",
            "user_weight": "INTEGER",
            "user_penis": "INTEGER",
            "user_artist_ref": "TEXT",
            
            # Stats
            "total_climax_bot": "INTEGER DEFAULT 0",
            "total_climax_user": "INTEGER DEFAULT 0",
            "stamina_bot": "INTEGER DEFAULT 100",
            "stamina_user": "INTEGER DEFAULT 100",
            
            # Intimacy
            "in_intimacy_cycle": "BOOLEAN DEFAULT 0",
            "intimacy_cycle_count": "INTEGER DEFAULT 0",
            "last_climax_time": "REAL",
            "cooldown_until": "REAL",
            
            # Memory & Emotion (CRITICAL)
            "weighted_memory_score": "REAL DEFAULT 0.5",
            "weighted_memory_data": "TEXT DEFAULT '{}'",
            "emotional_bias": "TEXT DEFAULT '{}'",
            
            # Secondary Emotion
            "secondary_emotion": "TEXT",
            "secondary_arousal": "INTEGER DEFAULT 0",
            "secondary_emotion_reason": "TEXT",
            
            # Physical State
            "physical_sensation": "TEXT DEFAULT 'biasa aja'",
            "physical_hunger": "INTEGER DEFAULT 30",
            "physical_thirst": "INTEGER DEFAULT 30",
            "physical_temperature": "INTEGER DEFAULT 25",
        }
        
        print("\n🔍 Checking for missing columns...")
        
        added = 0
        skipped = 0
        
        for col, definition in columns_to_add.items():
            if col not in existing:
                try:
                    await db.execute(f"ALTER TABLE registrations ADD COLUMN {col} {definition}")
                    print(f"  ✅ Added: {col}")
                    added += 1
                except Exception as e:
                    print(f"  ⚠️ Failed: {col} - {e}")
                    skipped += 1
            else:
                print(f"  ⏭️  Skipped (exists): {col}")
                skipped += 1
        
        # Commit changes
        await db.commit()
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Added: {added} column(s)")
        print(f"   ⏭️  Skipped: {skipped} column(s)")
        
        # Verify critical column
        columns = await db.fetch_all("PRAGMA table_info(registrations)")
        col_names = [c['name'] for c in columns]
        
        print("\n🔍 Verification:")
        if 'weighted_memory_score' in col_names:
            print("   ✅ weighted_memory_score exists!")
        else:
            print("   ❌ weighted_memory_score STILL MISSING!")
        
        print(f"   📊 Total columns now: {len(col_names)}")
        
        # Check state_tracker
        print("\n📊 Checking state_tracker...")
        
        result = await db.fetch_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='state_tracker'"
        )
        
        if result:
            columns = await db.fetch_all("PRAGMA table_info(state_tracker)")
            col_names = [c['name'] for c in columns]
            
            needed = ['clothing_bot_outer_bottom', 'family_status']
            missing = [c for c in needed if c not in col_names]
            
            if missing:
                print(f"   ⚠️ Missing in state_tracker: {missing}")
                for col in missing:
                    try:
                        await db.execute(f"ALTER TABLE state_tracker ADD COLUMN {col} TEXT")
                        print(f"   ✅ Added: {col}")
                    except Exception as e:
                        print(f"   ❌ Failed: {col} - {e}")
                await db.commit()
            else:
                print("   ✅ All critical columns present")
        else:
            print("   ⚠️ state_tracker table not found")
        
        await close_db()
        
        print("\n" + "=" * 60)
        print("✅ SAFE DATABASE FIX COMPLETE!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(safe_fix())
    sys.exit(0 if success else 1)
