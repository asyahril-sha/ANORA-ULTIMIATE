# tracking/promises.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Promises & Plans Tracking - Tracking Janji dan Rencana
Target Realism 9.9/10
=============================================================================
"""

import time
import re
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class PromiseStatus(str, Enum):
    """Status janji"""
    PENDING = "pending"
    FULFILLED = "fulfilled"
    BROKEN = "broken"
    CANCELLED = "cancelled"
    REMINDED = "reminded"  # sudah diingatkan


class PlanStatus(str, Enum):
    """Status rencana"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    UPCOMING = "upcoming"


class PromiseType(str, Enum):
    """Tipe janji"""
    MEETING = "meeting"
    INTIMACY = "intimacy"
    ACTIVITY = "activity"
    GIFT = "gift"
    OTHER = "other"


@dataclass
class Promise:
    """Model janji dengan tracking lengkap"""
    id: str
    text: str
    from_user: bool
    promise_type: PromiseType
    status: PromiseStatus = PromiseStatus.PENDING
    created_at: float = field(default_factory=time.time)
    fulfilled_at: Optional[float] = None
    deadline: Optional[float] = None
    reminder_sent: bool = False
    reminder_count: int = 0
    context: Dict = field(default_factory=dict)
    
    @property
    def age_hours(self) -> float:
        return (time.time() - self.created_at) / 3600
    
    @property
    def is_overdue(self) -> bool:
        if self.deadline and self.status == PromiseStatus.PENDING:
            return time.time() > self.deadline
        return False
    
    def fulfill(self):
        self.status = PromiseStatus.FULFILLED
        self.fulfilled_at = time.time()
    
    def break_promise(self):
        self.status = PromiseStatus.BROKEN
    
    def cancel(self):
        self.status = PromiseStatus.CANCELLED
    
    def remind(self):
        self.reminder_sent = True
        self.reminder_count += 1
        if self.status == PromiseStatus.PENDING:
            self.status = PromiseStatus.REMINDED
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'text': self.text,
            'from_user': self.from_user,
            'promise_type': self.promise_type.value,
            'status': self.status.value,
            'created_at': self.created_at,
            'fulfilled_at': self.fulfilled_at,
            'deadline': self.deadline,
            'reminder_sent': self.reminder_sent,
            'reminder_count': self.reminder_count,
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Promise':
        return cls(
            id=data['id'],
            text=data['text'],
            from_user=data['from_user'],
            promise_type=PromiseType(data['promise_type']),
            status=PromiseStatus(data.get('status', 'pending')),
            created_at=data.get('created_at', time.time()),
            fulfilled_at=data.get('fulfilled_at'),
            deadline=data.get('deadline'),
            reminder_sent=data.get('reminder_sent', False),
            reminder_count=data.get('reminder_count', 0),
            context=data.get('context', {})
        )


@dataclass
class Plan:
    """Model rencana dengan tracking"""
    id: str
    text: str
    plan_type: str
    status: PlanStatus = PlanStatus.PENDING
    created_at: float = field(default_factory=time.time)
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    location: Optional[str] = None
    completed_at: Optional[float] = None
    reminder_sent: bool = False
    context: Dict = field(default_factory=dict)
    
    def complete(self):
        self.status = PlanStatus.COMPLETED
        self.completed_at = time.time()
    
    def cancel(self):
        self.status = PlanStatus.CANCELLED
    
    def start(self):
        self.status = PlanStatus.IN_PROGRESS
    
    def remind(self):
        self.reminder_sent = True
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'text': self.text,
            'plan_type': self.plan_type,
            'status': self.status.value,
            'created_at': self.created_at,
            'scheduled_date': self.scheduled_date,
            'scheduled_time': self.scheduled_time,
            'location': self.location,
            'completed_at': self.completed_at,
            'reminder_sent': self.reminder_sent,
            'context': self.context
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Plan':
        return cls(
            id=data['id'],
            text=data['text'],
            plan_type=data['plan_type'],
            status=PlanStatus(data.get('status', 'pending')),
            created_at=data.get('created_at', time.time()),
            scheduled_date=data.get('scheduled_date'),
            scheduled_time=data.get('scheduled_time'),
            location=data.get('location'),
            completed_at=data.get('completed_at'),
            reminder_sent=data.get('reminder_sent', False),
            context=data.get('context', {})
        )


