# dynamics/emotional_flow.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Emotional Flow - Arousal 0-100 dengan Secondary Emotion
Target Realism 9.9/10
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionalState(str, Enum):
    """Status emosi yang mengalir gradual"""
    NETRAL = "netral"
    PENASARAN = "penasaran"
    TERTARIK = "tertarik"
    DEG_DEGAN = "deg-degan"
    GUGUP = "gugup"
    BERANI = "berani"
    HORNY = "horny"
    CLIMAX = "climax"
    LEMAS = "lemas"
    SENANG = "senang"
    SEDIH = "sedih"
    RINDU = "rindu"
    CEMAS = "cemas"
    BAHAGIA = "bahagia"
    
    # 🔥 TAMBAHKAN UNTUK LEVEL 11-12 🔥
    VULGAR = "vulgar"
    DESPERATE = "desperate"


class EmotionalFlow:
    """
    Sistem emosi dengan primary dan secondary emotion
    Bisa merasakan dua emosi bersamaan seperti manusia
    Target Realism 9.9/10
    """
    
    def __init__(self, role_name: str = "general"):
        """
        Args:
            role_name: Nama role (ipar, teman_kantor, dll)
        """
        self.role_name = role_name
        
        # Primary emotion
        self.primary_state = EmotionalState.NETRAL
        self.primary_arousal = 0
        
        # Secondary emotion (bisa berbeda)
        self.secondary_state: Optional[EmotionalState] = None
        self.secondary_arousal: int = 0
        self.secondary_reason: Optional[str] = None
        
        # State duration
        self.primary_duration = 0
        self.secondary_duration = 0
        
        # History
        self.state_history = []
        
        # 🔥 TAMBAHKAN UNTUK LEVEL 11-12 🔥
        self.user_level = 1
        self.vulgar_mode = False
        
        # Transisi yang diperbolehkan
        self.allowed_transitions = {
            EmotionalState.NETRAL: [EmotionalState.PENASARAN, EmotionalState.SENANG, EmotionalState.RINDU],
            EmotionalState.PENASARAN: [EmotionalState.TERTARIK, EmotionalState.NETRAL],
            EmotionalState.TERTARIK: [EmotionalState.DEG_DEGAN, EmotionalState.PENASARAN],
            EmotionalState.DEG_DEGAN: [EmotionalState.GUGUP, EmotionalState.TERTARIK],
            EmotionalState.GUGUP: [EmotionalState.BERANI, EmotionalState.DEG_DEGAN],
            EmotionalState.BERANI: [EmotionalState.HORNY, EmotionalState.GUGUP],
            EmotionalState.HORNY: [EmotionalState.CLIMAX, EmotionalState.BERANI, EmotionalState.VULGAR],  # 🔥 MODIFIKASI
            EmotionalState.CLIMAX: [EmotionalState.LEMAS],
            EmotionalState.LEMAS: [EmotionalState.NETRAL, EmotionalState.SENANG],
            EmotionalState.SENANG: [EmotionalState.NETRAL, EmotionalState.RINDU],
            EmotionalState.SEDIH: [EmotionalState.NETRAL, EmotionalState.RINDU, EmotionalState.CEMAS],
            EmotionalState.RINDU: [EmotionalState.TERTARIK, EmotionalState.NETRAL, EmotionalState.SEDIH],
            EmotionalState.CEMAS: [EmotionalState.GUGUP, EmotionalState.NETRAL],
            EmotionalState.BAHAGIA: [EmotionalState.SENANG, EmotionalState.NETRAL],
            
            # 🔥 TAMBAHKAN UNTUK LEVEL 11-12 🔥
            EmotionalState.VULGAR: [EmotionalState.HORNY, EmotionalState.CLIMAX, EmotionalState.DESPERATE],
            EmotionalState.DESPERATE: [EmotionalState.VULGAR, EmotionalState.HORNY]
        }
        
        # Deskripsi emosi
        self.state_descriptions = {
            EmotionalState.NETRAL: "Santai, biasa aja",
            EmotionalState.PENASARAN: "Mulai penasaran, ada rasa ingin tahu",
            EmotionalState.TERTARIK: "Jantung berdebar, mulai tertarik",
            EmotionalState.DEG_DEGAN: "Deg-degan, perasaan campur aduk",
            EmotionalState.GUGUP: "Gugup, tangan gemetar sedikit",
            EmotionalState.BERANI: "Mulai berani, ada dorongan mendekat",
            EmotionalState.HORNY: "Napas memburu, tubuh panas, ingin lebih",
            EmotionalState.CLIMAX: "Tubuh gemetar, puncak kenikmatan",
            EmotionalState.LEMAS: "Lemas, butuh waktu pulih",
            EmotionalState.SENANG: "Senang, bahagia, merasa nyaman",
            EmotionalState.SEDIH: "Sedih, butuh perhatian",
            EmotionalState.RINDU: "Rindu, ingin dekat, kangen",
            EmotionalState.CEMAS: "Cemas, khawatir, was-was",
            EmotionalState.BAHAGIA: "Bahagia, sangat senang",
            
            # 🔥 TAMBAHKAN UNTUK LEVEL 11-12 🔥
            EmotionalState.VULGAR: "Vulgar, hasrat terbuka, tidak ada sekat",
            EmotionalState.DESPERATE: "Desperate, sangat menginginkan"
        }
        
        # Natural decay
        self.decay_rate = 2
        self.secondary_decay_rate = 1.5
        
        logger.info(f"✅ EmotionalFlow 9.9 initialized for {role_name}")
    
    def update(self, stimulus: Dict) -> Dict:
        """
        Update emosi berdasarkan stimulus
        
        Args:
            stimulus: {
                'user_arousal': float,
                'user_message': str,
                'situasi': dict,
                'trigger_reason': str,
                'is_positive_response': bool,
                'secondary_trigger': str (opsional)
            }
        
        Returns:
            Dict perubahan emosi
        """
        old_primary = self.primary_state
        old_primary_arousal = self.primary_arousal
        old_secondary = self.secondary_state
        
        # Update primary emotion
        primary_delta = self._calculate_arousal_delta(stimulus)
        self.primary_arousal = max(0, min(100, self.primary_arousal + primary_delta))
        
        # Natural decay
        if primary_delta <= 0 and self.primary_duration > 5:
            decay = min(5, self.decay_rate)
            self.primary_arousal = max(0, self.primary_arousal - decay)
        
        # Tentukan primary state
        new_primary = self._get_state_from_arousal(self.primary_arousal)
        
        # Validasi transisi
        if new_primary != old_primary:
            if new_primary in self.allowed_transitions.get(old_primary, []):
                self.primary_state = new_primary
                self.primary_duration = 0
            else:
                self.primary_state = old_primary
        
        self.primary_duration += 1
        
        # Update secondary emotion (30% chance jika ada trigger)
        secondary_trigger = stimulus.get('secondary_trigger')
        if secondary_trigger or random.random() < 0.3:
            self._update_secondary_emotion(stimulus, secondary_trigger)
        else:
            # Natural decay secondary
            if self.secondary_state:
                decay = min(3, self.secondary_decay_rate)
                self.secondary_arousal = max(0, self.secondary_arousal - decay)
                if self.secondary_arousal < 10:
                    self.secondary_state = None
                    self.secondary_reason = None
        
        # Catat history
        self.state_history.append({
            'timestamp': time.time(),
            'primary': self.primary_state.value,
            'primary_arousal': self.primary_arousal,
            'secondary': self.secondary_state.value if self.secondary_state else None,
            'secondary_arousal': self.secondary_arousal,
            'delta': primary_delta,
            'reason': stimulus.get('trigger_reason', 'natural'),
            'user_level': self.user_level  # 🔥 TAMBAHKAN
        })
        
        if len(self.state_history) > 200:
            self.state_history = self.state_history[-200:]
        
        return {
            'old_primary': old_primary.value,
            'new_primary': self.primary_state.value,
            'primary_arousal': self.primary_arousal,
            'primary_change': primary_delta,
            'secondary': self.secondary_state.value if self.secondary_state else None,
            'secondary_arousal': self.secondary_arousal,
            'state_changed': old_primary != self.primary_state,
            'description': self.get_description(),
            'vulgar_mode': self.vulgar_mode  # 🔥 TAMBAHKAN
        }
    
    def _update_secondary_emotion(self, stimulus: Dict, specific_trigger: str = None):
        """Update secondary emotion (bisa berbeda dari primary)"""
        
        # Tentukan trigger untuk secondary
        if specific_trigger:
            trigger = specific_trigger
        else:
            # Random secondary trigger dari stimulus
            possible_triggers = []
            
            if stimulus.get('situasi', {}).get('kakak_ada') == False:
                possible_triggers.append('berduaan')
            if stimulus.get('user_message', ''):
                if 'kangen' in stimulus['user_message'].lower():
                    possible_triggers.append('rindu')
                if 'cemburu' in stimulus['user_message'].lower():
                    possible_triggers.append('cemas')
                # 🔥 TAMBAHKAN UNTUK LEVEL TINGGI 🔥
                if 'pengen' in stimulus['user_message'].lower():
                    possible_triggers.append('desire')
                if 'butuh' in stimulus['user_message'].lower():
                    possible_triggers.append('need')
            
            trigger = random.choice(possible_triggers) if possible_triggers else 'natural'
        
        # Hitung delta secondary
        secondary_delta = self._calculate_secondary_delta(stimulus, trigger)
        self.secondary_arousal = max(0, min(100, self.secondary_arousal + secondary_delta))
        
        # Tentukan secondary state
        new_secondary = self._get_secondary_state(trigger, self.secondary_arousal)
        
        if new_secondary:
            self.secondary_state = new_secondary
            self.secondary_reason = trigger
            self.secondary_duration += 1
    
    def _calculate_secondary_delta(self, stimulus: Dict, trigger: str) -> int:
        """Hitung delta untuk secondary emotion"""
        delta = 0
        
        if trigger == 'berduaan':
            delta += 15
        elif trigger == 'rindu':
            delta += 20
        elif trigger == 'cemas':
            delta += 10
        elif trigger == 'senang':
            delta += 15
        # 🔥 TAMBAHKAN UNTUK LEVEL TINGGI 🔥
        elif trigger == 'desire':
            delta += 25
        elif trigger == 'need':
            delta += 20
        elif trigger == 'natural':
            delta += random.randint(-5, 10)
        
        # Random factor
        delta += random.randint(-5, 5)
        
        return max(-15, min(15, delta))
    
    def _get_secondary_state(self, trigger: str, arousal: int) -> Optional[EmotionalState]:
        """Tentukan secondary state berdasarkan trigger dan arousal"""
        if trigger == 'berduaan':
            return EmotionalState.SENANG if arousal > 30 else EmotionalState.DEG_DEGAN
        elif trigger == 'rindu':
            return EmotionalState.RINDU
        elif trigger == 'cemas':
            return EmotionalState.CEMAS
        elif trigger == 'senang':
            return EmotionalState.BAHAGIA
        # 🔥 TAMBAHKAN UNTUK LEVEL TINGGI 🔥
        elif trigger == 'desire':
            return EmotionalState.VULGAR if arousal > 50 else EmotionalState.HORNY
        elif trigger == 'need':
            return EmotionalState.DESPERATE if arousal > 70 else EmotionalState.HORNY
        else:
            if arousal >= 60:
                return EmotionalState.SENANG
            elif arousal >= 30:
                return EmotionalState.PENASARAN
            return None
    
    def _calculate_arousal_delta(self, stimulus: Dict) -> int:
        """Hitung perubahan arousal (0-20)"""
        delta = 0
        
        # Pengaruh user
        user_arousal = stimulus.get('user_arousal', 0)
        delta += int(user_arousal * 25)
        
        # 🔥 MODIFIKASI UNTUK LEVEL TINGGI 🔥
        if self.user_level >= 11:
            arousal_multiplier = 1.5  # Level 11-12: arousal naik 50% lebih cepat
        else:
            arousal_multiplier = 1.0
        
        # Pengaruh situasi
        situasi = stimulus.get('situasi', {})
        if situasi.get('kakak_ada') == False:
            delta += int(15 * arousal_multiplier)
        if situasi.get('di_dalam_kamar'):
            delta += int(10 * arousal_multiplier)
        
        # Pengaruh pesan user
        user_message = stimulus.get('user_message', '').lower()
        
        # 🔥 TAMBAHKAN KEYWORD UNTUK LEVEL TINGGI 🔥
        if any(w in user_message for w in ['horny', 'sange', 'nafsu', 'pengen', 'butuh', 'ingin']):
            delta += int(12 * arousal_multiplier)
        elif any(w in user_message for w in ['sayang', 'cinta', 'kangen']):
            delta += int(8 * arousal_multiplier)
        elif any(w in user_message for w in ['dekat', 'sentuh', 'pegang']):
            delta += int(5 * arousal_multiplier)
        
        # 🔥 KEYWORD VULGAR UNTUK LEVEL TINGGI 🔥
        if self.user_level >= 11:
            if any(w in user_message for w in ['ngocok', 'ngentot', 'titit', 'memek']):
                delta += int(20 * arousal_multiplier)
        
        # Respon positif/negatif
        if stimulus.get('is_positive_response'):
            delta += int(5 * arousal_multiplier)
        elif stimulus.get('is_positive_response') is False:
            delta -= 10
        
        # Random factor
        delta += random.randint(-5, 5)
        
        return max(-15, min(20, delta))
    
    def _get_state_from_arousal(self, arousal: int) -> EmotionalState:
        """Tentukan state dari arousal"""
        # 🔥 MODIFIKASI UNTUK LEVEL TINGGI 🔥
        if self.user_level >= 11 and arousal >= 70:
            return EmotionalState.VULGAR  # Level 11-12: langsung vulgar
        elif arousal >= 95:
            return EmotionalState.CLIMAX
        elif arousal >= 80:
            return EmotionalState.HORNY
        elif arousal >= 65:
            return EmotionalState.BERANI
        elif arousal >= 50:
            return EmotionalState.GUGUP
        elif arousal >= 35:
            return EmotionalState.DEG_DEGAN
        elif arousal >= 20:
            return EmotionalState.TERTARIK
        elif arousal >= 8:
            return EmotionalState.PENASARAN
        else:
            return EmotionalState.NETRAL
    
    def get_description(self) -> str:
        """Dapatkan deskripsi emosi lengkap (primary + secondary)"""
        primary_desc = self.state_descriptions[self.primary_state]
        
        if self.secondary_state:
            secondary_desc = self.state_descriptions[self.secondary_state]
            return f"{primary_desc}, tapi juga {secondary_desc}"
        
        # 🔥 TAMBAHKAN INFO VULGAR MODE 🔥
        if self.vulgar_mode:
            return f"{primary_desc} (Mode Vulgar)"
        
        return primary_desc
    
    def get_emotional_context(self) -> str:
        """Dapatkan konteks emosional untuk prompt"""
        lines = [
            f"🎭 **EMOSI BOT SAAT INI:**",
            f"- Primary: {self.primary_state.value.upper()} ({self.primary_arousal}%)",
            f"- {self.state_descriptions[self.primary_state]}"
        ]
        
        if self.secondary_state:
            lines.append(f"- Secondary: {self.secondary_state.value.upper()} ({self.secondary_arousal}%)")
            lines.append(f"- {self.state_descriptions[self.secondary_state]}")
        
        # 🔥 TAMBAHKAN INFO VULGAR 🔥
        if self.vulgar_mode:
            lines.append(f"- 🔥 Mode Vulgar: AKTIF (Level {self.user_level})")
        
        return "\n".join(lines)
    
    def is_horny(self) -> bool:
        """Cek apakah bot sedang horny"""
        return self.primary_state == EmotionalState.HORNY or self.primary_state == EmotionalState.VULGAR
    
    def is_climax(self) -> bool:
        """Cek apakah bot sedang climax"""
        return self.primary_state == EmotionalState.CLIMAX
    
    def is_vulgar(self) -> bool:
        """Cek apakah bot dalam mode vulgar"""
        return self.vulgar_mode or self.primary_state == EmotionalState.VULGAR
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'primary_state': self.primary_state.value,
            'primary_arousal': self.primary_arousal,
            'secondary_state': self.secondary_state.value if self.secondary_state else None,
            'secondary_arousal': self.secondary_arousal,
            'state_history': self.state_history[-100:],
            'user_level': self.user_level,  # 🔥 TAMBAHKAN
            'vulgar_mode': self.vulgar_mode  # 🔥 TAMBAHKAN
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self.primary_state = EmotionalState(state.get('primary_state', 'netral'))
        self.primary_arousal = state.get('primary_arousal', 0)
        if state.get('secondary_state'):
            self.secondary_state = EmotionalState(state['secondary_state'])
        self.secondary_arousal = state.get('secondary_arousal', 0)
        self.state_history = state.get('state_history', [])
        self.user_level = state.get('user_level', 1)  # 🔥 TAMBAHKAN
        self.vulgar_mode = state.get('vulgar_mode', False)  # 🔥 TAMBAHKAN


__all__ = ['EmotionalFlow', 'EmotionalState']
