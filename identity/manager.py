# identity/manager.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Identity Manager - Multi-Identity System
=============================================================================
"""

import time
import random
import json
import logging
from typing import Dict, List, Optional, Any

from database.repository import Repository
from database.models import CharacterRole, RegistrationStatus, StateTracker, ClothingState
from .registration import CharacterRegistration, CharacterStatus
from .bot_identity import BotIdentity
from .user_identity import UserIdentity

logger = logging.getLogger(__name__)


class IdentityManager:
    """
    Manager untuk multi-identity system
    Semua operasi via bot/user object (bukan field terpisah)
    """
    
    def __init__(self):
        self.repo = Repository()
        self._current_registration: Optional[CharacterRegistration] = None
        self._active_session: Optional[str] = None
    
    # =========================================================================
    # REGISTRATION MANAGEMENT
    # =========================================================================
    
    async def create_character(
        self,
        role: CharacterRole,
        user_name: Optional[str] = None,
        bot_name: Optional[str] = None
    ) -> CharacterRegistration:
        """Buat karakter baru"""
        sequence = await self.repo.get_next_sequence(role)
        registration = CharacterRegistration.create_new(
            role=role,
            sequence=sequence,
            user_name=user_name,
            bot_name=bot_name
        )
        
        db_reg = registration.to_db_registration()
        await self.repo.create_registration(db_reg)
        
        # Create initial state tracker
        state = StateTracker(
            registration_id=registration.id,
            location_bot="ruang tamu",
            location_user="ruang tamu",
            position_bot="duduk",
            position_user="duduk",
            position_relative="bersebelahan",
            clothing_state=ClothingState(),
            current_time=self._get_initial_time()
        )
        await self.repo.save_state(state)
        
        logger.info(f"✅ Created new character: {registration.id}")
        return registration
    
    async def get_character(self, registration_id: str) -> Optional[CharacterRegistration]:
        """Dapatkan karakter berdasarkan ID"""
        db_reg = await self.repo.get_registration(registration_id)
        if not db_reg:
            return None
        return CharacterRegistration.from_db_registration(db_reg)
    
    async def get_all_characters(self, role: Optional[CharacterRole] = None) -> List[CharacterRegistration]:
        """Dapatkan semua karakter"""
        db_regs = await self.repo.get_user_registrations(0, role)
        characters = []
        for db_reg in db_regs:
            characters.append(CharacterRegistration.from_db_registration(db_reg))
        characters.sort(key=lambda x: x.last_updated, reverse=True)
        return characters
    
    async def get_active_character(self) -> Optional[CharacterRegistration]:
        """Dapatkan karakter aktif"""
        if self._current_registration:
            return await self.get_character(self._current_registration.id)
        return None
    
    async def switch_character(self, registration_id: str) -> Optional[CharacterRegistration]:
        """Switch ke karakter lain"""
        character = await self.get_character(registration_id)
        if not character:
            return None
        if self._current_registration:
            await self.close_current_session()
        self._current_registration = character
        self._active_session = character.id
        logger.info(f"🔄 Switched to character: {character.id}")
        return character
    
    async def close_current_session(self):
        """Tutup session saat ini"""
        if self._current_registration:
            self._current_registration.status = CharacterStatus.CLOSED
            self._current_registration.last_updated = time.time()
            db_reg = self._current_registration.to_db_registration()
            await self.repo.update_registration(db_reg)
            self._current_registration = None
            self._active_session = None
            logger.info("📁 Closed current session")
    
    async def end_character(self, registration_id: str) -> bool:
        """Akhiri karakter (hapus permanen)"""
        if self._active_session == registration_id:
            await self.close_current_session()
        await self.repo.delete_registration(registration_id)
        logger.info(f"💔 Ended character: {registration_id}")
        return True
    
    # =========================================================================
    # CHARACTER STATE UPDATE (VIA BOT/USER OBJECT)
    # =========================================================================
    
    async def update_character_emotion(
        self, 
        registration_id: str, 
        emotion: str, 
        arousal_delta: int = 0
    ) -> bool:
        """Update emosi karakter (via bot object)"""
        character = await self.get_character(registration_id)
        if not character:
            return False
        
        character.bot.emotion = emotion
        character.bot.arousal = max(0, min(100, character.bot.arousal + arousal_delta))
        character.last_updated = time.time()
        
        await self.repo.update_registration(character.to_db_registration())
        return True
    
    async def update_character_stamina(
        self,
        registration_id: str,
        bot_delta: int = 0,
        user_delta: int = 0
    ) -> bool:
        """Update stamina karakter (via bot/user object)"""
        character = await self.get_character(registration_id)
        if not character:
            return False
        
        character.bot.stamina = max(0, min(100, character.bot.stamina + bot_delta))
        character.user.stamina = max(0, min(100, character.user.stamina + user_delta))
        character.last_updated = time.time()
        
        await self.repo.update_registration(character.to_db_registration())
        return True
    
    async def record_climax(self, registration_id: str, is_bot: bool = True) -> bool:
        """Rekam climax (via bot/user object)"""
        character = await self.get_character(registration_id)
        if not character:
            return False
        
        if is_bot:
            character.bot.record_climax()
        else:
            character.user.record_climax()
        
        character.last_climax_time = time.time()
        character.cooldown_until = time.time() + (3 * 3600)
        character.last_updated = time.time()
        
        await self.repo.update_registration(character.to_db_registration())
        return True
    
    # =========================================================================
    # STATE TRACKER
    # =========================================================================
    
    async def get_character_state(self, registration_id: str) -> Optional[Dict]:
        """Dapatkan state tracker (lokasi, posisi, pakaian)"""
        state = await self.repo.load_state(registration_id)
        if not state:
            return None
        
        return {
            'location_bot': state.location_bot,
            'location_user': state.location_user,
            'position_bot': state.position_bot,
            'position_user': state.position_user,
            'position_relative': state.position_relative,
            'clothing_state': state.clothing_state.to_dict() if state.clothing_state else {},
            'family_status': state.family_status.value if state.family_status else None,
            'family_location': state.family_location.value if state.family_location else None,
            'activity_bot': state.activity_bot,
            'activity_user': state.activity_user,
            'current_time': state.current_time,
            'updated_at': state.updated_at
        }
    
    async def update_character_state(self, registration_id: str, updates: Dict):
        """Update state tracker"""
        state = await self.repo.load_state(registration_id)
        if not state:
            from database.models import StateTracker
            state = StateTracker(registration_id=registration_id)
        
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)
        
        if 'clothing_state' in updates:
            clothing_data = updates['clothing_state']
            if isinstance(clothing_data, dict):
                for k, v in clothing_data.items():
                    if hasattr(state.clothing_state, k):
                        setattr(state.clothing_state, k, v)
        
        state.updated_at = time.time()
        await self.repo.save_state(state)
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def _get_initial_time(self) -> str:
        """Dapatkan waktu awal random"""
        times = ["08:00", "12:00", "16:00", "20:00"]
        return random.choice(times)
    
    async def get_registration_stats(self) -> Dict:
        """Dapatkan statistik registrasi"""
        characters = await self.get_all_characters()
        
        total = len(characters)
        by_role = {}
        active = 0
        total_chats = 0
        total_climax = 0
        
        for c in characters:
            role_name = c.role.value
            by_role[role_name] = by_role.get(role_name, 0) + 1
            if c.status == CharacterStatus.ACTIVE:
                active += 1
            total_chats += c.total_chats
            total_climax += c.bot.total_climax + c.user.total_climax
        
        return {
            "total_characters": total,
            "active_characters": active,
            "by_role": by_role,
            "total_chats_all_time": total_chats,
            "total_climax_all_time": total_climax,
            "top_character": max(characters, key=lambda x: x.get_score()) if characters else None
        }


__all__ = ['IdentityManager']
