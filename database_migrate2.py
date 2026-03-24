# quick_fix.py
import asyncio
from database.connection import init_db, get_db, close_db

async def fix():
    await init_db()
    db = await get_db()
    
    # Add weighted_memory_score directly
    try:
        await db.execute("ALTER TABLE registrations ADD COLUMN weighted_memory_score REAL DEFAULT 0.5")
        print("✅ Added weighted_memory_score")
    except Exception as e:
        print(f"⚠️ {e}")
    
    # Add other missing columns
    columns_to_add = {
        "weighted_memory_data": "TEXT DEFAULT '{}'",
        "emotional_bias": "TEXT DEFAULT '{}'",
        "stamina_bot": "INTEGER DEFAULT 100",
        "stamina_user": "INTEGER DEFAULT 100",
        "physical_sensation": "TEXT DEFAULT 'biasa aja'",
        "physical_hunger": "INTEGER DEFAULT 30",
        "physical_thirst": "INTEGER DEFAULT 30",
        "secondary_emotion": "TEXT",
        "secondary_arousal": "INTEGER DEFAULT 0",
        "in_intimacy_cycle": "BOOLEAN DEFAULT 0",
    }
    
    for col, defn in columns_to_add.items():
        try:
            await db.execute(f"ALTER TABLE registrations ADD COLUMN {col} {defn}")
            print(f"✅ Added {col}")
        except Exception as e:
            print(f"⚠️ {col}: {e}")
    
    await db.commit()
    await close_db()
    print("✅ Done!")

asyncio.run(fix())
