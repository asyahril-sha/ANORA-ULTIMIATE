# database/repository.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Database Repository
=============================================================================
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .connection import get_db
from .models import (
    Registration, RegistrationStatus, CharacterRole,
    WorkingMemoryItem, LongTermMemoryItem, MemoryType,
    StateTracker, ClothingState, MoodType,
    USER_PHYSICAL_TEMPLATES
)

logger = logging.getLogger(__name__)


class Repository:
    """
    Repository untuk semua operasi database AMORIA
    """
    
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        """Get database connection"""
        if not self.db:
            self.db = await get_db()
        return self.db
    
    # =========================================================================
    # REGISTRATION OPERATIONS
    # =========================================================================
    
    async def get_next_sequence(self, role: CharacterRole) -> int:
        """
        Dapatkan nomor urut berikutnya untuk role tertentu
        
        Args:
            role: Role karakter
        
        Returns:
            Nomor urut berikutnya (1, 2, 3, ...)
        """
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT MAX(sequence) as max_seq FROM registrations WHERE role = ?",
            (role.value,)
        )
        
        if result and result['max_seq']:
            return result['max_seq'] + 1
        return 1
    
    async def create_registration(self, registration: Registration) -> str:
        """
        Buat registrasi baru
        
        Args:
            registration: Registration object
        
        Returns:
            registration_id
        """
        db = await self._get_db()
        data = registration.to_dict()
        
        await db.execute(
            """
            INSERT INTO registrations (
                id, role, sequence, status, created_at, last_updated,
                bot_name, bot_age, bot_height, bot_weight, bot_chest, bot_hijab,
                user_name, user_status, user_age, user_height, user_weight,
                user_penis, user_artist_ref,
                level, total_chats, total_climax_bot, total_climax_user,
                stamina_bot, stamina_user,
                in_intimacy_cycle, intimacy_cycle_count,
                last_climax_time, cooldown_until,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data['id'], data['role'], data['sequence'], data['status'],
                data['created_at'], data['last_updated'],
                data['bot_name'], data['bot_age'], data['bot_height'],
                data['bot_weight'], data['bot_chest'], data['bot_hijab'],
                data['user_name'], data['user_status'], data['user_age'],
                data['user_height'], data['user_weight'], data['user_penis'],
                data['user_artist_ref'],
                data['level'], data['total_chats'], data['total_climax_bot'],
                data['total_climax_user'], data['stamina_bot'], data['stamina_user'],
                data['in_intimacy_cycle'], data['intimacy_cycle_count'],
                data['last_climax_time'], data['cooldown_until'],
                data['metadata']
            )
        )
        
        logger.info(f"✅ Created registration: {registration.id}")
        return registration.id
    
    async def get_registration(self, registration_id: str) -> Optional[Registration]:
        """
        Dapatkan registrasi berdasarkan ID
        
        Args:
            registration_id: ID registrasi (contoh: IPAR-001)
        
        Returns:
            Registration object atau None
        """
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT * FROM registrations WHERE id = ?",
            (registration_id,)
        )
        
        if not result:
            return None
        
        return Registration(
            id=result['id'],
            role=CharacterRole(result['role']),
            sequence=result['sequence'],
            status=RegistrationStatus(result['status']),
            created_at=result['created_at'],
            last_updated=result['last_updated'],
            bot_name=result['bot_name'],
            bot_age=result['bot_age'],
            bot_height=result['bot_height'],
            bot_weight=result['bot_weight'],
            bot_chest=result['bot_chest'],
            bot_hijab=bool(result['bot_hijab']),
            user_name=result['user_name'],
            user_status=result['user_status'],
            user_age=result['user_age'],
            user_height=result['user_height'],
            user_weight=result['user_weight'],
            user_penis=result['user_penis'],
            user_artist_ref=result['user_artist_ref'],
            level=result['level'],
            total_chats=result['total_chats'],
            total_climax_bot=result['total_climax_bot'],
            total_climax_user=result['total_climax_user'],
            stamina_bot=result['stamina_bot'],
            stamina_user=result['stamina_user'],
            in_intimacy_cycle=bool(result['in_intimacy_cycle']),
            intimacy_cycle_count=result['intimacy_cycle_count'],
            last_climax_time=result['last_climax_time'],
            cooldown_until=result['cooldown_until'],
            metadata=json.loads(result['metadata']) if result['metadata'] else {}
        )
    
    async def get_user_registrations(self, user_id: int, role: Optional[CharacterRole] = None) -> List[Registration]:
        """
        Dapatkan semua registrasi untuk user (admin)
        
        Args:
            user_id: ID user
            role: Filter role (opsional)
        
        Returns:
            List registrasi
        """
        # Untuk admin, semua registrasi adalah miliknya
        # Karena admin adalah satu-satunya user
        db = await self._get_db()
        
        if role:
            results = await db.fetch_all(
                "SELECT * FROM registrations WHERE role = ? ORDER BY last_updated DESC",
                (role.value,)
            )
        else:
            results = await db.fetch_all(
                "SELECT * FROM registrations ORDER BY last_updated DESC"
            )
        
        registrations = []
        for row in results:
            registrations.append(Registration(
                id=row['id'],
                role=CharacterRole(row['role']),
                sequence=row['sequence'],
                status=RegistrationStatus(row['status']),
                created_at=row['created_at'],
                last_updated=row['last_updated'],
                bot_name=row['bot_name'],
                bot_age=row['bot_age'],
                bot_height=row['bot_height'],
                bot_weight=row['bot_weight'],
                bot_chest=row['bot_chest'],
                bot_hijab=bool(row['bot_hijab']),
                user_name=row['user_name'],
                user_status=row['user_status'],
                user_age=row['user_age'],
                user_height=row['user_height'],
                user_weight=row['user_weight'],
                user_penis=row['user_penis'],
                user_artist_ref=row['user_artist_ref'],
                level=row['level'],
                total_chats=row['total_chats'],
                total_climax_bot=row['total_climax_bot'],
                total_climax_user=row['total_climax_user'],
                stamina_bot=row['stamina_bot'],
                stamina_user=row['stamina_user'],
                in_intimacy_cycle=bool(row['in_intimacy_cycle']),
                intimacy_cycle_count=row['intimacy_cycle_count'],
                last_climax_time=row['last_climax_time'],
                cooldown_until=row['cooldown_until'],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            ))
        
        return registrations
    
    async def update_registration(self, registration: Registration):
        """Update registrasi"""
        db = await self._get_db()
        data = registration.to_dict()
        
        registration.last_updated = time.time()
        
        await db.execute(
            """
            UPDATE registrations SET
                status = ?, last_updated = ?,
                level = ?, total_chats = ?, total_climax_bot = ?, total_climax_user = ?,
                stamina_bot = ?, stamina_user = ?,
                in_intimacy_cycle = ?, intimacy_cycle_count = ?,
                last_climax_time = ?, cooldown_until = ?,
                metadata = ?
            WHERE id = ?
            """,
            (
                data['status'], registration.last_updated,
                data['level'], data['total_chats'], data['total_climax_bot'],
                data['total_climax_user'], data['stamina_bot'], data['stamina_user'],
                data['in_intimacy_cycle'], data['intimacy_cycle_count'],
                data['last_climax_time'], data['cooldown_until'],
                data['metadata'], registration.id
            )
        )
    
    async def close_registration(self, registration_id: str):
        """Tutup registrasi (close session)"""
        db = await self._get_db()
        await db.execute(
            "UPDATE registrations SET status = ?, last_updated = ? WHERE id = ?",
            (RegistrationStatus.CLOSED.value, time.time(), registration_id)
        )
        logger.info(f"📁 Closed registration: {registration_id}")
    
    async def end_registration(self, registration_id: str):
        """Akhiri registrasi (hapus permanen)"""
        db = await self._get_db()
        await db.execute(
            "UPDATE registrations SET status = ?, last_updated = ? WHERE id = ?",
            (RegistrationStatus.ENDED.value, time.time(), registration_id)
        )
        logger.info(f"💔 Ended registration: {registration_id}")
    
    async def delete_registration(self, registration_id: str):
        """Hapus registrasi permanen (cascade akan menghapus semua terkait)"""
        db = await self._get_db()
        await db.execute("DELETE FROM registrations WHERE id = ?", (registration_id,))
        logger.info(f"🗑️ Deleted registration: {registration_id}")
    
    # =========================================================================
    # WORKING MEMORY OPERATIONS
    # =========================================================================
    
    async def add_to_working_memory(self, item: WorkingMemoryItem):
        """Tambah item ke working memory"""
        db = await self._get_db()
        data = item.to_dict()
        
        await db.execute(
            """
            INSERT INTO working_memory
            (registration_id, chat_index, timestamp, user_message, bot_response, context)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data['registration_id'], data['chat_index'],
                data['timestamp'], data['user_message'],
                data['bot_response'], data['context']
            )
        )
    
    async def get_working_memory(self, registration_id: str, limit: int = 1000) -> List[Dict]:
        """
        Dapatkan working memory (chat terakhir)
        
        Args:
            registration_id: ID registrasi
            limit: Jumlah chat (default 1000)
        
        Returns:
            List chat dengan konteks
        """
        db = await self._get_db()
        
        results = await db.fetch_all(
            """
            SELECT * FROM working_memory
            WHERE registration_id = ?
            ORDER BY chat_index DESC LIMIT ?
            """,
            (registration_id, limit)
        )
        
        # Balik urutan agar kronologis
        results.reverse()
        
        memories = []
        for row in results:
            memories.append({
                'chat_index': row['chat_index'],
                'timestamp': row['timestamp'],
                'user': row['user_message'],
                'bot': row['bot_response'],
                'context': json.loads(row['context']) if row['context'] else {}
            })
        
        return memories
    
    async def get_last_chat_index(self, registration_id: str) -> int:
        """Dapatkan index chat terakhir"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT MAX(chat_index) as max_idx FROM working_memory WHERE registration_id = ?",
            (registration_id,)
        )
        
        return result['max_idx'] if result and result['max_idx'] else 0
    
    async def cleanup_old_working_memory(self, registration_id: str, keep: int = 1000):
        """Hapus working memory lama, sisakan keep terakhir"""
        db = await self._get_db()
        
        # Dapatkan chat_index minimal yang harus dipertahankan
        result = await db.fetch_one(
            """
            SELECT MIN(chat_index) as min_keep FROM (
                SELECT chat_index FROM working_memory
                WHERE registration_id = ?
                ORDER BY chat_index DESC LIMIT ?
            )
            """,
            (registration_id, keep)
        )
        
        if result and result['min_keep']:
            await db.execute(
                "DELETE FROM working_memory WHERE registration_id = ? AND chat_index < ?",
                (registration_id, result['min_keep'])
            )
    
    # =========================================================================
    # LONG TERM MEMORY OPERATIONS
    # =========================================================================
    
    async def add_long_term_memory(self, item: LongTermMemoryItem):
        """Tambah item ke long-term memory"""
        db = await self._get_db()
        data = item.to_dict()
        
        await db.execute(
            """
            INSERT INTO long_term_memory
            (registration_id, memory_type, content, importance, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data['registration_id'], data['memory_type'],
                data['content'], data['importance'], data['timestamp'],
                data['metadata']
            )
        )
    
    async def get_long_term_memory(
        self,
        registration_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Dapatkan long-term memory"""
        db = await self._get_db()
        
        if memory_type:
            results = await db.fetch_all(
                """
                SELECT * FROM long_term_memory
                WHERE registration_id = ? AND memory_type = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
                """,
                (registration_id, memory_type.value, limit)
            )
        else:
            results = await db.fetch_all(
                """
                SELECT * FROM long_term_memory
                WHERE registration_id = ?
                ORDER BY importance DESC, timestamp DESC LIMIT ?
                """,
                (registration_id, limit)
            )
        
        memories = []
        for row in results:
            memories.append({
                'id': row['id'],
                'type': row['memory_type'],
                'content': row['content'],
                'importance': row['importance'],
                'timestamp': row['timestamp'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {}
            })
        
        return memories
    
    # =========================================================================
    # STATE TRACKER OPERATIONS
    # =========================================================================
    
    async def save_state(self, state: StateTracker):
        """Simpan state tracker"""
        db = await self._get_db()
        data = state.to_dict()
        
        # Cek apakah sudah ada
        existing = await db.fetch_one(
            "SELECT registration_id FROM state_tracker WHERE registration_id = ?",
            (state.registration_id,)
        )
        
        state.updated_at = time.time()
        
        if existing:
            await db.execute(
                """
                UPDATE state_tracker SET
                    location_bot = ?, location_user = ?, position_bot = ?,
                    position_user = ?, position_relative = ?,
                    clothing_bot_outer = ?, clothing_bot_inner_top = ?,
                    clothing_bot_inner_bottom = ?, clothing_user_outer = ?,
                    clothing_user_inner_bottom = ?, clothing_history = ?,
                    emotion_bot = ?, arousal_bot = ?, mood_bot = ?,
                    emotion_user = ?, arousal_user = ?,
                    family_status = ?, family_location = ?, family_activity = ?,
                    family_estimate_return = ?,
                    activity_bot = ?, activity_user = ?,
                    current_time = ?, time_override_history = ?,
                    updated_at = ?
                WHERE registration_id = ?
                """,
                (
                    data['location_bot'], data['location_user'],
                    data['position_bot'], data['position_user'],
                    data['position_relative'],
                    data['clothing_bot_outer'], data['clothing_bot_inner_top'],
                    data['clothing_bot_inner_bottom'], data['clothing_user_outer'],
                    data['clothing_user_inner_bottom'], data['clothing_history'],
                    data['emotion_bot'], data['arousal_bot'], data['mood_bot'],
                    data['emotion_user'], data['arousal_user'],
                    data['family_status'], data['family_location'],
                    data['family_activity'], data['family_estimate_return'],
                    data['activity_bot'], data['activity_user'],
                    data['current_time'], data['time_override_history'],
                    data['updated_at'], state.registration_id
                )
            )
        else:
            await db.execute(
                """
                INSERT INTO state_tracker (
                    registration_id, location_bot, location_user, position_bot,
                    position_user, position_relative, clothing_bot_outer,
                    clothing_bot_inner_top, clothing_bot_inner_bottom,
                    clothing_user_outer, clothing_user_inner_bottom,
                    clothing_history, emotion_bot, arousal_bot, mood_bot,
                    emotion_user, arousal_user, family_status, family_location,
                    family_activity, family_estimate_return, activity_bot,
                    activity_user, current_time, time_override_history, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    state.registration_id, data['location_bot'],
                    data['location_user'], data['position_bot'],
                    data['position_user'], data['position_relative'],
                    data['clothing_bot_outer'], data['clothing_bot_inner_top'],
                    data['clothing_bot_inner_bottom'], data['clothing_user_outer'],
                    data['clothing_user_inner_bottom'], data['clothing_history'],
                    data['emotion_bot'], data['arousal_bot'], data['mood_bot'],
                    data['emotion_user'], data['arousal_user'],
                    data['family_status'], data['family_location'],
                    data['family_activity'], data['family_estimate_return'],
                    data['activity_bot'], data['activity_user'],
                    data['current_time'], data['time_override_history'],
                    data['updated_at']
                )
            )
    
    async def load_state(self, registration_id: str) -> Optional[StateTracker]:
        """Load state tracker"""
        db = await self._get_db()
        
        result = await db.fetch_one(
            "SELECT * FROM state_tracker WHERE registration_id = ?",
            (registration_id,)
        )
        
        if not result:
            return None
        
        # Parse clothing history
        clothing_history = []
        if result['clothing_history']:
            clothing_history = json.loads(result['clothing_history'])
        
        # Parse time override history
        time_override_history = []
        if result['time_override_history']:
            time_override_history = json.loads(result['time_override_history'])
        
        # Parse family status
        family_status = None
        if result['family_status']:
            from .models import FamilyStatus
            family_status = FamilyStatus(result['family_status'])
        
        family_location = None
        if result['family_location']:
            from .models import FamilyLocation
            family_location = FamilyLocation(result['family_location'])
        
        # Create ClothingState
        clothing_state = ClothingState(
            bot_outer_top=result['clothing_bot_outer'],
            bot_inner_top=result['clothing_bot_inner_top'],
            bot_inner_bottom=result['clothing_bot_inner_bottom'],
            user_outer_top=result['clothing_user_outer'],
            user_inner_bottom=result['clothing_user_inner_bottom'],
            history=clothing_history
        )
        
        # Set flags from clothing
        clothing_state.bot_outer_top_on = result['clothing_bot_outer'] is not None
        clothing_state.bot_inner_top_on = result['clothing_bot_inner_top'] is not None
        clothing_state.bot_inner_bottom_on = result['clothing_bot_inner_bottom'] is not None
        clothing_state.user_outer_top_on = result['clothing_user_outer'] is not None
        clothing_state.user_inner_bottom_on = result['clothing_user_inner_bottom'] is not None
        
        return StateTracker(
            registration_id=registration_id,
            location_bot=result['location_bot'],
            location_user=result['location_user'],
            position_bot=result['position_bot'],
            position_user=result['position_user'],
            position_relative=result['position_relative'],
            clothing_state=clothing_state,
            emotion_bot=result['emotion_bot'],
            arousal_bot=result['arousal_bot'],
            mood_bot=MoodType(result['mood_bot']) if result['mood_bot'] else MoodType.NORMAL,
            emotion_user=result['emotion_user'],
            arousal_user=result['arousal_user'],
            family_status=family_status,
            family_location=family_location,
            family_activity=result['family_activity'],
            family_estimate_return=result['family_estimate_return'],
            activity_bot=result['activity_bot'],
            activity_user=result['activity_user'],
            current_time=result['current_time'],
            time_override_history=time_override_history,
            updated_at=result['updated_at']
        )
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    async def get_registration_score(self, registration: Registration) -> float:
        """
        Hitung score registrasi untuk ranking
        
        Formula: (Total Chat × 0.3) + (Level × 0.4) + (Total Climax × 0.3)
        """
        total_chat_score = min(100, registration.total_chats) / 100
        level_score = registration.level / 12
        climax_score = min(50, registration.total_climax_bot + registration.total_climax_user) / 50
        
        score = (total_chat_score * 0.3) + (level_score * 0.4) + (climax_score * 0.3)
        return score * 100
    
    async def get_top_registrations(self, role: CharacterRole, limit: int = 10) -> List[Registration]:
        """Dapatkan top registrations berdasarkan score"""
        registrations = await self.get_user_registrations(0, role)  # user_id tidak dipakai
        
        # Hitung score dan sort
        scored = []
        for reg in registrations:
            score = await self.get_registration_score(reg)
            scored.append((reg, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [reg for reg, _ in scored[:limit]]
    
    async def cleanup_old_registrations(self):
        """Bersihkan registrasi lama (simpan top 10 per role)"""
        for role in CharacterRole:
            top = await self.get_top_registrations(role, 10)
            top_ids = [r.id for r in top]
            
            db = await self._get_db()
            await db.execute(
                """
                DELETE FROM registrations
                WHERE role = ? AND status != 'active' AND id NOT IN ({})
                """.format(','.join('?' * len(top_ids))),
                [role.value] + top_ids
            )
        
        logger.info("🧹 Cleaned up old registrations")


__all__ = ['Repository']
