"""
ANORA 9.9 Intimacy - Main Module
Menyatukan semua sistem intimacy menjadi satu API sederhana.
TERINTEGRASI DENGAN EMOTIONAL ENGINE 9.9
"""

import logging
from typing import Dict, Optional, Tuple

from .intimacy_flow import get_anora_intimacy_99, anora_intimacy_99, IntimacyFlow99
from .intimacy_core import (
    IntimacyPhase, StaminaSystem, ArousalSystem,
    PositionDatabase, ClimaxLocationDatabase, MoansDatabase, FlashbackDatabase
)
from .emotional_engine import get_emotional_engine
from .conflict_engine import get_conflict_engine
from .relationship import get_relationship_manager

logger = logging.getLogger(__name__)


# =============================================================================
# MAIN INTIMACY CLASS (Wrapper)
# =============================================================================

class AnoraIntimacy99:
    """
    Wrapper untuk IntimacyFlow99.
    Menyediakan API sederhana untuk dipanggil dari luar.
    TERINTEGRASI DENGAN EMOTIONAL ENGINE 9.9
    """
    
    def __init__(self):
        self._flow = None
        self.emotional = get_emotional_engine()
        self.conflict = get_conflict_engine()
        self.relationship = get_relationship_manager()
    
    @property
    def flow(self) -> IntimacyFlow99:
        """Dapatkan IntimacyFlow99 instance"""
        if self._flow is None:
            self._flow = get_anora_intimacy_99()
        return self._flow
    
    def can_start_intimacy(self, level: int) -> Tuple[bool, str]:
        """Cek apakah bisa mulai intim"""
        return self.flow.can_start_intimacy(level)
    
    def start_intimacy(self) -> str:
        """Mulai sesi intim"""
        return self.flow.start_intimacy()
    
    def process_intimacy_message(self, pesan_mas: str, level: int) -> Optional[str]:
        """Proses pesan intim"""
        return self.flow.process_intimacy_message(pesan_mas, level)
    
    def update_from_pesan(self, pesan_mas: str, level: int):
        """Update arousal dan desire dari pesan Mas"""
        self.flow.update_from_pesan(pesan_mas, level)
        
        # Sync dengan emotional engine
        self.emotional.arousal = self.flow.arousal.arousal
        self.emotional.desire = self.flow.arousal.desire
        self.emotional.tension = self.flow.arousal.tension
    
    def get_status(self) -> str:
        """Dapatkan status intimacy lengkap"""
        return self.flow.get_status()
    
    def get_stamina_status(self) -> Tuple[int, int, str, str]:
        """Dapatkan status stamina"""
        return (
            self.flow.stamina.nova_current,
            self.flow.stamina.mas_current,
            self.flow.stamina.get_nova_status(),
            self.flow.stamina.get_mas_status()
        )
    
    def get_arousal_state(self) -> Dict:
        """Dapatkan state arousal"""
        return self.flow.arousal.get_state()
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Dict:
        """Rekam climax manual"""
        return self.flow.session.record_climax(is_heavy)
    
    def end_intimacy(self) -> str:
        """Akhiri sesi intim"""
        return self.flow.session.end()
    
    def is_active(self) -> bool:
        """Cek apakah sesi intim aktif"""
        return self.flow.session.is_active
    
    def get_current_phase(self) -> str:
        """Dapatkan fase intim saat ini"""
        return self.flow.session.phase.value if self.flow.session.phase else "waiting"
    
    def change_position(self, position: str = None) -> Tuple[str, str, str]:
        """Ganti posisi"""
        return self.flow.session.change_position(position)
    
    def get_climax_request(self, location: str = None) -> str:
        """Dapatkan request climax"""
        return self.flow.session.get_climax_request(location)
    
    def sync_with_emotional_engine(self):
        """Sync semua state dengan emotional engine"""
        self.emotional.arousal = self.flow.arousal.arousal
        self.emotional.desire = self.flow.arousal.desire
        self.emotional.tension = self.flow.arousal.tension
    
    def to_dict(self) -> Dict:
        """Serialize ke dict untuk database"""
        return self.flow.to_dict()
    
    def from_dict(self, data: Dict):
        """Load dari dict"""
        self.flow.from_dict(data)


# =============================================================================
# SINGLETON
# =============================================================================

_anora_intimacy_99_instance: Optional['AnoraIntimacy99'] = None


def get_anora_intimacy_99_wrapper() -> AnoraIntimacy99:
    """Dapatkan instance AnoraIntimacy99 (singleton)"""
    global _anora_intimacy_99_instance
    if _anora_intimacy_99_instance is None:
        _anora_intimacy_99_instance = AnoraIntimacy99()
        logger.info("💕 ANORA 9.9 Intimacy initialized")
    return _anora_intimacy_99_instance


# =============================================================================
# EXPORTED FUNCTIONS (untuk kemudahan import)
# =============================================================================

def can_start_intimacy(level: int) -> Tuple[bool, str]:
    """Cek apakah bisa mulai intim"""
    return get_anora_intimacy_99_wrapper().can_start_intimacy(level)


def start_intimacy() -> str:
    """Mulai sesi intim"""
    return get_anora_intimacy_99_wrapper().start_intimacy()


def process_intimacy_message(pesan_mas: str, level: int) -> Optional[str]:
    """Proses pesan intim"""
    return get_anora_intimacy_99_wrapper().process_intimacy_message(pesan_mas, level)


def get_intimacy_status() -> str:
    """Dapatkan status intimacy"""
    return get_anora_intimacy_99_wrapper().get_status()


def end_intimacy() -> str:
    """Akhiri sesi intim"""
    return get_anora_intimacy_99_wrapper().end_intimacy()


def is_intimacy_active() -> bool:
    """Cek apakah sesi intim aktif"""
    return get_anora_intimacy_99_wrapper().is_active()


def get_stamina_status() -> Tuple[int, int, str, str]:
    """Dapatkan status stamina"""
    return get_anora_intimacy_99_wrapper().get_stamina_status()


# =============================================================================
# DIRECT ACCESS (untuk kompatibilitas dengan kode lama)
# =============================================================================

# Singleton instance untuk kemudahan import
anora_intimacy_99 = get_anora_intimacy_99_wrapper()

# Untuk kompatibilitas dengan kode yang masih panggil anora_intimacy
anora_intimacy = anora_intimacy_99


__all__ = [
    'AnoraIntimacy99',
    'IntimacyFlow99',
    'IntimacyPhase',
    'StaminaSystem',
    'ArousalSystem',
    'PositionDatabase',
    'ClimaxLocationDatabase',
    'MoansDatabase',
    'FlashbackDatabase',
    'get_anora_intimacy_99_wrapper',
    'can_start_intimacy',
    'start_intimacy',
    'process_intimacy_message',
    'get_intimacy_status',
    'end_intimacy',
    'is_intimacy_active',
    'get_stamina_status',
    'anora_intimacy_99',
    'anora_intimacy',
]
