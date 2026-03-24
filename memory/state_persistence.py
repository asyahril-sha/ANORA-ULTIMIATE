# memory/state_persistence.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
State Persistence - Menyimpan Semua Aspek State
=============================================================================
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ClothingState:
    """State pakaian dengan hierarchy"""
    bot_outer_top: Optional[str] = None
    bot_outer_bottom: Optional[str] = None
    bot_inner_top: Optional[str] = None
    bot_inner_bottom: Optional[str] = None
    bot_outer_top_on: bool = True
    bot_outer_bottom_on: bool = True
    bot_inner_top_on: bool = True
    bot_inner_bottom_on: bool = True
    user_outer_top: Optional[str] = None
    user_outer_bottom: Optional[str] = None
    user_inner_bottom: Optional[str] = None
    user_outer_top_on: bool = True
    user_outer_bottom_on: bool = True
    user_inner_bottom_on: bool = True
    history: List[Dict] = field(default_factory=list)
    last_updated: float = field(default_factory=lambda: time.time())
    
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
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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


@dataclass
class LocationState:
    bot: str = "ruang tamu"
    user: str = "ruang tamu"
    last_change: float = field(default_factory=lambda: time.time())
    history: List[Dict] = field(default_factory=list)
    
    def update(self, new_location: str, actor: str = "bot"):
        old_location = self.bot if actor == "bot" else self.user
        if actor == "bot":
            self.bot = new_location
        else:
            self.user = new_location
        self.history.append({
            'timestamp': time.time(),
            'actor': actor,
            'from': old_location,
            'to': new_location
        })
        self.last_change = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'bot': self.bot,
            'user': self.user,
            'last_change': self.last_change,
            'history': self.history[-50:]
        }


@dataclass
class PositionState:
    bot: str = "duduk"
    user: str = "duduk"
    relative: str = "bersebelahan"
    last_change: float = field(default_factory=lambda: time.time())
    history: List[Dict] = field(default_factory=list)
    
    def update_bot(self, position: str):
        self.bot = position
        self._add_history("bot", position)
    
    def update_user(self, position: str):
        self.user = position
        self._add_history("user", position)
    
    def update_relative(self, relative: str):
        self.relative = relative
        self._add_history("relative", relative)
    
    def _add_history(self, target: str, value: str):
        self.history.append({
            'timestamp': time.time(),
            'target': target,
            'value': value
        })
        self.last_change = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'bot': self.bot,
            'user': self.user,
            'relative': self.relative,
            'last_change': self.last_change,
            'history': self.history[-50:]
        }


@dataclass
class EmotionalState:
    emotion_bot: str = "netral"
    arousal_bot: int = 0
    mood_bot: str = "normal"
    emotion_user: str = "netral"
    arousal_user: int = 0
    last_change: float = field(default_factory=lambda: time.time())
    history: List[Dict] = field(default_factory=list)
    
    def update_bot(self, emotion: str, arousal_delta: int = 0):
        self.emotion_bot = emotion
        self.arousal_bot = max(0, min(100, self.arousal_bot + arousal_delta))
        self._add_history("bot", emotion, self.arousal_bot)
    
    def update_user(self, emotion: str, arousal: int):
        self.emotion_user = emotion
        self.arousal_user = arousal
        self._add_history("user", emotion, arousal)
    
    def _add_history(self, target: str, emotion: str, arousal: int):
        self.history.append({
            'timestamp': time.time(),
            'target': target,
            'emotion': emotion,
            'arousal': arousal
        })
        self.last_change = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'emotion_bot': self.emotion_bot,
            'arousal_bot': self.arousal_bot,
            'mood_bot': self.mood_bot,
            'emotion_user': self.emotion_user,
            'arousal_user': self.arousal_user,
            'last_change': self.last_change,
            'history': self.history[-50:]
        }


@dataclass
class ActivityState:
    bot: Optional[str] = None
    user: Optional[str] = None
    start_time: Optional[float] = None
    last_update: float = field(default_factory=lambda: time.time())
    history: List[Dict] = field(default_factory=list)
    
    def start_activity(self, actor: str, activity: str):
        if actor == "bot":
            self.bot = activity
        else:
            self.user = activity
        self.start_time = time.time()
        self._add_history("start", actor, activity)
    
    def end_activity(self, actor: str):
        if actor == "bot":
            self.bot = None
        else:
            self.user = None
        self._add_history("end", actor, "")
    
    def _add_history(self, action: str, actor: str, activity: str):
        self.history.append({
            'timestamp': time.time(),
            'action': action,
            'actor': actor,
            'activity': activity
        })
        self.last_update = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'bot': self.bot,
            'user': self.user,
            'start_time': self.start_time,
            'last_update': self.last_update,
            'history': self.history[-50:]
        }


