# anora/database.py
"""
ANORA Database - Memory Nova yang personal, gak tercampur AMORIA.
"""

import time
import json
import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class AnoraDatabase:
    """Database khusus Nova."""
    
    def __init__(self, db_path: Path = Path("data/anora.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
    
    async def init(self):
        """Buat tabel kalo belum ada."""
        self._conn = await aiosqlite.connect(str(self.db_path))
        
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS anora_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jenis TEXT NOT NULL,
                judul TEXT NOT NULL,
                isi TEXT NOT NULL,
                perasaan TEXT,
                waktu REAL NOT NULL
            )
        ''')
        
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS anora_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS anora_places (
                id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit REAL NOT NULL
            )
        ''')
        
        await self._conn.commit()
        await self._init_state()
        logger.info(f"✅ ANORA database initialized at {self.db_path}")
    
    async def _init_state(self):
        defaults = {
            'sayang': '50',
            'rindu': '0',
            'desire': '0',
            'arousal': '0',
            'tension': '0',
            'level': '1',
            'intimacy_cycle_count': '0',
            'in_intimacy_cycle': '0',
            'energi': '100'
        }
        
        for key, val in defaults.items():
            await self._conn.execute(
                "INSERT OR IGNORE INTO anora_state (key, value, updated_at) VALUES (?, ?, ?)",
                (key, val, time.time())
            )
        
        await self._conn.commit()
    
    async def get_state(self, key: str) -> Optional[str]:
        cursor = await self._conn.execute("SELECT value FROM anora_state WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def set_state(self, key: str, value: str):
        await self._conn.execute(
            "INSERT OR REPLACE INTO anora_state (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, time.time())
        )
        await self._conn.commit()
    
    async def get_all_states(self) -> Dict[str, str]:
        cursor = await self._conn.execute("SELECT key, value FROM anora_state")
        rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}
    
    async def tambah_momen(self, judul: str, isi: str, perasaan: str):
        await self._conn.execute(
            "INSERT INTO anora_memory (jenis, judul, isi, perasaan, waktu) VALUES (?, ?, ?, ?, ?)",
            ('momen', judul, isi, perasaan, time.time())
        )
        await self._conn.commit()
    
    async def tambah_ingatan(self, judul: str, isi: str, perasaan: str):
        await self._conn.execute(
            "INSERT INTO anora_memory (jenis, judul, isi, perasaan, waktu) VALUES (?, ?, ?, ?, ?)",
            ('ingatan', judul, isi, perasaan, time.time())
        )
        await self._conn.commit()
    
    async def get_momen_terbaru(self, limit: int = 20) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM anora_memory WHERE jenis = 'momen' ORDER BY waktu DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_ingatan(self, limit: int = 30) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM anora_memory WHERE jenis = 'ingatan' ORDER BY waktu DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def flashback(self, pemicu: str = "") -> Optional[Dict]:
        if pemicu:
            cursor = await self._conn.execute(
                "SELECT * FROM anora_memory WHERE jenis = 'momen' AND (judul LIKE ? OR isi LIKE ?) ORDER BY waktu DESC LIMIT 5",
                (f'%{pemicu}%', f'%{pemicu}%')
            )
        else:
            cursor = await self._conn.execute(
                "SELECT * FROM anora_memory WHERE jenis = 'momen' ORDER BY waktu DESC LIMIT 10"
            )
        
        rows = await cursor.fetchall()
        if rows:
            import random
            return dict(random.choice(rows))
        return None
    
    async def close(self):
        if self._conn:
            await self._conn.close()


_anora_db: Optional[AnoraDatabase] = None


async def get_anora_db() -> AnoraDatabase:
    global _anora_db
    if _anora_db is None:
        _anora_db = AnoraDatabase()
        await _anora_db.init()
    return _anora_db


async def init_anora_db() -> AnoraDatabase:
    return await get_anora_db()
