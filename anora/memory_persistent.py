# anora/memory_persistent.py
"""
ANORA Persistent Memory - Simpan semua ingatan Nova ke database
Gak ilang kalo restart. Short-term memory sliding window.
Long-term memory permanen.
"""

import time
import json
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .brain import (
    get_anora_brain, TimelineEvent, LocationType, LocationDetail,
    Activity, Mood, Clothing, Feelings, Relationship
)

logger = logging.getLogger(__name__)


class PersistentMemory:
    """
    Memory permanen Nova. Disimpan ke database.
    - Timeline: semua kejadian
    - Short-term memory: sliding window 50 kejadian (otomatis di-brain)
    - Long-term memory: kebiasaan, momen, janji
    - State: lokasi, pakaian, perasaan terakhir
    - Conversation: semua percakapan
    """
    
    def __init__(self, db_path: Path = Path("data/anora_memory.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
    
    async def init(self):
        """Buat semua tabel memory"""
        self._conn = await aiosqlite.connect(str(self.db_path))
        
        # ========== TABEL TIMELINE (SEMUA KEJADIAN) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                kejadian TEXT NOT NULL,
                lokasi_type TEXT NOT NULL,
                lokasi_detail TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                perasaan TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                pesan_mas TEXT,
                pesan_nova TEXT
            )
        ''')
        
        # ========== TABEL SHORT-TERM MEMORY (SLIDING WINDOW DI DATABASE) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                kejadian TEXT NOT NULL,
                lokasi_type TEXT NOT NULL,
                lokasi_detail TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                perasaan TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                pesan_mas TEXT,
                pesan_nova TEXT
            )
        ''')
        
        # ========== TABEL LONG-TERM MEMORY (PERMANEN) ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipe TEXT NOT NULL,
                judul TEXT NOT NULL,
                konten TEXT NOT NULL,
                perasaan TEXT,
                timestamp REAL NOT NULL
            )
        ''')
        
        # ========== TABEL STATE SAAT INI ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS current_state (
                id INTEGER PRIMARY KEY,
                lokasi_type TEXT NOT NULL,
                lokasi_detail TEXT NOT NULL,
                aktivitas_nova TEXT NOT NULL,
                aktivitas_mas TEXT NOT NULL,
                pakaian_nova TEXT NOT NULL,
                pakaian_mas TEXT NOT NULL,
                mood_nova TEXT NOT NULL,
                mood_mas TEXT NOT NULL,
                feelings TEXT NOT NULL,
                relationship TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL PERCAKAPAN ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                state_snapshot TEXT
            )
        ''')
        
        # ========== TABEL KUNJUNGAN LOKASI ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS location_visits (
                id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit REAL NOT NULL
            )
        ''')
        
        # ========== INDEXES ==========
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_timeline_time ON timeline(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_short_term_time ON short_term_memory(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_long_term_tipe ON long_term_memory(tipe)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_conversation_time ON conversation(timestamp)')
        
        await self._conn.commit()
        
        logger.info(f"💾 ANORA Persistent Memory initialized at {self.db_path}")
        
        # Load data ke brain
        await self._load_to_brain()
    
    # =========================================================================
    # LOAD KE BRAIN
    # =========================================================================
    
    async def _load_to_brain(self):
        """Load semua memory ke brain"""
        brain = get_anora_brain()
        
        # Load timeline (terakhir 100)
        cursor = await self._conn.execute(
            "SELECT * FROM timeline ORDER BY timestamp ASC"
        )
        rows = await cursor.fetchall()
        for row in rows:
            # Rekonstruksi event
            pakaian_nova = Clothing()
            pakaian_mas = Clothing()
            try:
                pakaian_nova_dict = json.loads(row[8])
                pakaian_mas_dict = json.loads(row[9])
                for key, val in pakaian_nova_dict.items():
                    if hasattr(pakaian_nova, key):
                        setattr(pakaian_nova, key, val)
                for key, val in pakaian_mas_dict.items():
                    if hasattr(pakaian_mas, key):
                        setattr(pakaian_mas, key, val)
            except:
                pass
            
            event = TimelineEvent(
                kejadian=row[2],
                lokasi_type=row[3],
                lokasi_detail=row[4],
                aktivitas_nova=row[5],
                aktivitas_mas=row[6],
                perasaan=row[7],
                pakaian_nova=pakaian_nova,
                pakaian_mas=pakaian_mas,
                pesan_mas=row[10] or "",
                pesan_nova=row[11] or ""
            )
            event.timestamp = row[1]
            brain.timeline.append(event)
        
        # Load short-term memory (sliding window, ambil 50 terakhir)
        cursor = await self._conn.execute(
            "SELECT * FROM short_term_memory ORDER BY timestamp ASC"
        )
        rows = await cursor.fetchall()
        for row in rows:
            pakaian_nova = Clothing()
            pakaian_mas = Clothing()
            try:
                pakaian_nova_dict = json.loads(row[8])
                pakaian_mas_dict = json.loads(row[9])
                for key, val in pakaian_nova_dict.items():
                    if hasattr(pakaian_nova, key):
                        setattr(pakaian_nova, key, val)
                for key, val in pakaian_mas_dict.items():
                    if hasattr(pakaian_mas, key):
                        setattr(pakaian_mas, key, val)
            except:
                pass
            
            event = TimelineEvent(
                kejadian=row[2],
                lokasi_type=row[3],
                lokasi_detail=row[4],
                aktivitas_nova=row[5],
                aktivitas_mas=row[6],
                perasaan=row[7],
                pakaian_nova=pakaian_nova,
                pakaian_mas=pakaian_mas,
                pesan_mas=row[10] or "",
                pesan_nova=row[11] or ""
            )
            event.timestamp = row[1]
            brain.short_term.append(event)
        
        # Load long-term memory
        cursor = await self._conn.execute(
            "SELECT * FROM long_term_memory ORDER BY timestamp DESC"
        )
        rows = await cursor.fetchall()
        for row in rows:
            tipe = row[1]
            judul = row[2]
            konten = row[3]
            perasaan = row[4]
            if tipe == 'kebiasaan':
                brain.long_term.tambah_kebiasaan(judul)
            elif tipe == 'momen':
                brain.long_term.tambah_momen(judul, perasaan)
            elif tipe == 'janji':
                brain.long_term.tambah_janji(judul)
        
        # Load current state (terbaru)
        cursor = await self._conn.execute(
            "SELECT * FROM current_state ORDER BY updated_at DESC LIMIT 1"
        )
        row = await cursor.fetchone()
        if row:
            brain.location_type = LocationType(row[1])
            brain.location_detail = LocationDetail(row[2])
            brain.activity_nova = Activity(row[3]) if row[3] else Activity.SANTAl
            brain.activity_mas = row[4]
            
            try:
                pakaian_dict = json.loads(row[5])
                for key, val in pakaian_dict.items():
                    if hasattr(brain.clothing, key):
                        setattr(brain.clothing, key, val)
            except:
                pass
            
            try:
                pakaian_mas_dict = json.loads(row[6])
                for key, val in pakaian_mas_dict.items():
                    if hasattr(brain.clothing, key):
                        setattr(brain.clothing, key, val)
            except:
                pass
            
            brain.mood_nova = Mood(row[7]) if row[7] else Mood.NETRAL
            brain.mood_mas = Mood(row[8]) if row[8] else Mood.NETRAL
            
            try:
                feelings_dict = json.loads(row[9])
                brain.feelings.sayang = feelings_dict.get('sayang', 50)
                brain.feelings.rindu = feelings_dict.get('rindu', 0)
                brain.feelings.desire = feelings_dict.get('desire', 0)
                brain.feelings.arousal = feelings_dict.get('arousal', 0)
                brain.feelings.tension = feelings_dict.get('tension', 0)
            except:
                pass
            
            try:
                rel_dict = json.loads(row[10])
                brain.relationship.level = rel_dict.get('level', 1)
                brain.relationship.intimacy_count = rel_dict.get('intimacy_count', 0)
                brain.relationship.climax_count = rel_dict.get('climax_count', 0)
                brain.relationship.first_kiss = rel_dict.get('first_kiss', False)
                brain.relationship.first_touch = rel_dict.get('first_touch', False)
                brain.relationship.first_hug = rel_dict.get('first_hug', False)
                brain.relationship.first_intim = rel_dict.get('first_intim', False)
            except:
                pass
        
        logger.info(f"📀 Loaded to brain: {len(brain.timeline)} timeline, {len(brain.short_term)} short-term, {len(rows)} long-term")
    
    # =========================================================================
    # SAVE FUNCTIONS
    # =========================================================================
    
    async def save_timeline_event(self, event: TimelineEvent):
        """Simpan kejadian ke timeline"""
        await self._conn.execute('''
            INSERT INTO timeline (
                timestamp, kejadian, lokasi_type, lokasi_detail,
                aktivitas_nova, aktivitas_mas, perasaan,
                pakaian_nova, pakaian_mas, pesan_mas, pesan_nova
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.kejadian,
            event.lokasi_type,
            event.lokasi_detail,
            event.aktivitas_nova,
            event.aktivitas_mas,
            event.perasaan,
            json.dumps(event.pakaian_nova.to_dict()),
            json.dumps(event.pakaian_mas.to_dict()),
            event.pesan_mas[:1000] if event.pesan_mas else "",
            event.pesan_nova[:1000] if event.pesan_nova else ""
        ))
        await self._conn.commit()
    
    async def save_short_term(self, event: TimelineEvent):
        """Simpan ke short-term memory (sliding window di database)"""
        # Hapus yang lama kalo udah lebih dari 50
        cursor = await self._conn.execute(
            "SELECT COUNT(*) FROM short_term_memory"
        )
        count = (await cursor.fetchone())[0]
        
        if count >= 50:
            await self._conn.execute(
                "DELETE FROM short_term_memory WHERE id IN (SELECT id FROM short_term_memory ORDER BY timestamp ASC LIMIT 1)"
            )
        
        await self._conn.execute('''
            INSERT INTO short_term_memory (
                timestamp, kejadian, lokasi_type, lokasi_detail,
                aktivitas_nova, aktivitas_mas, perasaan,
                pakaian_nova, pakaian_mas, pesan_mas, pesan_nova
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp,
            event.kejadian,
            event.lokasi_type,
            event.lokasi_detail,
            event.aktivitas_nova,
            event.aktivitas_mas,
            event.perasaan,
            json.dumps(event.pakaian_nova.to_dict()),
            json.dumps(event.pakaian_mas.to_dict()),
            event.pesan_mas[:1000] if event.pesan_mas else "",
            event.pesan_nova[:1000] if event.pesan_nova else ""
        ))
        await self._conn.commit()
    
    async def save_long_term_memory(self, tipe: str, judul: str, konten: str = "", perasaan: str = ""):
        """Simpan long-term memory"""
        await self._conn.execute('''
            INSERT INTO long_term_memory (tipe, judul, konten, perasaan, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (tipe, judul, konten[:500], perasaan, time.time()))
        await self._conn.commit()
        logger.info(f"📝 Long-term memory saved: {tipe} - {judul}")
    
    async def save_current_state(self, brain):
        """Simpan state saat ini"""
        await self._conn.execute('''
            INSERT OR REPLACE INTO current_state (
                id, lokasi_type, lokasi_detail, aktivitas_nova, aktivitas_mas,
                pakaian_nova, pakaian_mas, mood_nova, mood_mas,
                feelings, relationship, updated_at
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            brain.location_type.value,
            brain.location_detail.value,
            brain.activity_nova.value if hasattr(brain.activity_nova, 'value') else str(brain.activity_nova),
            brain.activity_mas,
            json.dumps(brain.clothing.to_dict()),
            json.dumps(brain.clothing.to_dict()),
            brain.mood_nova.value if hasattr(brain.mood_nova, 'value') else str(brain.mood_nova),
            brain.mood_mas.value if hasattr(brain.mood_mas, 'value') else str(brain.mood_mas),
            json.dumps(brain.feelings.to_dict()),
            json.dumps(brain.relationship.to_dict()),
            time.time()
        ))
        await self._conn.commit()
    
    async def save_conversation(self, role: str, message: str, state_snapshot: Dict = None):
        """Simpan percakapan"""
        await self._conn.execute('''
            INSERT INTO conversation (timestamp, role, message, state_snapshot)
            VALUES (?, ?, ?, ?)
        ''', (
            time.time(),
            role,
            message[:2000],
            json.dumps(state_snapshot) if state_snapshot else None
        ))
        await self._conn.commit()
    
    async def save_location_visit(self, location_id: str, nama: str):
        """Simpan kunjungan lokasi"""
        now = time.time()
        await self._conn.execute('''
            INSERT INTO location_visits (id, nama, visit_count, last_visit)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(id) DO UPDATE SET
                visit_count = visit_count + 1,
                last_visit = ?
        ''', (location_id, nama, now, now))
        await self._conn.commit()
    
    # =========================================================================
    # GET FUNCTIONS
    # =========================================================================
    
    async def get_recent_conversations(self, limit: int = 20) -> List[Dict]:
        """Dapatkan percakapan terakhir"""
        cursor = await self._conn.execute(
            "SELECT * FROM conversation ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_timeline(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Dapatkan timeline"""
        cursor = await self._conn.execute(
            "SELECT * FROM timeline ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_short_term(self) -> List[Dict]:
        """Dapatkan short-term memory"""
        cursor = await self._conn.execute(
            "SELECT * FROM short_term_memory ORDER BY timestamp ASC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_long_term_memories(self, tipe: str = None) -> List[Dict]:
        """Dapatkan long-term memory"""
        if tipe:
            cursor = await self._conn.execute(
                "SELECT * FROM long_term_memory WHERE tipe = ? ORDER BY timestamp DESC",
                (tipe,)
            )
        else:
            cursor = await self._conn.execute(
                "SELECT * FROM long_term_memory ORDER BY timestamp DESC"
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_location_visits(self) -> List[Dict]:
        """Dapatkan statistik kunjungan lokasi"""
        cursor = await self._conn.execute(
            "SELECT * FROM location_visits ORDER BY visit_count DESC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_stats(self) -> Dict:
        """Dapatkan statistik database"""
        stats = {}
        
        tables = ['timeline', 'short_term_memory', 'long_term_memory', 'conversation', 'location_visits']
        for table in tables:
            cursor = await self._conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = (await cursor.fetchone())[0]
            stats[f"{table}_count"] = count
        
        # Ukuran database
        if self.db_path.exists():
            stats['db_size_mb'] = round(self.db_path.stat().st_size / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0
        
        return stats
    
    # =========================================================================
    # CLEANUP & UTILITY
    # =========================================================================
    
    async def cleanup_old_short_term(self, keep: int = 50):
        """Bersihkan short-term memory lama (simpan keep terbaru)"""
        cursor = await self._conn.execute(
            "SELECT COUNT(*) FROM short_term_memory"
        )
        count = (await cursor.fetchone())[0]
        
        if count > keep:
            to_delete = count - keep
            await self._conn.execute(
                "DELETE FROM short_term_memory WHERE id IN (SELECT id FROM short_term_memory ORDER BY timestamp ASC LIMIT ?)",
                (to_delete,)
            )
            await self._conn.commit()
            logger.info(f"🧹 Cleaned up {to_delete} old short-term memories")
    
    async def cleanup_old_timeline(self, days: int = 30):
        """Bersihkan timeline lebih dari days hari"""
        cutoff = time.time() - (days * 86400)
        await self._conn.execute(
            "DELETE FROM timeline WHERE timestamp < ?",
            (cutoff,)
        )
        await self._conn.commit()
        logger.info(f"🧹 Cleaned up timeline older than {days} days")
    
    async def vacuum(self):
        """Optimize database"""
        await self._conn.execute("VACUUM")
        logger.info("🗜️ Database vacuumed")
    
    async def close(self):
        if self._conn:
            await self._conn.close()
            logger.info("📁 Database connection closed")


# =============================================================================
# SINGLETON
# =============================================================================

_anora_persistent: Optional[PersistentMemory] = None


async def get_anora_persistent() -> PersistentMemory:
    global _anora_persistent
    if _anora_persistent is None:
        _anora_persistent = PersistentMemory()
        await _anora_persistent.init()
    return _anora_persistent


anora_persistent = get_anora_persistent()