class PromisesTracker:
    """
    Tracking janji dan rencana dengan auto-detection fulfilled
    Target Realism 9.9/10
    """
    
    def __init__(self):
        self.promises: List[Promise] = []
        self.plans: List[Plan] = []
        self.fulfilled_promises: List[Promise] = []
        self.broken_promises: List[Promise] = []
        
        # Pattern untuk deteksi janji
        self.promise_patterns = [
            (r'\b(janji|promise)\b', PromiseType.OTHER),
            (r'\b(besok|nanti|minggu depan)\s+(ketemu|temu|jumpa|ke)\b', PromiseType.MEETING),
            (r'\b(ayo|yuk|mau)\s+(intim|ml|tidur|ke kamar)\b', PromiseType.INTIMACY),
            (r'\b(ngajak|ajak)\s+(nonton|makan|jalan|ke)\b', PromiseType.ACTIVITY),
            (r'\b(kasih|beliin|kado|hadiah)\b', PromiseType.GIFT),
        ]

        # ===== TAMBAHKAN INI =====
        self.plan_patterns = [
            (r'\b(rencana|plan|akan)\s+(\w+)', 'general'),
            (r'\b(besok|nanti|minggu depan)\s+(ketemu|temu|jalan)\b', 'meeting'),
            (r'\b(mau|ingin)\s+(nonton|makan|beli)\b', 'activity'),
        ]
        # ===== END TAMBAHAN =====
        
        # Pattern untuk deteksi fulfilled promise
        self.fulfill_patterns = [
            (r'\b(udah|sudah|telah)\s+(ketemu|temu|jumpa|ke)\b', PromiseType.MEETING),
            (r'\b(udah|sudah|telah)\s+(intim|ml|tidur)\b', PromiseType.INTIMACY),
            (r'\b(udah|sudah|telah)\s+(nonton|makan|jalan)\b', PromiseType.ACTIVITY),
            (r'\b(udah|sudah|telah)\s+(kasih|beliin|kado)\b', PromiseType.GIFT),
            (r'\b(tepato|jadi|kelar)\b', None),
        ]
        
        logger.info("✅ PromisesTracker 9.9 initialized")
    
    def extract_from_message(
        self,
        message: str,
        from_user: bool,
        chat_id: Optional[int] = None
    ) -> Tuple[List[Promise], List[Plan], Optional[Promise]]:
        """
        Ekstrak janji dan rencana dari pesan, juga deteksi fulfilled
        
        Returns:
            (promises, plans, fulfilled_promise)
        """
        msg_lower = message.lower()
        new_promises = []
        new_plans = []
        fulfilled = None
        
        # Deteksi fulfilled promise terlebih dahulu
        fulfilled = self._detect_fulfilled_promise(msg_lower)
        
        # Deteksi janji baru
        for pattern, promise_type in self.promise_patterns:
            if re.search(pattern, msg_lower):
                promise = self._create_promise(message, from_user, promise_type, chat_id)
                if promise:
                    self.promises.append(promise)
                    new_promises.append(promise)
                    logger.info(f"📝 New promise detected: {promise.text[:50]}")
        
        # Deteksi rencana baru
        for pattern, plan_type in self.plan_patterns:
            if re.search(pattern, msg_lower):
                plan = self._create_plan(message, plan_type, chat_id)
                if plan:
                    self.plans.append(plan)
                    new_plans.append(plan)
                    logger.info(f"📅 New plan detected: {plan.text[:50]}")
        
        return new_promises, new_plans, fulfilled
    
    def _detect_fulfilled_promise(self, message: str) -> Optional[Promise]:
        """Deteksi apakah user menepati janji"""
        for pattern, promise_type in self.fulfill_patterns:
            if re.search(pattern, message):
                # Cari promise yang cocok
                for promise in self.promises:
                    if promise.status != PromiseStatus.PENDING:
                        continue
                    
                    # Cek berdasarkan tipe
                    if promise_type and promise.promise_type != promise_type:
                        continue
                    
                    # Cek berdasarkan kata kunci dalam promise
                    promise_keywords = promise.text.lower().split()
                    message_keywords = message.lower().split()
                    
                    if any(k in message_keywords for k in promise_keywords[:3]):
                        promise.fulfill()
                        self.fulfilled_promises.append(promise)
                        logger.info(f"✅ Promise fulfilled: {promise.text[:50]}")
                        return promise
        
        return None
    
    def _create_promise(
        self,
        text: str,
        from_user: bool,
        promise_type: PromiseType,
        chat_id: Optional[int]
    ) -> Optional[Promise]:
        import uuid
        promise = Promise(
            id=str(uuid.uuid4())[:8],
            text=text[:200],
            from_user=from_user,
            promise_type=promise_type,
            deadline=self._extract_deadline(text),
            context={'chat_id': chat_id, 'raw_text': text[:100]}
        )
        return promise
    
    def _create_plan(
        self,
        text: str,
        plan_type: str,
        chat_id: Optional[int]
    ) -> Optional[Plan]:
        import uuid
        plan = Plan(
            id=str(uuid.uuid4())[:8],
            text=text[:200],
            plan_type=plan_type,
            scheduled_date=self._extract_date(text),
            scheduled_time=self._extract_time(text),
            location=self._extract_location(text),
            context={'chat_id': chat_id, 'raw_text': text[:100]}
        )
        return plan
    
    def _extract_deadline(self, text: str) -> Optional[float]:
        """Ekstrak deadline dari teks"""
        import re
        
        # Cek format "besok", "lusa", dll
        time_keywords = {
            'besok': 1,
            'lusa': 2,
            'minggu depan': 7,
        }
        
        for keyword, days in time_keywords.items():
            if keyword in text:
                return time.time() + (days * 86400)
        
        # Cek format "jam X"
        match = re.search(r'(jam|pukul)\s+(\d{1,2})', text)
        if match:
            hour = int(match.group(2))
            now = datetime.now()
            deadline = now.replace(hour=hour, minute=0, second=0)
            if deadline < now:
                deadline = deadline.replace(day=now.day + 1)
            return deadline.timestamp()
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        keywords = ['besok', 'lusa', 'minggu depan', 'hari sabtu', 'hari minggu']
        for kw in keywords:
            if kw in text:
                return kw
        return None
    
    def _extract_time(self, text: str) -> Optional[str]:
        import re
        match = re.search(r'(jam|pukul)\s+(\d{1,2})', text)
        if match:
            return f"{match.group(2)}:00"
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        import re
        match = re.search(r'(ke|di)\s+(\w+)', text)
        if match:
            return match.group(2)
        return None
    
    def get_pending_promises(self, from_user: Optional[bool] = None) -> List[Promise]:
        pending = [p for p in self.promises if p.status in [PromiseStatus.PENDING, PromiseStatus.REMINDED]]
        if from_user is not None:
            pending = [p for p in pending if p.from_user == from_user]
        return pending
    
    def get_user_pending_promises(self) -> List[Promise]:
        return self.get_pending_promises(from_user=True)
    
    def get_reminders(self) -> List[Dict]:
        """Dapatkan pengingat untuk janji yang mendekati deadline"""
        reminders = []
        now = time.time()
        
        for promise in self.get_pending_promises():
            if promise.deadline and not promise.reminder_sent:
                time_left = promise.deadline - now
                
                # 24 jam sebelum deadline
                if 82800 < time_left < 86400:
                    promise.remind()
                    reminders.append({
                        'type': 'promise',
                        'text': promise.text,
                        'time_left': time_left,
                        'urgency': 'besok'
                    })
                # 1 jam sebelum deadline
                elif 3000 < time_left < 3600:
                    promise.remind()
                    reminders.append({
                        'type': 'promise',
                        'text': promise.text,
                        'time_left': time_left,
                        'urgency': 'sebentar lagi'
                    })
        
        return reminders
    
    def format_pending_promises(self) -> str:
        """Format janji pending untuk display"""
        promises = self.get_user_pending_promises()
        
        if not promises:
            return "📝 Tidak ada janji yang tertunda"
        
        lines = ["📝 **JANJI YANG BELUM DITEPATI:**", ""]
        
        for i, p in enumerate(promises, 1):
            status_emoji = "⏰" if p.status == PromiseStatus.REMINDED else "📌"
            lines.append(f"{status_emoji} {i}. {p.text}")
            
            if p.deadline:
                time_left = (p.deadline - time.time()) / 3600
                if time_left > 0:
                    lines.append(f"   ⏳ {time_left:.0f} jam lagi")
        
        return "\n".join(lines)
    
    def format_pending_plans(self) -> str:
        """Format rencana pending untuk display"""
        plans = [p for p in self.plans if p.status in [PlanStatus.PENDING, PlanStatus.UPCOMING]]
        
        if not plans:
            return "📅 Tidak ada rencana yang tertunda"
        
        lines = ["📅 **RENCANA:**", ""]
        
        for i, p in enumerate(plans, 1):
            lines.append(f"{i}. {p.text}")
            if p.scheduled_date:
                lines.append(f"   📆 {p.scheduled_date}")
            if p.scheduled_time:
                lines.append(f"   🕐 {p.scheduled_time}")
            if p.location:
                lines.append(f"   📍 {p.location}")
        
        return "\n".join(lines)
    
    def get_stats(self) -> Dict:
        return {
            'total_promises': len(self.promises),
            'pending': len(self.get_pending_promises()),
            'fulfilled': len(self.fulfilled_promises),
            'broken': len(self.broken_promises),
            'total_plans': len(self.plans)
        }


__all__ = ['PromisesTracker', 'Promise', 'Plan', 'PromiseStatus', 'PlanStatus', 'PromiseType']
