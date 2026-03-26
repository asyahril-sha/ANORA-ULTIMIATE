"""
ANORA 9.9 Persistent Memory - Simpan semua ingatan Nova ke database
Gak ilang kalo restart. Short-term memory sliding window.
Long-term memory permanen.
DENGAN COMPLETE STATE - Semua aspek disimpan ke database.
TERINTEGRASI DENGAN ANORA 9.9 ENGINES
"""

import time
import json
import aiosqlite
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# ========== IMPORT ANORA 9.9 ==========
from .brain import get_anora_brain
from .emotional_engine import get_emotional_engine
from .relationship import get_relationship_manager
from .conflict_engine import get_conflict_engine

logger = logging.getLogger(__name__)


class PersistentMemory:
    """
    Memory permanen Nova 9.9. Disimpan ke database.
    - Timeline: semua kejadian
    - Short-term memory: sliding window 50 kejadian
    - Long-term memory: kebiasaan, momen, janji
    - State: lokasi, pakaian, perasaan terakhir
    - Conversation: semua percakapan
    - COMPLETE STATE: semua aspek Mas, Nova, dan bersama
    - EMOTIONAL STATE: semua emosi dari emotional engine
    - CONFLICT STATE: semua konflik dari conflict engine
    - RELATIONSHIP STATE: semua fase dari relationship manager
    """
    
    def __init__(self, db_path: Path = Path("data/anora99.db")):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = None
    
    async def init(self):
        """Buat semua tabel memory"""
        self._conn = await aiosqlite.connect(str(self.db_path))
        
        # ========== TABEL STATE UTAMA ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS anora_state_99 (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL COMPLETE STATE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS complete_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                mas_state TEXT NOT NULL,
                nova_state TEXT NOT NULL,
                together_state TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL EMOTIONAL STATE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS emotional_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                sayang REAL NOT NULL,
                rindu REAL NOT NULL,
                trust REAL NOT NULL,
                mood REAL NOT NULL,
                desire REAL NOT NULL,
                arousal REAL NOT NULL,
                tension REAL NOT NULL,
                cemburu REAL NOT NULL,
                kecewa REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL RELATIONSHIP STATE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS relationship_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                phase TEXT NOT NULL,
                level INTEGER NOT NULL,
                interaction_count INTEGER NOT NULL,
                milestones TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL CONFLICT STATE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS conflict_state_99 (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                cemburu REAL NOT NULL,
                kecewa REAL NOT NULL,
                marah REAL NOT NULL,
                sakit_hati REAL NOT NULL,
                is_cold_war INTEGER NOT NULL,
                is_waiting_for_apology INTEGER NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL TIMELINE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS timeline_99 (
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
        
        # ========== TABEL SHORT-TERM MEMORY ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory_99 (
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
        
        # ========== TABEL LONG-TERM MEMORY ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory_99 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipe TEXT NOT NULL,
                judul TEXT NOT NULL,
                konten TEXT NOT NULL,
                perasaan TEXT,
                timestamp REAL NOT NULL
            )
        ''')
        
        # ========== TABEL CURRENT STATE ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS current_state_99 (
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
                complete_state TEXT,
                updated_at REAL NOT NULL
            )
        ''')
        
        # ========== TABEL PERCAKAPAN ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS conversation_99 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                state_snapshot TEXT
            )
        ''')
        
        # ========== TABEL KUNJUNGAN LOKASI ==========
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS location_visits_99 (
                id TEXT PRIMARY KEY,
                nama TEXT NOT NULL,
                visit_count INTEGER DEFAULT 1,
                last_visit REAL NOT NULL
            )
        ''')
        
        # ========== INDEXES ==========
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_timeline_99_time ON timeline_99(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_short_term_99_time ON short_term_memory_99(timestamp)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_long_term_99_tipe ON long_term_memory_99(tipe)')
        await self._conn.execute('CREATE INDEX IF NOT EXISTS idx_conversation_99_time ON conversation_99(timestamp)')
        
        await self._conn.commit()
        
        # Inisialisasi state awal
        await self._init_state()
        
        logger.info(f"💾 ANORA 9.9 Persistent Memory initialized at {self.db_path}")
    
    async def _init_state(self):
        """Inisialisasi state awal"""
        # Cek apakah tabel complete_state sudah ada isinya
        cursor = await self._conn.execute("SELECT COUNT(*) FROM complete_state_99")
        count = await cursor.fetchone()
        
        if count[0] == 0:
            # Inisialisasi complete_state default
            default_complete = {
                'mas': {
                    'clothing': {'top': 'kaos', 'bottom': 'celana pendek', 'boxer': True, 'last_update': time.time()},
                    'position': {'state': None, 'detail': None, 'last_update': 0},
                    'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                    'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                    'holding': {'object': None, 'detail': None, 'last_update': 0},
                    'status': {'mood': 'netral', 'need': None, 'last_update': 0}
                },
                'nova': {
                    'clothing': {'hijab': True, 'top': 'daster rumah motif bunga', 'bra': True, 'cd': True, 'last_update': time.time()},
                    'position': {'state': None, 'detail': None, 'last_update': 0},
                    'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                    'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                    'holding': {'object': None, 'detail': None, 'last_update': 0},
                    'status': {'mood': 'malu-malu', 'need': None, 'last_update': 0}
                },
                'together': {
                    'location': 'kamar',
                    'distance': None,
                    'atmosphere': 'santai',
                    'last_action': None,
                    'pending_action': None,
                    'confirmed_topics': [],
                    'asked_count': 0,
                    'last_question': '',
                    'last_update': time.time()
                }
            }
            
            await self._conn.execute(
                "INSERT INTO complete_state_99 (id, mas_state, nova_state, together_state, updated_at) VALUES (1, ?, ?, ?, ?)",
                (json.dumps(default_complete['mas']), json.dumps(default_complete['nova']), 
                 json.dumps(default_complete['together']), time.time())
            )
            await self._conn.commit()
            logger.info("📀 Complete state initialized")
        
        # Cek emotional state
        cursor = await self._conn.execute("SELECT COUNT(*) FROM emotional_state_99")
        if (await cursor.fetchone())[0] == 0:
            await self._conn.execute(
                "INSERT INTO emotional_state_99 (id, sayang, rindu, trust, mood, desire, arousal, tension, cemburu, kecewa, updated_at) "
                "VALUES (1, 50, 0, 50, 0, 0, 0, 0, 0, 0, ?)",
                (time.time(),)
            )
            await self._conn.commit()
        
        # Cek relationship state
        cursor = await self._conn.execute("SELECT COUNT(*) FROM relationship_state_99")
        if (await cursor.fetchone())[0] == 0:
            await self._conn.execute(
                "INSERT INTO relationship_state_99 (id, phase, level, interaction_count, milestones, updated_at) "
                "VALUES (1, 'stranger', 1, 0, '{}', ?)",
                (time.time(),)
            )
            await self._conn.commit()
        
        # Cek conflict state
        cursor = await self._conn.execute("SELECT COUNT(*) FROM conflict_state_99")
        if (await cursor.fetchone())[0] == 0:
            await self._conn.execute(
                "INSERT INTO conflict_state_99 (id, cemburu, kecewa, marah, sakit_hati, is_cold_war, is_waiting_for_apology, updated_at) "
                "VALUES (1, 0, 0, 0, 0, 0, 0, ?)",
                (time.time(),)
            )
            await self._conn.commit()
    
    # =========================================================================
    # STATE METHODS
    # =========================================================================
    
    async def get_state(self, key: str) -> Optional[str]:
        """Dapatkan state berdasarkan key"""
        cursor = await self._conn.execute("SELECT value FROM anora_state_99 WHERE key = ?", (key,))
        row = await cursor.fetchone()
        return row[0] if row else None
    
    async def set_state(self, key: str, value: str):
        """Simpan state ke database"""
        await self._conn.execute(
            "INSERT OR REPLACE INTO anora_state_99 (key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, time.time())
        )
        await self._conn.commit()
    
    async def get_all_states(self) -> Dict[str, str]:
        """Dapatkan semua state"""
        cursor = await self._conn.execute("SELECT key, value FROM anora_state_99")
        rows = await cursor.fetchall()
        return {row[0]: row[1] for row in rows}
    
    # =========================================================================
    # COMPLETE STATE METHODS
    # =========================================================================
    
    async def save_complete_state(self, brain):
        """Simpan complete_state ke database"""
        try:
            complete = brain.complete_state
            
            await self._conn.execute(
                """INSERT OR REPLACE INTO complete_state_99 
                   (id, mas_state, nova_state, together_state, updated_at) 
                   VALUES (1, ?, ?, ?, ?)""",
                (json.dumps(complete['mas']), json.dumps(complete['nova']), 
                 json.dumps(complete['together']), time.time())
            )
            await self._conn.commit()
            logger.debug("💾 Complete state saved")
        except Exception as e:
            logger.error(f"Error saving complete state: {e}")
    
    async def load_complete_state(self, brain) -> bool:
        """Load complete_state dari database ke brain"""
        try:
            cursor = await self._conn.execute(
                "SELECT mas_state, nova_state, together_state FROM complete_state_99 WHERE id = 1"
            )
            row = await cursor.fetchone()
            
            if row:
                brain.complete_state['mas'] = json.loads(row[0])
                brain.complete_state['nova'] = json.loads(row[1])
                brain.complete_state['together'] = json.loads(row[2])
                logger.info("📀 Complete state loaded")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading complete state: {e}")
            return False
    
    # =========================================================================
    # EMOTIONAL STATE METHODS
    # =========================================================================
    
    async def save_emotional_state(self, emotional_engine):
        """Simpan emotional state ke database"""
        await self._conn.execute('''
            INSERT OR REPLACE INTO emotional_state_99 
            (id, sayang, rindu, trust, mood, desire, arousal, tension, cemburu, kecewa, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            emotional_engine.sayang,
            emotional_engine.rindu,
            emotional_engine.trust,
            emotional_engine.mood,
            emotional_engine.desire,
            emotional_engine.arousal,
            emotional_engine.tension,
            emotional_engine.cemburu,
            emotional_engine.kecewa,
            time.time()
        ))
        await self._conn.commit()
        logger.debug("💾 Emotional state saved")
    
    async def load_emotional_state(self, emotional_engine) -> bool:
        """Load emotional state dari database"""
        try:
            cursor = await self._conn.execute(
                "SELECT sayang, rindu, trust, mood, desire, arousal, tension, cemburu, kecewa FROM emotional_state_99 WHERE id = 1"
            )
            row = await cursor.fetchone()
            
            if row:
                emotional_engine.sayang = row[0]
                emotional_engine.rindu = row[1]
                emotional_engine.trust = row[2]
                emotional_engine.mood = row[3]
                emotional_engine.desire = row[4]
                emotional_engine.arousal = row[5]
                emotional_engine.tension = row[6]
                emotional_engine.cemburu = row[7]
                emotional_engine.kecewa = row[8]
                logger.info("📀 Emotional state loaded")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading emotional state: {e}")
            return False
    
    # =========================================================================
    # RELATIONSHIP STATE METHODS (FIXED)
    # =========================================================================
    
    async def save_relationship_state(self, relationship_manager):
        """Simpan relationship state ke database"""
        try:
            # Konversi milestones ke dictionary simple (hanya boolean)
            milestones_dict = {}
            for name, milestone in relationship_manager.milestones.items():
                milestones_dict[name] = milestone.achieved  # ambil boolean-nya saja
            
            await self._conn.execute(
                """INSERT OR REPLACE INTO relationship_state_99 
                   (id, phase, level, interaction_count, milestones, updated_at) 
                   VALUES (1, ?, ?, ?, ?, ?)""",
                (relationship_manager.phase.value, 
                 relationship_manager.level,
                 relationship_manager.interaction_count,
                 json.dumps(milestones_dict),
                 time.time())
            )
            await self._conn.commit()
            logger.debug("💾 Relationship state saved")
        except Exception as e:
            logger.error(f"Error saving relationship state: {e}")
    
    async def load_relationship_state(self, relationship_manager) -> bool:
        """Load relationship state dari database"""
        try:
            cursor = await self._conn.execute(
                "SELECT phase, level, interaction_count, milestones FROM relationship_state_99 WHERE id = 1"
            )
            row = await cursor.fetchone()
            
            if row:
                from .relationship import RelationshipPhase
                relationship_manager.phase = RelationshipPhase(row[0])
                relationship_manager.level = row[1]
                relationship_manager.interaction_count = row[2]
                
                # Load milestones dari JSON
                milestones_dict = json.loads(row[3])
                for name, achieved in milestones_dict.items():
                    if name in relationship_manager.milestones:
                        relationship_manager.milestones[name].achieved = achieved
                
                logger.info(f"📀 Relationship state loaded: Phase {relationship_manager.phase.value}, Level {relationship_manager.level}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading relationship state: {e}")
            return False
    
    # =========================================================================
    # CONFLICT STATE METHODS
    # =========================================================================
    
    async def save_conflict_state(self, conflict_engine):
        """Simpan conflict state ke database"""
        try:
            await self._conn.execute(
                """INSERT OR REPLACE INTO conflict_state_99 
                   (id, cemburu, kecewa, marah, sakit_hati, is_cold_war, is_waiting_for_apology, updated_at) 
                   VALUES (1, ?, ?, ?, ?, ?, ?, ?)""",
                (conflict_engine.cemburu, conflict_engine.kecewa, conflict_engine.marah,
                 conflict_engine.sakit_hati, 1 if conflict_engine.is_cold_war else 0,
                 1 if conflict_engine.is_waiting_for_apology else 0, time.time())
            )
            await self._conn.commit()
            logger.debug("💾 Conflict state saved")
        except Exception as e:
            logger.error(f"Error saving conflict state: {e}")
    
    async def load_conflict_state(self, conflict_engine) -> bool:
        """Load conflict state dari database"""
        try:
            cursor = await self._conn.execute(
                "SELECT cemburu, kecewa, marah, sakit_hati, is_cold_war, is_waiting_for_apology FROM conflict_state_99 WHERE id = 1"
            )
            row = await cursor.fetchone()
            
            if row:
                conflict_engine.cemburu = row[0]
                conflict_engine.kecewa = row[1]
                conflict_engine.marah = row[2]
                conflict_engine.sakit_hati = row[3]
                conflict_engine.is_cold_war = bool(row[4])
                conflict_engine.is_waiting_for_apology = bool(row[5])
                logger.info("📀 Conflict state loaded")
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading conflict state: {e}")
            return False
    
    # =========================================================================
    # SAVE ALL STATES
    # =========================================================================
    
    async def save_all_states(self, brain, emotional, relationship, conflict):
        """Simpan semua state sekaligus"""
        await self.save_complete_state(brain)
        await self.save_emotional_state(emotional)
        await self.save_relationship_state(relationship)
        await self.save_conflict_state(conflict)
        await self.save_current_state(brain)
    
    async def load_all_states(self, brain, emotional, relationship, conflict):
        """Load semua state sekaligus"""
        await self.load_complete_state(brain)
        await self.load_emotional_state(emotional)
        await self.load_relationship_state(relationship)
        await self.load_conflict_state(conflict)
    
    # =========================================================================
    # TIMELINE METHODS
    # =========================================================================
    
    async def save_timeline_event(self, event):
        """Simpan kejadian ke timeline"""
        await self._conn.execute('''
            INSERT INTO timeline_99 (
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
    
    async def save_short_term(self, event):
        """Simpan ke short-term memory"""
        cursor = await self._conn.execute("SELECT COUNT(*) FROM short_term_memory_99")
        count = (await cursor.fetchone())[0]
        
        if count >= 50:
            await self._conn.execute(
                "DELETE FROM short_term_memory_99 WHERE id IN (SELECT id FROM short_term_memory_99 ORDER BY timestamp ASC LIMIT 1)"
            )
        
        await self._conn.execute('''
            INSERT INTO short_term_memory_99 (
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
            INSERT INTO long_term_memory_99 (tipe, judul, konten, perasaan, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (tipe, judul, konten[:500], perasaan, time.time()))
        await self._conn.commit()
        logger.info(f"📝 Long-term memory saved: {tipe} - {judul}")
    
    async def save_current_state(self, brain):
        """Simpan state saat ini"""
        state = brain.get_current_state()
        
        await self._conn.execute('''
            INSERT OR REPLACE INTO current_state_99 (
                id, lokasi_type, lokasi_detail, aktivitas_nova, aktivitas_mas,
                pakaian_nova, pakaian_mas, mood_nova, mood_mas,
                feelings, relationship, complete_state, updated_at
            ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            json.dumps(brain.relationship_state.to_dict()),
            json.dumps(brain.complete_state),
            time.time()
        ))
        await self._conn.commit()
    
    async def save_conversation(self, role: str, message: str, state_snapshot: Dict = None):
        """Simpan percakapan"""
        await self._conn.execute('''
            INSERT INTO conversation_99 (timestamp, role, message, state_snapshot)
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
            INSERT INTO location_visits_99 (id, nama, visit_count, last_visit)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(id) DO UPDATE SET
                visit_count = visit_count + 1,
                last_visit = ?
        ''', (location_id, nama, now, now))
        await self._conn.commit()
    
    # =========================================================================
    # GET METHODS
    # =========================================================================
    
    async def get_recent_conversations(self, limit: int = 20) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM conversation_99 ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_timeline(self, limit: int = 100) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM timeline_99 ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows][::-1]
    
    async def get_short_term(self) -> List[Dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM short_term_memory_99 ORDER BY timestamp ASC"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_long_term_memories(self, tipe: str = None) -> List[Dict]:
        if tipe:
            cursor = await self._conn.execute(
                "SELECT * FROM long_term_memory_99 WHERE tipe = ? ORDER BY timestamp DESC",
                (tipe,)
            )
        else:
            cursor = await self._conn.execute(
                "SELECT * FROM long_term_memory_99 ORDER BY timestamp DESC"
            )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_stats(self) -> Dict:
        stats = {}
        tables = ['timeline_99', 'short_term_memory_99', 'long_term_memory_99', 
                  'conversation_99', 'location_visits_99', 'complete_state_99',
                  'emotional_state_99', 'relationship_state_99', 'conflict_state_99']
        for table in tables:
            cursor = await self._conn.execute(f"SELECT COUNT(*) FROM {table}")
            count = (await cursor.fetchone())[0]
            stats[f"{table}_count"] = count
        if self.db_path.exists():
            stats['db_size_mb'] = round(self.db_path.stat().st_size / (1024 * 1024), 2)
        return stats
    
    # =========================================================================
    # CLEANUP & UTILITY
    # =========================================================================
    
    async def cleanup_old_short_term(self, keep: int = 50):
        cursor = await self._conn.execute("SELECT COUNT(*) FROM short_term_memory_99")
        count = (await cursor.fetchone())[0]
        if count > keep:
            to_delete = count - keep
            await self._conn.execute(
                "DELETE FROM short_term_memory_99 WHERE id IN (SELECT id FROM short_term_memory_99 ORDER BY timestamp ASC LIMIT ?)",
                (to_delete,)
            )
            await self._conn.commit()
    
    async def vacuum(self):
        await self._conn.execute("VACUUM")
    
    async def close(self):
        if self._conn:
            await self._conn.close()


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
