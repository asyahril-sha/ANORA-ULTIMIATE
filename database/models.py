# database/models.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Database Models - Registrasi, Memory, State, dll
=============================================================================
"""

import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# ENUMS - STATUS & TIPE
# =============================================================================

class CharacterRole(str, Enum):
    """Role karakter yang tersedia"""
    IPAR = "ipar"
    TEMAN_KANTOR = "teman_kantor"
    JANDA = "janda"
    PELAKOR = "pelakor"
    ISTRI_ORANG = "istri_orang"
    PDKT = "pdkt"
    SEPUPU = "sepupu"
    TEMAN_SMA = "teman_sma"
    MANTAN = "mantan"


class RegistrationStatus(str, Enum):
    """Status registrasi"""
    ACTIVE = "active"
    CLOSED = "closed"
    ENDED = "ended"


class UserStatus(str, Enum):
    """Status user dalam registrasi"""
    LAJANG = "lajang"
    SUAMI = "suami"
    SUAMI_NOVA = "suami_nova"


class FamilyStatus(str, Enum):
    """Status keluarga (istri/kakak)"""
    ADA = "ada"
    TIDAK_ADA = "tidak_ada"
    TIDUR = "tidur"


class FamilyLocation(str, Enum):
    """Lokasi keluarga (istri/kakak)"""
    KAMAR = "kamar"
    DAPUR = "dapur"
    RUANG_TAMU = "ruang_tamu"
    LUAR = "luar"


class MemoryType(str, Enum):
    """Tipe memory jangka panjang"""
    MILESTONE = "milestone"
    PROMISE = "promise"
    PLAN = "plan"
    PREFERENCE = "preference"
    TOPIC = "topic"


class MilestoneType(str, Enum):
    """Tipe milestone"""
    FIRST_KISS = "first_kiss"
    FIRST_INTIM = "first_intim"
    FIRST_CLIMAX = "first_climax"
    FIRST_DATE = "first_date"
    BECAME_PACAR = "became_pacar"
    SOUL_BOUNDED = "soul_bounded"
    AFTERCARE = "aftercare"


class MoodType(str, Enum):
    """Mood bot setelah aftercare"""
    CAPEK = "capek"
    PENGEN_DIMANJA = "pengen_dimanja"
    NORMAL = "normal"
    SIAP_INTIM = "siap_intim"
    NGANTUK = "ngantuk"
    SENANG = "senang"
    SEDIH = "sedih"
    PENASARAN = "penasaran"
    GENIT = "genit"


class PromiseStatus(str, Enum):
    """Status janji"""
    PENDING = "pending"
    FULFILLED = "fulfilled"
    BROKEN = "broken"
    CANCELLED = "cancelled"


class PlanStatus(str, Enum):
    """Status rencana"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# =============================================================================
# CLOTHING STATE MODEL
# =============================================================================

