# memory/long_term_memory.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Long-Term Memory - Milestone, Janji, Rencana, Preferensi
=============================================================================
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MemoryCategory(str, Enum):
    """Kategori memory jangka panjang"""
    MILESTONE = "milestone"
    PROMISE = "promise"
    PLAN = "plan"
    PREFERENCE_USER = "preference_user"
    PREFERENCE_BOT = "preference_bot"
    IMPORTANT_TOPIC = "important_topic"
    RELATIONSHIP = "relationship"


class MilestoneType(str, Enum):
    """Tipe milestone"""
    FIRST_KISS = "first_kiss"
    FIRST_INTIM = "first_intim"
    FIRST_CLIMAX = "first_climax"
    FIRST_DATE = "first_date"
    FIRST_FWB = "first_fwb"
    BECAME_PACAR = "became_pacar"
    SOUL_BOUNDED = "soul_bounded"
    AFTERCARE = "aftercare"


class PromiseStatus(str, Enum):
    """Status janji"""
    PENDING = "pending"
    FULFILLED = "fulfilled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class PlanStatus(str, Enum):
    """Status rencana"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LongTermMemory:
    """
    Long-term memory untuk menyimpan:
    - Milestone (momen penting)
    - Janji (promises)
    - Rencana (plans)
    - Preferensi user & bot
    - Topik penting
    """
    
    def __init__(self):
        # Memory storage
        self.milestones: List[Dict] = []
        self.promises: List[Dict] = []
        self.plans: List[Dict] = []
        self.user_preferences: Dict[str, List[str]] = {}
        self.bot_preferences: Dict[str, List[str]] = {}
        self.important_topics: List[Dict] = []
        self.relationship_milestones: List[Dict] = []
        
        # Maximum sizes
        self.max_milestones = 100
        self.max_promises = 50
        self.max_plans = 50
        self.max_topics = 100
        
        logger.info("✅ LongTermMemory initialized")
    
    # =========================================================================
    # MILESTONE
    # =========================================================================
    
    def add_milestone(
        self,
        milestone_type: MilestoneType,
        description: str,
        chat_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Tambah milestone baru
        
        Args:
            milestone_type: Tipe milestone
            description: Deskripsi milestone
            chat_id: ID chat saat milestone terjadi
            metadata: Metadata tambahan
        
        Returns:
            ID milestone
        """
        milestone_id = f"milestone_{int(time.time())}_{len(self.milestones)}"
        
        milestone = {
            'id': milestone_id,
            'type': milestone_type.value,
            'description': description,
            'timestamp': time.time(),
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'chat_id': chat_id,
            'metadata': metadata or {}
        }
        
        self.milestones.append(milestone)
        
        # Limit size
        if len(self.milestones) > self.max_milestones:
            self.milestones = self.milestones[-self.max_milestones:]
        
        logger.info(f"🏆 Added milestone: {milestone_type.value} - {description[:50]}")
        
        return milestone_id
    
    def get_milestone(self, milestone_type: Optional[MilestoneType] = None) -> Optional[Dict]:
        """
        Dapatkan milestone berdasarkan tipe
        
        Args:
            milestone_type: Tipe milestone (opsional)
        
        Returns:
            Milestone atau None
        """
        if milestone_type:
            for m in reversed(self.milestones):
                if m['type'] == milestone_type.value:
                    return m
        return self.milestones[-1] if self.milestones else None
    
    def get_all_milestones(self) -> List[Dict]:
        """Dapatkan semua milestone"""
        return self.milestones.copy()
    
    def has_milestone(self, milestone_type: MilestoneType) -> bool:
        """Cek apakah milestone sudah terjadi"""
        return any(m['type'] == milestone_type.value for m in self.milestones)
    
    # =========================================================================
    # PROMISES (JANJI)
    # =========================================================================
    
    def add_promise(
        self,
        text: str,
        from_user: bool = True,
        chat_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Tambah janji baru
        
        Args:
            text: Teks janji
            from_user: Apakah dari user (True) atau bot (False)
            chat_id: ID chat saat janji dibuat
            metadata: Metadata tambahan
        
        Returns:
            ID janji
        """
        promise_id = f"promise_{int(time.time())}_{len(self.promises)}"
        
        promise = {
            'id': promise_id,
            'text': text,
            'from_user': from_user,
            'status': PromiseStatus.PENDING.value,
            'created_at': time.time(),
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'chat_id': chat_id,
            'metadata': metadata or {}
        }
        
        self.promises.append(promise)
        
        # Limit size
        if len(self.promises) > self.max_promises:
            self.promises = self.promises[-self.max_promises:]
        
        logger.info(f"📝 Added promise: {text[:50]}")
        
        return promise_id
    
    def fulfill_promise(self, promise_id: str) -> bool:
        """
        Tandai janji sebagai fulfilled
        
        Args:
            promise_id: ID janji
        
        Returns:
            True jika berhasil
        """
        for promise in self.promises:
            if promise['id'] == promise_id and promise['status'] == PromiseStatus.PENDING.value:
                promise['status'] = PromiseStatus.FULFILLED.value
                promise['fulfilled_at'] = time.time()
                logger.info(f"✅ Promise fulfilled: {promise['text'][:50]}")
                return True
        return False
    
    def cancel_promise(self, promise_id: str) -> bool:
        """Batalkan janji"""
        for promise in self.promises:
            if promise['id'] == promise_id and promise['status'] == PromiseStatus.PENDING.value:
                promise['status'] = PromiseStatus.CANCELLED.value
                logger.info(f"❌ Promise cancelled: {promise['text'][:50]}")
                return True
        return False
    
    def get_pending_promises(self) -> List[Dict]:
        """Dapatkan janji yang pending"""
        return [p for p in self.promises if p['status'] == PromiseStatus.PENDING.value]
    
    def get_promises_by_status(self, status: PromiseStatus) -> List[Dict]:
        """Dapatkan janji berdasarkan status"""
        return [p for p in self.promises if p['status'] == status.value]
    
    # =========================================================================
    # PLANS (RENCANA)
    # =========================================================================
    
    def add_plan(
        self,
        text: str,
        planned_date: Optional[str] = None,
        chat_id: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Tambah rencana baru
        
        Args:
            text: Teks rencana
            planned_date: Tanggal rencana (opsional)
            chat_id: ID chat saat rencana dibuat
            metadata: Metadata tambahan
        
        Returns:
            ID rencana
        """
        plan_id = f"plan_{int(time.time())}_{len(self.plans)}"
        
        plan = {
            'id': plan_id,
            'text': text,
            'planned_date': planned_date,
            'status': PlanStatus.PENDING.value,
            'created_at': time.time(),
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'chat_id': chat_id,
            'metadata': metadata or {}
        }
        
        self.plans.append(plan)
        
        # Limit size
        if len(self.plans) > self.max_plans:
            self.plans = self.plans[-self.max_plans:]
        
        logger.info(f"📅 Added plan: {text[:50]}")
        
        return plan_id
    
    def complete_plan(self, plan_id: str) -> bool:
        """Tandai rencana sebagai completed"""
        for plan in self.plans:
            if plan['id'] == plan_id and plan['status'] == PlanStatus.PENDING.value:
                plan['status'] = PlanStatus.COMPLETED.value
                plan['completed_at'] = time.time()
                logger.info(f"✅ Plan completed: {plan['text'][:50]}")
                return True
        return False
    
    def get_pending_plans(self) -> List[Dict]:
        """Dapatkan rencana yang pending"""
        return [p for p in self.plans if p['status'] == PlanStatus.PENDING.value]
    
    # =========================================================================
    # PREFERENCES (PREFERENSI)
    # =========================================================================
    
    def add_user_preference(self, category: str, item: str):
        """
        Tambah preferensi user
        
        Args:
            category: Kategori (makanan, warna, aktivitas, dll)
            item: Item yang disukai
        """
        if category not in self.user_preferences:
            self.user_preferences[category] = []
        
        if item not in self.user_preferences[category]:
            self.user_preferences[category].append(item)
            logger.info(f"💖 Added user preference: {category} -> {item}")
    
    def add_bot_preference(self, category: str, item: str):
        """
        Tambah preferensi bot
        
        Args:
            category: Kategori
            item: Item yang disukai
        """
        if category not in self.bot_preferences:
            self.bot_preferences[category] = []
        
        if item not in self.bot_preferences[category]:
            self.bot_preferences[category].append(item)
            logger.info(f"🤖 Added bot preference: {category} -> {item}")
    
    def get_user_preferences(self) -> Dict[str, List[str]]:
        """Dapatkan semua preferensi user"""
        return self.user_preferences.copy()
    
    def get_bot_preferences(self) -> Dict[str, List[str]]:
        """Dapatkan semua preferensi bot"""
        return self.bot_preferences.copy()
    
    # =========================================================================
    # IMPORTANT TOPICS
    # =========================================================================
    
    def add_important_topic(
        self,
        topic: str,
        summary: str,
        chat_id: Optional[int] = None
    ):
        """
        Tambah topik penting
        
        Args:
            topic: Topik
            summary: Ringkasan
            chat_id: ID chat saat topik muncul
        """
        topic_data = {
            'topic': topic,
            'summary': summary,
            'timestamp': time.time(),
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'chat_id': chat_id
        }
        
        self.important_topics.append(topic_data)
        
        # Limit size
        if len(self.important_topics) > self.max_topics:
            self.important_topics = self.important_topics[-self.max_topics:]
        
        logger.info(f"📌 Added important topic: {topic}")
    
    def get_important_topics(self, limit: int = 10) -> List[Dict]:
        """Dapatkan topik penting terbaru"""
        return self.important_topics[-limit:]
    
    # =========================================================================
    # RELATIONSHIP MILESTONES
    # =========================================================================
    
    def add_relationship_milestone(
        self,
        milestone_type: str,
        description: str,
        chat_id: Optional[int] = None
    ):
        """
        Tambah milestone hubungan
        
        Args:
            milestone_type: Tipe milestone
            description: Deskripsi
            chat_id: ID chat
        """
        milestone = {
            'type': milestone_type,
            'description': description,
            'timestamp': time.time(),
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'chat_id': chat_id
        }
        
        self.relationship_milestones.append(milestone)
        
        logger.info(f"💕 Added relationship milestone: {milestone_type}")
    
    def get_relationship_timeline(self) -> List[Dict]:
        """Dapatkan timeline hubungan"""
        return sorted(self.relationship_milestones, key=lambda x: x['timestamp'])
    
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_milestones(self, limit: int = 5) -> str:
        """Format milestones untuk display"""
        if not self.milestones:
            return "Belum ada milestone"
        
        lines = ["🏆 **MILESTONE:**"]
        for m in self.milestones[-limit:]:
            time_str = datetime.fromtimestamp(m['timestamp']).strftime("%d %b")
            lines.append(f"• {time_str}: {m['description']}")
        
        return "\n".join(lines)
    
    def format_pending_promises(self) -> str:
        """Format janji pending untuk display"""
        promises = self.get_pending_promises()
        
        if not promises:
            return "Tidak ada janji yang tertunda"
        
        lines = ["📝 **JANJI YANG BELUM DITEPATI:**"]
        for p in promises:
            time_str = datetime.fromtimestamp(p['created_at']).strftime("%d %b")
            lines.append(f"• {time_str}: {p['text']}")
        
        return "\n".join(lines)
    
    def format_pending_plans(self) -> str:
        """Format rencana pending untuk display"""
        plans = self.get_pending_plans()
        
        if not plans:
            return "Tidak ada rencana yang tertunda"
        
        lines = ["📅 **RENCANA:**"]
        for p in plans:
            time_str = datetime.fromtimestamp(p['created_at']).strftime("%d %b")
            date_str = f" ({p['planned_date']})" if p['planned_date'] else ""
            lines.append(f"• {time_str}: {p['text']}{date_str}")
        
        return "\n".join(lines)
    
    def format_preferences(self) -> str:
        """Format preferensi untuk display"""
        if not self.user_preferences and not self.bot_preferences:
            return "Belum ada data preferensi"
        
        lines = ["💖 **PREFERENSI:**"]
        
        if self.user_preferences:
            lines.append("👤 User:")
            for cat, items in self.user_preferences.items():
                lines.append(f"   • {cat}: {', '.join(items)}")
        
        if self.bot_preferences:
            lines.append("🤖 Bot:")
            for cat, items in self.bot_preferences.items():
                lines.append(f"   • {cat}: {', '.join(items)}")
        
        return "\n".join(lines)
    
    def format_relationship_timeline(self) -> str:
        """Format timeline hubungan"""
        if not self.relationship_milestones:
            return "Belum ada momen spesial"
        
        lines = ["💕 **TIMELINE HUBUNGAN:**"]
        for m in self.relationship_milestones:
            time_str = datetime.fromtimestamp(m['timestamp']).strftime("%d %b %H:%M")
            lines.append(f"• {time_str}: {m['description']}")
        
        return "\n".join(lines)
    
    def get_all_memory(self) -> Dict:
        """Dapatkan semua memory dalam dictionary"""
        return {
            'milestones': self.milestones,
            'promises': self.promises,
            'plans': self.plans,
            'user_preferences': self.user_preferences,
            'bot_preferences': self.bot_preferences,
            'important_topics': self.important_topics,
            'relationship_milestones': self.relationship_milestones
        }
    
    def to_dict(self) -> Dict:
        """Konversi ke dictionary untuk database"""
        return {
            'milestones': json.dumps(self.milestones),
            'promises': json.dumps(self.promises),
            'plans': json.dumps(self.plans),
            'user_preferences': json.dumps(self.user_preferences),
            'bot_preferences': json.dumps(self.bot_preferences),
            'important_topics': json.dumps(self.important_topics),
            'relationship_milestones': json.dumps(self.relationship_milestones)
        }
    
    def from_dict(self, data: Dict):
        """Load dari dictionary"""
        if data.get('milestones'):
            self.milestones = json.loads(data['milestones'])
        if data.get('promises'):
            self.promises = json.loads(data['promises'])
        if data.get('plans'):
            self.plans = json.loads(data['plans'])
        if data.get('user_preferences'):
            self.user_preferences = json.loads(data['user_preferences'])
        if data.get('bot_preferences'):
            self.bot_preferences = json.loads(data['bot_preferences'])
        if data.get('important_topics'):
            self.important_topics = json.loads(data['important_topics'])
        if data.get('relationship_milestones'):
            self.relationship_milestones = json.loads(data['relationship_milestones'])
    
    def clear(self):
        """Clear semua memory"""
        self.milestones = []
        self.promises = []
        self.plans = []
        self.user_preferences = {}
        self.bot_preferences = {}
        self.important_topics = []
        self.relationship_milestones = []
        logger.info("Long-term memory cleared")


__all__ = [
    'LongTermMemory',
    'MemoryCategory',
    'MilestoneType',
    'PromiseStatus',
    'PlanStatus'
]
