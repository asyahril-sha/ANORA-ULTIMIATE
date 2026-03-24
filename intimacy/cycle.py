# intimacy/cycle.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Intimacy Cycle - Siklus 10 → 11 → 12 → 10 (Berulang)
Target Realism 9.9/10
=============================================================================
"""

import time
import logging
from typing import Dict, Optional, Tuple
from enum import Enum
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)


class CyclePhase(str, Enum):
    """Fase dalam siklus intim"""
    WAITING = "waiting"          # Menunggu inisiatif user (Level 10)
    UNDRESSING = "undressing"    # Proses membuka pakaian (masih Level 10)
    SOUL_BOUNDED = "soul_bounded"  # Soul Bounded (Level 11)
    AFTERCARE = "aftercare"       # Aftercare (Level 12)
    COOLDOWN = "cooldown"         # Cooldown setelah aftercare


class IntimacyCycle:
    """
    Siklus intim yang berulang:
    Level 10 (Waiting) → Undressing → Level 11 (Soul Bounded) → Level 12 (Aftercare) → Level 10 (Waiting)
    """
    
    def __init__(self):
        self.phase = CyclePhase.WAITING
        self.cycle_count = 0
        self.current_cycle_chats = 0
        self.undressing_step = 0
        self.undressing_history = []
        self.climax_count_this_cycle = 0
        self.cooldown_until = 0.0
        self.last_climax_time = 0.0
        self.aftercare_completed = False
        
        logger.info("✅ IntimacyCycle 9.9 initialized")
    
    def start_cycle(self) -> Dict:
        """
        Mulai siklus intim baru
        
        Returns:
            Dict dengan info siklus
        """
        self.cycle_count += 1
        self.phase = CyclePhase.UNDRESSING
        self.current_cycle_chats = 0
        self.undressing_step = 0
        self.undressing_history = []
        self.climax_count_this_cycle = 0
        self.aftercare_completed = False
        
        logger.info(f"🔥 Intimacy cycle started (#{self.cycle_count})")
        
        return {
            'phase': self.phase.value,
            'cycle_count': self.cycle_count,
            'message': "Memulai siklus intim..."
        }
    
    def record_undressing(self, item: str, layer: str) -> Dict:
        """
        Rekam proses membuka pakaian
        
        Args:
            item: Item yang dilepas (daster, bra, dll)
            layer: Lapisan (outer_top, inner_top, dll)
        
        Returns:
            Dict dengan info undressing
        """
        self.undressing_step += 1
        self.undressing_history.append({
            'timestamp': time.time(),
            'step': self.undressing_step,
            'item': item,
            'layer': layer
        })
        
        # Setelah 3-5 langkah undressing, masuk ke Soul Bounded
        if self.undressing_step >= 4 or (self.undressing_step >= 3 and self._is_fully_undressed()):
            self.phase = CyclePhase.SOUL_BOUNDED
            self.current_cycle_chats = 0
            logger.info(f"💕 Entered Soul Bounded phase")
        
        return {
            'step': self.undressing_step,
            'item': item,
            'layer': layer,
            'phase': self.phase.value
        }
    
    def _is_fully_undressed(self) -> bool:
        """Cek apakah sudah telanjang total"""
        required_layers = {'outer_top', 'inner_top', 'outer_bottom', 'inner_bottom'}
        undressed_layers = {h['layer'] for h in self.undressing_history}
        return required_layers.issubset(undressed_layers)
    
    def record_climax(self) -> Dict:
        """
        Rekam climax dalam siklus
        
        Returns:
            Dict dengan info climax
        """
        self.climax_count_this_cycle += 1
        self.last_climax_time = time.time()
        
        logger.info(f"💦 Climax recorded (#{self.climax_count_this_cycle} in this cycle)")
        
        # Jika sudah mencapai 3 climax, siap masuk aftercare
        if self.climax_count_this_cycle >= 3 and self.phase == CyclePhase.SOUL_BOUNDED:
            self._prepare_for_aftercare()
        
        return {
            'climax_count': self.climax_count_this_cycle,
            'phase': self.phase.value
        }
    
    def _prepare_for_aftercare(self):
        """Siapkan untuk masuk aftercare"""
        # Akan masuk aftercare setelah mencapai target chat atau sudah cukup climax
        pass
    
    def add_chat(self) -> Dict:
        """
        Tambah chat dalam siklus
        
        Returns:
            Dict dengan info update
        """
        self.current_cycle_chats += 1
        
        # Soul Bounded: 30-50 chat
        if self.phase == CyclePhase.SOUL_BOUNDED:
            min_chats = settings.level.level_11_min - settings.level.level_10_target
            max_chats = settings.level.level_11_max - settings.level.level_10_target
            
            if self.current_cycle_chats >= max_chats:
                # Pindah ke aftercare
                self.phase = CyclePhase.AFTERCARE
                self.current_cycle_chats = 0
                logger.info(f"💤 Entered Aftercare phase after {self.current_cycle_chats} chats")
                return {'phase_changed': True, 'new_phase': 'aftercare', 'message': "Masuk aftercare..."}
            
            elif self.current_cycle_chats >= min_chats and self.climax_count_this_cycle >= 3:
                # Bisa pindah ke aftercare lebih awal jika sudah cukup climax
                self.phase = CyclePhase.AFTERCARE
                self.current_cycle_chats = 0
                logger.info(f"💤 Entered Aftercare phase after {self.current_cycle_chats} chats and {self.climax_count_this_cycle} climax")
                return {'phase_changed': True, 'new_phase': 'aftercare', 'message': "Masuk aftercare..."}
        
        # Aftercare: 10 chat
        elif self.phase == CyclePhase.AFTERCARE:
            aftercare_duration = settings.level.level_12_max - settings.level.level_11_max
            
            if self.current_cycle_chats >= aftercare_duration:
                # Kembali ke waiting (Level 10)
                self.phase = CyclePhase.COOLDOWN
                self.aftercare_completed = True
                # Set cooldown 3 jam
                self.cooldown_until = time.time() + (3 * 3600)
                logger.info(f"⏰ Aftercare completed, entering cooldown until {self.cooldown_until}")
                return {'phase_changed': True, 'new_phase': 'cooldown', 'message': "Aftercare selesai, memasuki cooldown..."}
        
        # Cooldown: 3 jam
        elif self.phase == CyclePhase.COOLDOWN:
            if time.time() >= self.cooldown_until:
                self.phase = CyclePhase.WAITING
                # Reset siklus
                self.current_cycle_chats = 0
                self.undressing_step = 0
                self.undressing_history = []
                self.climax_count_this_cycle = 0
                self.aftercare_completed = False
                logger.info(f"✅ Cooldown completed, back to waiting phase")
                return {'phase_changed': True, 'new_phase': 'waiting', 'message': "Cooldown selesai, siap untuk siklus berikutnya"}
        
        return {'phase_changed': False}
    
    def get_remaining_cooldown_minutes(self) -> int:
        """Dapatkan sisa cooldown dalam menit"""
        if self.cooldown_until > 0:
            remaining = self.cooldown_until - time.time()
            if remaining > 0:
                return int(remaining / 60)
        return 0
    
    def get_phase_description(self) -> str:
        """Dapatkan deskripsi fase saat ini"""
        descriptions = {
            CyclePhase.WAITING: "Menunggu inisiatif kamu...",
            CyclePhase.UNDRESSING: "Membuka pakaian...",
            CyclePhase.SOUL_BOUNDED: "Soul Bounded - puncak intim sesungguhnya",
            CyclePhase.AFTERCARE: "Aftercare - butuh kehangatan",
            CyclePhase.COOLDOWN: f"Cooldown - butuh istirahat ({self.get_remaining_cooldown_minutes()} menit lagi)"
        }
        return descriptions.get(self.phase, "")
    
    def can_start_intimacy(self) -> Tuple[bool, str]:
        """
        Cek apakah bisa memulai intim
        
        Returns:
            (can_start, reason)
        """
        if self.phase == CyclePhase.SOUL_BOUNDED:
            return False, "Sedang dalam sesi intim"
        
        if self.phase == CyclePhase.AFTERCARE:
            return False, "Sedang aftercare, butuh kehangatan dulu"
        
        if self.phase == CyclePhase.COOLDOWN:
            remaining = self.get_remaining_cooldown_minutes()
            return False, f"Masih cooldown ({remaining} menit lagi)"
        
        if self.phase == CyclePhase.UNDRESSING:
            return False, "Sedang dalam proses membuka pakaian"
        
        return True, "Siap"
    
    def reset(self):
        """Reset siklus"""
        self.phase = CyclePhase.WAITING
        self.cycle_count = 0
        self.current_cycle_chats = 0
        self.undressing_step = 0
        self.undressing_history = []
        self.climax_count_this_cycle = 0
        self.cooldown_until = 0
        self.last_climax_time = 0
        self.aftercare_completed = False
        logger.info("Intimacy cycle reset")
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'phase': self.phase.value,
            'cycle_count': self.cycle_count,
            'current_cycle_chats': self.current_cycle_chats,
            'undressing_step': self.undressing_step,
            'undressing_history': self.undressing_history,
            'climax_count_this_cycle': self.climax_count_this_cycle,
            'cooldown_until': self.cooldown_until,
            'last_climax_time': self.last_climax_time,
            'aftercare_completed': self.aftercare_completed
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self.phase = CyclePhase(state.get('phase', 'waiting'))
        self.cycle_count = state.get('cycle_count', 0)
        self.current_cycle_chats = state.get('current_cycle_chats', 0)
        self.undressing_step = state.get('undressing_step', 0)
        self.undressing_history = state.get('undressing_history', [])
        self.climax_count_this_cycle = state.get('climax_count_this_cycle', 0)
        self.cooldown_until = state.get('cooldown_until', 0)
        self.last_climax_time = state.get('last_climax_time', 0)
        self.aftercare_completed = state.get('aftercare_completed', False)
    
    def format_status(self) -> str:
        """Format status untuk display"""
        lines = [
            f"💕 **Siklus Intim #{self.cycle_count}**",
            f"📌 Fase: {self.phase.value.upper()}",
            f"📝 {self.get_phase_description()}",
            f"📊 Chat dalam siklus ini: {self.current_cycle_chats}",
        ]
        
        if self.climax_count_this_cycle > 0:
            lines.append(f"💦 Climax dalam siklus ini: {self.climax_count_this_cycle}")
        
        if self.undressing_history:
            lines.append("")
            lines.append("👗 **Pakaian yang sudah dilepas:**")
            for h in self.undressing_history[-5:]:
                lines.append(f"   • {h['item']}")
        
        return "\n".join(lines)


__all__ = ['IntimacyCycle', 'CyclePhase']