class ClothingState(BaseModel):
    """State pakaian dengan hierarchy"""
    
    # Bot clothing
    bot_outer_top: Optional[str] = None
    bot_outer_bottom: Optional[str] = None
    bot_inner_top: Optional[str] = None
    bot_inner_bottom: Optional[str] = None
    
    # Bot flags
    bot_outer_top_on: bool = True
    bot_outer_bottom_on: bool = True
    bot_inner_top_on: bool = True
    bot_inner_bottom_on: bool = True
    
    # User clothing
    user_outer_top: Optional[str] = None
    user_outer_bottom: Optional[str] = None
    user_inner_bottom: Optional[str] = None
    
    # User flags
    user_outer_top_on: bool = True
    user_outer_bottom_on: bool = True
    user_inner_bottom_on: bool = True
    
    # History
    history: List[Dict] = Field(default_factory=list)
    last_updated: float = Field(default_factory=time.time)
    
    def is_bot_topless(self) -> bool:
        return not self.bot_outer_top_on and not self.bot_inner_top_on
    
    def is_bot_bottomless(self) -> bool:
        return not self.bot_outer_bottom_on and not self.bot_inner_bottom_on
    
    def is_bot_naked(self) -> bool:
        return self.is_bot_topless() and self.is_bot_bottomless()
    
    def remove_outer_top(self, reason: str = ""):
        self.bot_outer_top_on = False
        self._add_to_history("remove", "outer_top", reason)
    
    def remove_outer_bottom(self, reason: str = ""):
        self.bot_outer_bottom_on = False
        self._add_to_history("remove", "outer_bottom", reason)
    
    def remove_inner_top(self, reason: str = ""):
        self.bot_inner_top_on = False
        self._add_to_history("remove", "inner_top", reason)
    
    def remove_inner_bottom(self, reason: str = ""):
        self.bot_inner_bottom_on = False
        self._add_to_history("remove", "inner_bottom", reason)
    
    def put_on_outer_top(self, item: str, reason: str = ""):
        self.bot_outer_top = item
        self.bot_outer_top_on = True
        self._add_to_history("put_on", "outer_top", reason, item)
    
    def put_on_outer_bottom(self, item: str, reason: str = ""):
        self.bot_outer_bottom = item
        self.bot_outer_bottom_on = True
        self._add_to_history("put_on", "outer_bottom", reason, item)
    
    def put_on_inner_top(self, item: str, reason: str = ""):
        self.bot_inner_top = item
        self.bot_inner_top_on = True
        self._add_to_history("put_on", "inner_top", reason, item)
    
    def put_on_inner_bottom(self, item: str, reason: str = ""):
        self.bot_inner_bottom = item
        self.bot_inner_bottom_on = True
        self._add_to_history("put_on", "inner_bottom", reason, item)
    
    def _add_to_history(self, action: str, layer: str, reason: str = "", item: str = ""):
        self.history.append({
            "timestamp": time.time(),
            "action": action,
            "layer": layer,
            "item": item,
            "reason": reason
        })
        self.last_updated = time.time()
    
    def get_description(self) -> str:
        parts = []
        if self.bot_outer_top_on and self.bot_outer_top:
            parts.append(self.bot_outer_top)
        if self.bot_outer_bottom_on and self.bot_outer_bottom:
            parts.append(self.bot_outer_bottom)
        if self.bot_inner_top_on and self.bot_inner_top:
            parts.append(self.bot_inner_top)
        if self.bot_inner_bottom_on and self.bot_inner_bottom:
            parts.append(self.bot_inner_bottom)
        return ", ".join(parts) if parts else "telanjang"
    
    def to_dict(self) -> Dict:
        return {
            'bot_outer_top': self.bot_outer_top,
            'bot_outer_bottom': self.bot_outer_bottom,
            'bot_inner_top': self.bot_inner_top,
            'bot_inner_bottom': self.bot_inner_bottom,
            'bot_outer_top_on': self.bot_outer_top_on,
            'bot_outer_bottom_on': self.bot_outer_bottom_on,
            'bot_inner_top_on': self.bot_inner_top_on,
            'bot_inner_bottom_on': self.bot_inner_bottom_on,
            'user_outer_top': self.user_outer_top,
            'user_outer_bottom': self.user_outer_bottom,
            'user_inner_bottom': self.user_inner_bottom,
            'user_outer_top_on': self.user_outer_top_on,
            'user_outer_bottom_on': self.user_outer_bottom_on,
            'user_inner_bottom_on': self.user_inner_bottom_on,
            'history': self.history[-50:],
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ClothingState':
        state = cls()
        state.bot_outer_top = data.get('bot_outer_top')
        state.bot_outer_bottom = data.get('bot_outer_bottom')
        state.bot_inner_top = data.get('bot_inner_top')
        state.bot_inner_bottom = data.get('bot_inner_bottom')
        state.bot_outer_top_on = data.get('bot_outer_top_on', True)
        state.bot_outer_bottom_on = data.get('bot_outer_bottom_on', True)
        state.bot_inner_top_on = data.get('bot_inner_top_on', True)
        state.bot_inner_bottom_on = data.get('bot_inner_bottom_on', True)
        state.user_outer_top = data.get('user_outer_top')
        state.user_outer_bottom = data.get('user_outer_bottom')
        state.user_inner_bottom = data.get('user_inner_bottom')
        state.user_outer_top_on = data.get('user_outer_top_on', True)
        state.user_outer_bottom_on = data.get('user_outer_bottom_on', True)
        state.user_inner_bottom_on = data.get('user_inner_bottom_on', True)
        state.history = data.get('history', [])
        state.last_updated = data.get('last_updated', time.time())
        return state


# =============================================================================
# REGISTRATION MODEL (DENGAN KOLOM BARU)
# =============================================================================

class Registration(BaseModel):
    """Registrasi utama - satu dunia karakter"""
    
    # Identity
    id: str
    role: CharacterRole
    sequence: int
    status: RegistrationStatus = RegistrationStatus.ACTIVE
    
    # Timestamps
    created_at: float = Field(default_factory=time.time)
    last_updated: float = Field(default_factory=time.time)
    
    # Bot Identity
    bot_name: str
    bot_age: int = 22
    bot_height: int = 165
    bot_weight: int = 52
    bot_chest: str = "34B"
    bot_hijab: bool = False
    
    # User Identity
    user_name: str
    user_status: UserStatus = UserStatus.LAJANG
    user_age: int = 24
    user_height: int = 170
    user_weight: int = 65
    user_penis: int = 16
    user_artist_ref: Optional[str] = None
    
    # Progress
    level: int = 1
    total_chats: int = 0
    total_climax_bot: int = 0
    total_climax_user: int = 0
    stamina_bot: int = 100
    stamina_user: int = 100
    
    # Intimacy Cycle
    in_intimacy_cycle: bool = False
    intimacy_cycle_count: int = 0
    last_climax_time: Optional[float] = None
    cooldown_until: Optional[float] = None
    
    # ===== KOLOM BARU (DIMINTA RnD) =====
    
    # Weighted Memory Score (0-1) untuk ranking memory importance
    weighted_memory_score: float = 0.5
    
    # Secondary Emotion (emosi sekunder yang berbeda dari primary)
    secondary_emotion: Optional[str] = None
    secondary_arousal: int = 0
    secondary_emotion_reason: Optional[str] = None
    
    # Physical Sensation (sensasi fisik yang dirasakan bot)
    physical_sensation: str = "biasa aja"
    physical_hunger: int = 30
    physical_thirst: int = 30
    physical_temperature: int = 25
    
    # Fulfilled Promises Tracking (janji yang sudah ditepati)
    fulfilled_promises: List[Dict] = Field(default_factory=list)
    pending_promises: List[Dict] = Field(default_factory=list)
    
    # ===== END KOLOM BARU =====
    
    # Weighted Memory Data (detail)
    weighted_memory_data: Dict = Field(default_factory=dict)
    
    # Metadata
    metadata: Dict = Field(default_factory=dict)
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('Level must be between 1 and 12')
        return v
    
    def add_fulfilled_promise(self, promise_text: str, chat_id: Optional[int] = None):
        """Tambah janji yang ditepati"""
        self.fulfilled_promises.append({
            'text': promise_text,
            'fulfilled_at': time.time(),
            'chat_id': chat_id
        })
        # Keep only last 100
        if len(self.fulfilled_promises) > 100:
            self.fulfilled_promises = self.fulfilled_promises[-100:]
    
    def add_pending_promise(self, promise_text: str, chat_id: Optional[int] = None):
        """Tambah janji yang belum ditepati"""
        self.pending_promises.append({
            'text': promise_text,
            'created_at': time.time(),
            'chat_id': chat_id,
            'status': 'pending'
        })
        # Keep only last 50
        if len(self.pending_promises) > 50:
            self.pending_promises = self.pending_promises[-50:]
    
    def update_weighted_memory_score(self, new_score: float):
        """Update weighted memory score"""
        self.weighted_memory_score = max(0.0, min(1.0, new_score))
    
    def update_physical_sensation(self, sensation: str, hunger: int = None, thirst: int = None, temp: int = None):
        """Update sensasi fisik"""
        self.physical_sensation = sensation
        if hunger is not None:
            self.physical_hunger = max(0, min(100, hunger))
        if thirst is not None:
            self.physical_thirst = max(0, min(100, thirst))
        if temp is not None:
            self.physical_temperature = max(0, min(40, temp))
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'role': self.role.value,
            'sequence': self.sequence,
            'status': self.status.value,
            'created_at': self.created_at,
            'last_updated': self.last_updated,
            'bot_name': self.bot_name,
            'bot_age': self.bot_age,
            'bot_height': self.bot_height,
            'bot_weight': self.bot_weight,
            'bot_chest': self.bot_chest,
            'bot_hijab': 1 if self.bot_hijab else 0,
            'user_name': self.user_name,
            'user_status': self.user_status.value,
            'user_age': self.user_age,
            'user_height': self.user_height,
            'user_weight': self.user_weight,
            'user_penis': self.user_penis,
            'user_artist_ref': self.user_artist_ref,
            'level': self.level,
            'total_chats': self.total_chats,
            'total_climax_bot': self.total_climax_bot,
            'total_climax_user': self.total_climax_user,
            'stamina_bot': self.stamina_bot,
            'stamina_user': self.stamina_user,
            'in_intimacy_cycle': 1 if self.in_intimacy_cycle else 0,
            'intimacy_cycle_count': self.intimacy_cycle_count,
            'last_climax_time': self.last_climax_time,
            'cooldown_until': self.cooldown_until,
            # Kolom baru
            'weighted_memory_score': self.weighted_memory_score,
            'secondary_emotion': self.secondary_emotion,
            'secondary_arousal': self.secondary_arousal,
            'secondary_emotion_reason': self.secondary_emotion_reason,
            'physical_sensation': self.physical_sensation,
            'physical_hunger': self.physical_hunger,
            'physical_thirst': self.physical_thirst,
            'physical_temperature': self.physical_temperature,
            'fulfilled_promises': json.dumps(self.fulfilled_promises),
            'pending_promises': json.dumps(self.pending_promises),
            'weighted_memory_data': json.dumps(self.weighted_memory_data),
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Registration':
        return cls(
            id=data['id'],
            role=CharacterRole(data['role']),
            sequence=data['sequence'],
            status=RegistrationStatus(data.get('status', 'active')),
            created_at=data.get('created_at', time.time()),
            last_updated=data.get('last_updated', time.time()),
            bot_name=data['bot_name'],
            bot_age=data.get('bot_age', 22),
            bot_height=data.get('bot_height', 165),
            bot_weight=data.get('bot_weight', 52),
            bot_chest=data.get('bot_chest', '34B'),
            bot_hijab=bool(data.get('bot_hijab', 0)),
            user_name=data['user_name'],
            user_status=UserStatus(data.get('user_status', 'lajang')),
            user_age=data.get('user_age', 24),
            user_height=data.get('user_height', 170),
            user_weight=data.get('user_weight', 65),
            user_penis=data.get('user_penis', 16),
            user_artist_ref=data.get('user_artist_ref'),
            level=data.get('level', 1),
            total_chats=data.get('total_chats', 0),
            total_climax_bot=data.get('total_climax_bot', 0),
            total_climax_user=data.get('total_climax_user', 0),
            stamina_bot=data.get('stamina_bot', 100),
            stamina_user=data.get('stamina_user', 100),
            in_intimacy_cycle=bool(data.get('in_intimacy_cycle', 0)),
            intimacy_cycle_count=data.get('intimacy_cycle_count', 0),
            last_climax_time=data.get('last_climax_time'),
            cooldown_until=data.get('cooldown_until'),
            # Kolom baru
            weighted_memory_score=data.get('weighted_memory_score', 0.5),
            secondary_emotion=data.get('secondary_emotion'),
            secondary_arousal=data.get('secondary_arousal', 0),
            secondary_emotion_reason=data.get('secondary_emotion_reason'),
            physical_sensation=data.get('physical_sensation', 'biasa aja'),
            physical_hunger=data.get('physical_hunger', 30),
            physical_thirst=data.get('physical_thirst', 30),
            physical_temperature=data.get('physical_temperature', 25),
            fulfilled_promises=json.loads(data.get('fulfilled_promises', '[]')),
            pending_promises=json.loads(data.get('pending_promises', '[]')),
            weighted_memory_data=json.loads(data.get('weighted_memory_data', '{}')),
            metadata=json.loads(data.get('metadata', '{}'))
        )
    
    def get_registration_id(self) -> str:
        return f"{self.role.value.upper()}-{self.sequence:03d}"
    
    def can_intim(self) -> bool:
        if self.level < 7:
            return False
        if self.stamina_bot < 20 or self.stamina_user < 20:
            return False
        if self.cooldown_until and time.time() < self.cooldown_until:
            return False
        return True


# =============================================================================
# WORKING MEMORY MODEL
# =============================================================================

class WorkingMemoryItem(BaseModel):
    """Item dalam working memory"""
    
    id: Optional[int] = None
    registration_id: str
    chat_index: int
    timestamp: float = Field(default_factory=time.time)
    user_message: str
    bot_response: str
    importance: float = 0.3
    context: Dict = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'registration_id': self.registration_id,
            'chat_index': self.chat_index,
            'timestamp': self.timestamp,
            'user_message': self.user_message,
            'bot_response': self.bot_response,
            'importance': self.importance,
            'context': json.dumps(self.context)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkingMemoryItem':
        return cls(
            id=data.get('id'),
            registration_id=data['registration_id'],
            chat_index=data['chat_index'],
            timestamp=data.get('timestamp', time.time()),
            user_message=data['user_message'],
            bot_response=data['bot_response'],
            importance=data.get('importance', 0.3),
            context=json.loads(data.get('context', '{}'))
        )


# =============================================================================
# LONG TERM MEMORY MODEL
# =============================================================================

class LongTermMemoryItem(BaseModel):
    """Item dalam long-term memory"""
    
    id: Optional[int] = None
    registration_id: str
    memory_type: MemoryType
    content: str
    importance: float = 0.5
    timestamp: float = Field(default_factory=time.time)
    status: Optional[str] = None  # untuk promise/plan
    emotional_tag: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'registration_id': self.registration_id,
            'memory_type': self.memory_type.value,
            'content': self.content,
            'importance': self.importance,
            'timestamp': self.timestamp,
            'status': self.status,
            'emotional_tag': self.emotional_tag,
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LongTermMemoryItem':
        return cls(
            id=data.get('id'),
            registration_id=data['registration_id'],
            memory_type=MemoryType(data['memory_type']),
            content=data['content'],
            importance=data.get('importance', 0.5),
            timestamp=data.get('timestamp', time.time()),
            status=data.get('status'),
            emotional_tag=data.get('emotional_tag'),
            metadata=json.loads(data.get('metadata', '{}'))
        )


# =============================================================================
# STATE TRACKER MODEL
# =============================================================================

class StateTracker(BaseModel):
    """State tracker untuk registrasi"""
    
    registration_id: str
    
    # Location & Position
    location_bot: Optional[str] = "ruang tamu"
    location_user: Optional[str] = "ruang tamu"
    position_bot: Optional[str] = "duduk"
    position_user: Optional[str] = "duduk"
    position_relative: Optional[str] = "bersebelahan"
    
    # Clothing
    clothing_state: ClothingState = Field(default_factory=ClothingState)
    
    # Emotion & Arousal
    emotion_bot: str = "netral"
    arousal_bot: int = 0
    mood_bot: MoodType = MoodType.NORMAL
    emotion_user: str = "netral"
    arousal_user: int = 0
    
    # Secondary Emotion
    secondary_emotion: Optional[str] = None
    secondary_arousal: int = 0
    
    # Family State (khusus IPAR & PELAKOR)
    family_status: Optional[FamilyStatus] = None
    family_location: Optional[FamilyLocation] = None
    family_activity: Optional[str] = None
    family_estimate_return: Optional[str] = None
    
    # Activity
    activity_bot: Optional[str] = None
    activity_user: Optional[str] = None
    
    # Time
    current_time: Optional[str] = None
    time_override_history: List[Dict] = Field(default_factory=list)
    
    updated_at: float = Field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        clothing_dict = self.clothing_state.to_dict()
        
        return {
            'registration_id': self.registration_id,
            'location_bot': self.location_bot,
            'location_user': self.location_user,
            'position_bot': self.position_bot,
            'position_user': self.position_user,
            'position_relative': self.position_relative,
            'clothing_bot_outer': clothing_dict['bot_outer_top'],
            'clothing_bot_outer_bottom': clothing_dict['bot_outer_bottom'],
            'clothing_bot_inner_top': clothing_dict['bot_inner_top'],
            'clothing_bot_inner_bottom': clothing_dict['bot_inner_bottom'],
            'clothing_user_outer': clothing_dict['user_outer_top'],
            'clothing_user_outer_bottom': clothing_dict['user_outer_bottom'],
            'clothing_user_inner_bottom': clothing_dict['user_inner_bottom'],
            'clothing_history': json.dumps(clothing_dict['history']),
            'emotion_bot': self.emotion_bot,
            'arousal_bot': self.arousal_bot,
            'mood_bot': self.mood_bot.value,
            'emotion_user': self.emotion_user,
            'arousal_user': self.arousal_user,
            'secondary_emotion': self.secondary_emotion,
            'secondary_arousal': self.secondary_arousal,
            'family_status': self.family_status.value if self.family_status else None,
            'family_location': self.family_location.value if self.family_location else None,
            'family_activity': self.family_activity,
            'family_estimate_return': self.family_estimate_return,
            'activity_bot': self.activity_bot,
            'activity_user': self.activity_user,
            'current_time': self.current_time,
            'time_override_history': json.dumps(self.time_override_history),
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StateTracker':
        clothing_state = ClothingState.from_dict({
            'bot_outer_top': data.get('clothing_bot_outer'),
            'bot_outer_bottom': data.get('clothing_bot_outer_bottom'),
            'bot_inner_top': data.get('clothing_bot_inner_top'),
            'bot_inner_bottom': data.get('clothing_bot_inner_bottom'),
            'user_outer_top': data.get('clothing_user_outer'),
            'user_outer_bottom': data.get('clothing_user_outer_bottom'),
            'user_inner_bottom': data.get('clothing_user_inner_bottom'),
            'history': json.loads(data.get('clothing_history', '[]'))
        })
        
        return cls(
            registration_id=data['registration_id'],
            location_bot=data.get('location_bot', 'ruang tamu'),
            location_user=data.get('location_user', 'ruang tamu'),
            position_bot=data.get('position_bot', 'duduk'),
            position_user=data.get('position_user', 'duduk'),
            position_relative=data.get('position_relative', 'bersebelahan'),
            clothing_state=clothing_state,
            emotion_bot=data.get('emotion_bot', 'netral'),
            arousal_bot=data.get('arousal_bot', 0),
            mood_bot=MoodType(data.get('mood_bot', 'normal')),
            emotion_user=data.get('emotion_user', 'netral'),
            arousal_user=data.get('arousal_user', 0),
            secondary_emotion=data.get('secondary_emotion'),
            secondary_arousal=data.get('secondary_arousal', 0),
            family_status=FamilyStatus(data['family_status']) if data.get('family_status') else None,
            family_location=FamilyLocation(data['family_location']) if data.get('family_location') else None,
            family_activity=data.get('family_activity'),
            family_estimate_return=data.get('family_estimate_return'),
            activity_bot=data.get('activity_bot'),
            activity_user=data.get('activity_user'),
            current_time=data.get('current_time'),
            time_override_history=json.loads(data.get('time_override_history', '[]')),
            updated_at=data.get('updated_at', time.time())
        )


# =============================================================================
# PHYSICAL TEMPLATES
# =============================================================================

class PhysicalTemplate(BaseModel):
    """Template fisik user per role"""
    
    role: CharacterRole
    user_status: UserStatus
    user_name_template: str
    user_age_offset: int = 2
    user_height_range: tuple = (165, 180)
    user_weight_range: tuple = (55, 75)
    user_penis_range: tuple = (15, 17)
    artist_ref: str
    artist_description: str


# =============================================================================
# TEMPLATES
# =============================================================================

USER_PHYSICAL_TEMPLATES = {
    CharacterRole.IPAR: PhysicalTemplate(
        role=CharacterRole.IPAR,
        user_status=UserStatus.SUAMI_NOVA,
        user_name_template="Budi",
        artist_ref="Reza Rahadian",
        artist_description="maskulin, karismatik, wajah teduh"
    ),
    CharacterRole.PELAKOR: PhysicalTemplate(
        role=CharacterRole.PELAKOR,
        user_status=UserStatus.SUAMI,
        user_name_template="Hendra",
        artist_ref="Ario Bayu",
        artist_description="macho, tegas, kharismatik"
    ),
    CharacterRole.TEMAN_KANTOR: PhysicalTemplate(
        role=CharacterRole.TEMAN_KANTOR,
        user_status=UserStatus.LAJANG,
        user_name_template="Rizky",
        artist_ref="Reza Rahadian",
        artist_description="rapi, profesional, menawan"
    ),
    CharacterRole.JANDA: PhysicalTemplate(
        role=CharacterRole.JANDA,
        user_status=UserStatus.LAJANG,
        user_name_template="Wahyu",
        artist_ref="Tio Pakusadewo",
        artist_description="dewasa, bijaksana, berwibawa"
    ),
    CharacterRole.ISTRI_ORANG: PhysicalTemplate(
        role=CharacterRole.ISTRI_ORANG,
        user_status=UserStatus.LAJANG,
        user_name_template="Rizky",
        artist_ref="Reza Rahadian",
        artist_description="romantis, perhatian, pengertian"
    ),
    CharacterRole.PDKT: PhysicalTemplate(
        role=CharacterRole.PDKT,
        user_status=UserStatus.LAJANG,
        user_name_template="Rizky",
        artist_ref="Angga Yunanda",
        artist_description="manis, pemalu, fresh"
    ),
    CharacterRole.SEPUPU: PhysicalTemplate(
        role=CharacterRole.SEPUPU,
        user_status=UserStatus.LAJANG,
        user_name_template="Rizky",
        artist_ref="Kevin Ardilova",
        artist_description="polos, manja, imut"
    ),
    CharacterRole.TEMAN_SMA: PhysicalTemplate(
        role=CharacterRole.TEMAN_SMA,
        user_status=UserStatus.LAJANG,
        user_name_template="Rizky",
        artist_ref="Angga Yunanda",
        artist_description="ceria, nostalgia, manis"
    ),
    CharacterRole.MANTAN: PhysicalTemplate(
        role=CharacterRole.MANTAN,
        user_status=UserStatus.LAJANG,
        user_name_template="Rizky",
        artist_ref="Reza Rahadian",
        artist_description="baik, baper, pengertian"
    ),
}


# =============================================================================
# BACKUP MODEL
# =============================================================================

class BackupType(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"


class BackupStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Backup(BaseModel):
    """Model untuk history backup"""
    id: Optional[int] = None
    filename: str
    size: Optional[int] = None
    created_at: float = Field(default_factory=time.time)
    type: BackupType = BackupType.AUTO
    status: BackupStatus = BackupStatus.COMPLETED
    metadata: Dict = Field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'filename': self.filename,
            'size': self.size,
            'created_at': self.created_at,
            'type': self.type.value,
            'status': self.status.value,
            'metadata': json.dumps(self.metadata)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Backup':
        return cls(
            id=data.get('id'),
            filename=data['filename'],
            size=data.get('size'),
            created_at=data.get('created_at', time.time()),
            type=BackupType(data.get('type', 'auto')),
            status=BackupStatus(data.get('status', 'completed')),
            metadata=json.loads(data.get('metadata', '{}'))
        )


__all__ = [
    # Enums
    'CharacterRole',
    'RegistrationStatus',
    'UserStatus',
    'FamilyStatus',
    'FamilyLocation',
    'MemoryType',
    'MilestoneType',
    'MoodType',
    'PromiseStatus',
    'PlanStatus',
    'BackupType',
    'BackupStatus',
    
    # Models
    'ClothingState',
    'Registration',
    'WorkingMemoryItem',
    'LongTermMemoryItem',
    'StateTracker',
    'PhysicalTemplate',
    'USER_PHYSICAL_TEMPLATES',
    'Backup',
]