@dataclass
class FamilyState:
    status: Optional[str] = None
    location: Optional[str] = None
    activity: Optional[str] = None
    estimate_return: Optional[str] = None
    last_update: float = field(default_factory=lambda: time.time())
    history: List[Dict] = field(default_factory=list)
    
    def update(self, status: str = None, location: str = None, activity: str = None):
        if status:
            self.status = status
        if location:
            self.location = location
        if activity:
            self.activity = activity
        self.history.append({
            'timestamp': time.time(),
            'status': self.status,
            'location': self.location,
            'activity': self.activity
        })
        self.last_update = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'status': self.status,
            'location': self.location,
            'activity': self.activity,
            'estimate_return': self.estimate_return,
            'last_update': self.last_update,
            'history': self.history[-50:]
        }


@dataclass
class TimeState:
    current: str = "08:00"
    start: str = "08:00"
    overrides: List[Dict] = field(default_factory=list)
    last_update: float = field(default_factory=lambda: time.time())

    # =========================
    # ADVANCE TIME (SMART)
    # =========================
    def advance(self, minutes: int = None):
        now = time.time()

        # AUTO ADVANCE berdasarkan jeda chat
        if minutes is None:
            delta = now - self.last_update

            if delta < 10:
                minutes = 1
            elif delta < 60:
                minutes = 3
            elif delta < 300:
                minutes = 5
            else:
                minutes = 10

        hour, minute = map(int, self.current.split(':'))
        total_minutes = hour * 60 + minute + minutes

        new_hour = (total_minutes // 60) % 24
        new_minute = total_minutes % 60

        self.current = f"{new_hour:02d}:{new_minute:02d}"
        self.last_update = now

    # =========================
    # OVERRIDE (USER FORCE TIME)
    # =========================
    def override(self, new_time: str, reason: str = ""):
        old_time = self.current

        self.current = new_time
        self.overrides.append({
            'timestamp': time.time(),
            'old_time': old_time,
            'new_time': new_time,
            'reason': reason
        })

        self.last_update = time.time()

    # =========================
    # DETECT TIME FROM TEXT
    # =========================
    def detect_and_apply(self, text: str):
        text = text.lower()

        # kata waktu
        mapping = {
            "subuh": "04:00",
            "pagi": "08:00",
            "siang": "12:00",
            "sore": "17:00",
            "malam": "20:00",
            "tengah malam": "00:00"
        }

        for key, val in mapping.items():
            if key in text:
                self.override(val, f"user said {key}")
                return True

        # detect jam format 02:00 / 2:00
        match = re.search(r'(\d{1,2})[:.](\d{2})', text)
        if match:
            hour = int(match.group(1)) % 24
            minute = int(match.group(2))
            self.override(f"{hour:02d}:{minute:02d}", "user explicit time")
            return True

        return False

    # =========================
    # TIME CATEGORY
    # =========================
    def get_time_of_day(self) -> str:
        hour = int(self.current.split(':')[0])

        if 5 <= hour < 11:
            return "pagi"
        elif 11 <= hour < 15:
            return "siang"
        elif 15 <= hour < 18:
            return "sore"
        elif 18 <= hour < 22:
            return "malam"
        return "tengah malam"

    # =========================
    # FEELING (INI YANG BIKIN HIDUP)
    # =========================
    def get_time_feel(self) -> str:
        hour = int(self.current.split(':')[0])

        if 0 <= hour < 5:
            return "sunyi, dingin, ngantuk berat"
        elif 5 <= hour < 9:
            return "pagi segar, masih santai"
        elif 9 <= hour < 12:
            return "fokus, energi naik"
        elif 12 <= hour < 15:
            return "sedikit lelah, butuh istirahat"
        elif 15 <= hour < 18:
            return "santai sore"
        elif 18 <= hour < 22:
            return "hangat, nyaman"
        else:
            return "larut malam, mulai lelah"

    # =========================
    def to_dict(self) -> Dict:
        return {
            'current': self.current,
            'start': self.start,
            'overrides': self.overrides[-20:],
            'last_update': self.last_update
        }


@dataclass
class StatePersistence:
    registration_id: str
    clothing: ClothingState = field(default_factory=ClothingState)
    location: LocationState = field(default_factory=LocationState)
    position: PositionState = field(default_factory=PositionState)
    emotional: EmotionalState = field(default_factory=EmotionalState)
    activity: ActivityState = field(default_factory=ActivityState)
    family: FamilyState = field(default_factory=FamilyState)
    time: TimeState = field(default_factory=TimeState)
    created_at: float = field(default_factory=lambda: time.time())
    updated_at: float = field(default_factory=lambda: time.time())
    
    def update_all(self, data: Dict):
        if 'clothing' in data:
            self.clothing.from_dict(data['clothing'])
        if 'location' in data:
            self.location.update(data['location'].get('bot', self.location.bot))
        if 'position' in data:
            if 'bot' in data['position']:
                self.position.update_bot(data['position']['bot'])
            if 'user' in data['position']:
                self.position.update_user(data['position']['user'])
            if 'relative' in data['position']:
                self.position.update_relative(data['position']['relative'])
        if 'emotional' in data:
            if 'bot' in data['emotional']:
                self.emotional.update_bot(
                    data['emotional']['bot'].get('emotion', self.emotional.emotion_bot),
                    data['emotional']['bot'].get('arousal_delta', 0)
                )
        if 'family' in data:
            self.family.update(
                status=data['family'].get('status'),
                location=data['family'].get('location'),
                activity=data['family'].get('activity')
            )
        if 'time' in data and 'override' in data['time']:
            self.time.override(data['time']['override'], data['time'].get('reason', ''))
        self.updated_at = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'registration_id': self.registration_id,
            'clothing': json.dumps(self.clothing.to_dict()),
            'location': json.dumps(self.location.to_dict()),
            'position': json.dumps(self.position.to_dict()),
            'emotional': json.dumps(self.emotional.to_dict()),
            'activity': json.dumps(self.activity.to_dict()),
            'family': json.dumps(self.family.to_dict()),
            'time': json.dumps(self.time.to_dict()),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def from_dict(self, data: Dict):
        self.registration_id = data['registration_id']
        if data.get('clothing'):
            self.clothing.from_dict(json.loads(data['clothing']))
        if data.get('location'):
            loc_data = json.loads(data['location'])
            self.location.bot = loc_data.get('bot', 'ruang tamu')
            self.location.user = loc_data.get('user', 'ruang tamu')
        if data.get('position'):
            pos_data = json.loads(data['position'])
            self.position.bot = pos_data.get('bot', 'duduk')
            self.position.user = pos_data.get('user', 'duduk')
            self.position.relative = pos_data.get('relative', 'bersebelahan')
        if data.get('emotional'):
            emo_data = json.loads(data['emotional'])
            self.emotional.emotion_bot = emo_data.get('emotion_bot', 'netral')
            self.emotional.arousal_bot = emo_data.get('arousal_bot', 0)
            self.emotional.mood_bot = emo_data.get('mood_bot', 'normal')
        if data.get('family'):
            fam_data = json.loads(data['family'])
            self.family.status = fam_data.get('status')
            self.family.location = fam_data.get('location')
            self.family.activity = fam_data.get('activity')
        if data.get('time'):
            time_data = json.loads(data['time'])
            self.time.current = time_data.get('current', '08:00')
            self.time.start = time_data.get('start', '08:00')
        self.created_at = data.get('created_at', time.time())
        self.updated_at = data.get('updated_at', time.time())
    
    def get_context_for_prompt(self) -> str:
        lines = [
            "📍 **STATE SAAT INI:**",
            f"• Waktu: {self.time.current} ({self.time.get_time_of_day()})",
            f"• Lokasi bot: {self.location.bot}",
            f"• Lokasi user: {self.location.user}",
            f"• Posisi bot: {self.position.bot}",
            f"• Posisi user: {self.position.user}",
            f"• Posisi relatif: {self.position.relative}",
            f"• Pakaian bot: {self.clothing.get_description()}",
            f"• Emosi bot: {self.emotional.emotion_bot} | Arousal: {self.emotional.arousal_bot}%",
            f"• Mood bot: {self.emotional.mood_bot}"
        ]
        if self.family.status:
            lines.append(f"• Status istri: {self.family.status} | Lokasi: {self.family.location or '-'}")
        if self.activity.bot:
            lines.append(f"• Aktivitas bot: {self.activity.bot}")
        return "\n".join(lines)


__all__ = [
    'ClothingState',
    'LocationState',
    'PositionState',
    'EmotionalState',
    'ActivityState',
    'FamilyState',
    'TimeState',
    'StatePersistence'
]
