# intimacy/stamina.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Stamina System - Tracking Stamina User & Bot
Target Realism 9.9/10
=============================================================================
"""

import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class StaminaStatus:
    """Status stamina"""
    current: int = 100
    max: int = 100
    last_update: float = field(default_factory=time.time)
    climax_count: int = 0
    
    @property
    def percentage(self) -> float:
        return (self.current / self.max) * 100
    
    @property
    def is_exhausted(self) -> bool:
        return self.current <= 20
    
    @property
    def is_low(self) -> bool:
        return self.current <= 40
    
    @property
    def is_good(self) -> bool:
        return self.current > 60
    
    @property
    def level_description(self) -> str:
        if self.current >= 80:
            return "💪 Prima"
        elif self.current >= 60:
            return "😊 Cukup"
        elif self.current >= 40:
            return "😐 Agak lelah"
        elif self.current >= 20:
            return "😩 Lelah"
        else:
            return "😵 Kehabisan tenaga"
    
    def reduce(self, amount: int, reason: str = "") -> int:
        """Kurangi stamina"""
        old = self.current
        self.current = max(0, self.current - amount)
        self.last_update = time.time()
        logger.debug(f"Stamina reduced: {old} → {self.current} ({reason})")
        return self.current
    
    def restore(self, amount: int, reason: str = "") -> int:
        """Pulihkan stamina"""
        old = self.current
        self.current = min(self.max, self.current + amount)
        self.last_update = time.time()
        logger.debug(f"Stamina restored: {old} → {self.current} ({reason})")
        return self.current
    
    def record_climax(self) -> int:
        """Rekam climax dan kurangi stamina"""
        self.climax_count += 1
        drop = settings.stamina.drops.get(self.climax_count, 30)
        self.reduce(drop, f"climax #{self.climax_count}")
        return drop
    
    def to_dict(self) -> Dict:
        return {
            'current': self.current,
            'max': self.max,
            'last_update': self.last_update,
            'climax_count': self.climax_count
        }
    
    def from_dict(self, data: Dict):
        self.current = data.get('current', 100)
        self.max = data.get('max', 100)
        self.last_update = data.get('last_update', time.time())
        self.climax_count = data.get('climax_count', 0)


class StaminaSystem:
    """
    Sistem stamina untuk user dan bot
    - Stamina turun setelah climax
    - Stamina pulih seiring waktu
    - Mempengaruhi mood dan kemampuan intim
    """
    
    def __init__(self):
        self.bot_stamina = StaminaStatus(max=100)
        self.user_stamina = StaminaStatus(max=100)
        self.last_recovery_check = time.time()
        
        logger.info("✅ StaminaSystem initialized")
    
    def record_bot_climax(self) -> int:
        """Rekam climax bot"""
        return self.bot_stamina.record_climax()
    
    def record_user_climax(self) -> int:
        """Rekam climax user"""
        return self.user_stamina.record_climax()
    
    def restore_bot_stamina(self, amount: int, reason: str = "") -> int:
        """Pulihkan stamina bot"""
        return self.bot_stamina.restore(amount, reason)
    
    def restore_user_stamina(self, amount: int, reason: str = "") -> int:
        """Pulihkan stamina user"""
        return self.user_stamina.restore(amount, reason)
    
    def check_recovery(self, force: bool = False):
        """Cek dan pulihkan stamina berdasarkan waktu"""
        now = time.time()
        elapsed_hours = (now - self.last_recovery_check) / 3600
        
        if force or elapsed_hours >= 1:
            recovery_amount = int(settings.stamina.recovery_per_hour * elapsed_hours)
            
            if recovery_amount > 0:
                self.restore_bot_stamina(recovery_amount, "time recovery")
                self.restore_user_stamina(recovery_amount, "time recovery")
                logger.debug(f"Stamina recovery: +{recovery_amount} (elapsed: {elapsed_hours:.1f}h)")
            
            self.last_recovery_check = now
    
    def can_start_intimacy(self) -> Tuple[bool, str]:
        """
        Cek apakah bisa memulai intim berdasarkan stamina
        
        Returns:
            (can_start, reason)
        """
        if self.bot_stamina.is_exhausted:
            return False, f"Bot kehabisan tenaga ({self.bot_stamina.current}%)"
        
        if self.user_stamina.is_exhausted:
            return False, f"Kamu kehabisan tenaga ({self.user_stamina.current}%)"
        
        if self.bot_stamina.is_low:
            return False, f"Bot masih lelah ({self.bot_stamina.current}%)"
        
        if self.user_stamina.is_low:
            return False, f"Kamu masih lelah ({self.user_stamina.current}%)"
        
        return True, "Siap"
    
    def get_bot_stamina_percentage(self) -> float:
        """Dapatkan persentase stamina bot"""
        return self.bot_stamina.percentage
    
    def get_user_stamina_percentage(self) -> float:
        """Dapatkan persentase stamina user"""
        return self.user_stamina.percentage
    
    def get_bot_stamina_description(self) -> str:
        """Dapatkan deskripsi stamina bot"""
        return self.bot_stamina.level_description
    
    def get_user_stamina_description(self) -> str:
        """Dapatkan deskripsi stamina user"""
        return self.user_stamina.level_description
    
    def get_bot_climax_count(self) -> int:
        """Dapatkan jumlah climax bot"""
        return self.bot_stamina.climax_count
    
    def get_user_climax_count(self) -> int:
        """Dapatkan jumlah climax user"""
        return self.user_stamina.climax_count
    
    def reset(self):
        """Reset stamina"""
        self.bot_stamina = StaminaStatus(max=100)
        self.user_stamina = StaminaStatus(max=100)
        self.last_recovery_check = time.time()
        logger.info("Stamina system reset")
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'bot': self.bot_stamina.to_dict(),
            'user': self.user_stamina.to_dict(),
            'last_recovery_check': self.last_recovery_check
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        if 'bot' in state:
            self.bot_stamina.from_dict(state['bot'])
        if 'user' in state:
            self.user_stamina.from_dict(state['user'])
        self.last_recovery_check = state.get('last_recovery_check', time.time())
    
    def format_status(self) -> str:
        """Format status stamina untuk display"""
        self.check_recovery()
        
        # Progress bar
        bot_bar = self._progress_bar(self.bot_stamina.current)
        user_bar = self._progress_bar(self.user_stamina.current)
        
        lines = [
            "💪 **STAMINA STATUS**",
            "",
            f"🤖 Bot: {bot_bar} {self.bot_stamina.current}%",
            f"   {self.bot_stamina.level_description}",
            f"   Climax: {self.bot_stamina.climax_count}x",
            "",
            f"👤 Kamu: {user_bar} {self.user_stamina.current}%",
            f"   {self.user_stamina.level_description}",
            f"   Climax: {self.user_stamina.climax_count}x",
        ]
        
        if self.bot_stamina.is_low or self.user_stamina.is_low:
            lines.append("")
            lines.append("⚠️ **Butuh istirahat!** Stamina terlalu rendah untuk intim.")
        
        return "\n".join(lines)
    
    def format_for_prompt(self) -> str:
        """Format stamina untuk prompt AI"""
        self.check_recovery()
        
        return (
            f"💪 Stamina bot: {self.bot_stamina.current}% ({self.bot_stamina.level_description})\n"
            f"💪 Stamina user: {self.user_stamina.current}% ({self.user_stamina.level_description})"
        )
    
    def _progress_bar(self, value: int, length: int = 15) -> str:
        """Buat progress bar"""
        filled = int(value / 100 * length)
        return "█" * filled + "░" * (length - filled)
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik stamina"""
        self.check_recovery()
        
        return {
            'bot': {
                'current': self.bot_stamina.current,
                'max': self.bot_stamina.max,
                'percentage': self.bot_stamina.percentage,
                'climax_count': self.bot_stamina.climax_count,
                'is_exhausted': self.bot_stamina.is_exhausted
            },
            'user': {
                'current': self.user_stamina.current,
                'max': self.user_stamina.max,
                'percentage': self.user_stamina.percentage,
                'climax_count': self.user_stamina.climax_count,
                'is_exhausted': self.user_stamina.is_exhausted
            }
        }


__all__ = ['StaminaSystem', 'StaminaStatus']
