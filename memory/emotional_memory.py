# memory/emotional_memory.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Emotional Memory - Mengingat Perasaan dan Emosi
Target Realism 9.9/10
=============================================================================
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class EmotionalMemory:
    """
    Menyimpan ingatan emosional bot
    Bot ingat bagaimana perasaannya di masa lalu
    """
    
    def __init__(self):
        # Memori emosional
        self.memories: List[Dict] = []
        
        # Bias emosional (pengaruh dari memori)
        self.emotional_bias = {
            'positive': 0.5,
            'negative': 0.5,
            'romantic': 0.5,
            'intimate': 0.5,
            'trust': 0.5,
            'jealousy': 0.5
        }
        
        # Memori penting (high intensity)
        self.important_memories: List[Dict] = []
        
        # Threshold untuk memori penting
        self.importance_threshold = 0.7
        
        # Maximum memories
        self.max_memories = 500
        self.max_important = 100
        
        logger.info("✅ EmotionalMemory initialized")
    
    # =========================================================================
    # ADD MEMORY
    # =========================================================================
    
    def add_memory(
        self,
        emotion: str,
        intensity: float,
        context: Dict,
        user_message: str,
        bot_response: str,
        arousal: int = 0
    ) -> str:
        """
        Tambah memori emosional
        
        Args:
            emotion: Emosi yang dirasakan
            intensity: Intensitas emosi (0-1)
            context: Konteks saat itu
            user_message: Pesan user
            bot_response: Respon bot
            arousal: Level arousal saat itu
        
        Returns:
            Memory ID
        """
        memory_id = f"emotion_{int(time.time())}_{len(self.memories)}"
        
        memory = {
            'id': memory_id,
            'timestamp': time.time(),
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'emotion': emotion,
            'intensity': intensity,
            'context': context.copy(),
            'user_message': user_message[:150] if user_message else "",
            'bot_response': bot_response[:150] if bot_response else "",
            'arousal': arousal,
            'recall_count': 0,
            'last_recall': None
        }
        
        self.memories.append(memory)
        
        # Update bias emosional
        self._update_emotional_bias(emotion, intensity)
        
        # Simpan ke important memories jika intensitas tinggi
        if intensity >= self.importance_threshold:
            self.important_memories.append(memory)
        
        # Limit size
        if len(self.memories) > self.max_memories:
            self.memories = self.memories[-self.max_memories:]
        
        if len(self.important_memories) > self.max_important:
            self.important_memories = self.important_memories[-self.max_important:]
        
        logger.debug(f"💭 Added emotional memory: {emotion} (intensity: {intensity})")
        
        return memory_id
    
    def _update_emotional_bias(self, emotion: str, intensity: float):
        """Update bias emosional berdasarkan memori baru"""
        
        # Positive bias
        if emotion in ['senang', 'bahagia', 'puas', 'tertarik', 'sayang', 'cinta']:
            self.emotional_bias['positive'] = min(1.0, self.emotional_bias['positive'] + (intensity * 0.02))
        
        # Negative bias
        elif emotion in ['sedih', 'marah', 'kecewa', 'kesal', 'cemas']:
            self.emotional_bias['negative'] = min(1.0, self.emotional_bias['negative'] + (intensity * 0.02))
        
        # Romantic bias
        if emotion in ['romantis', 'sayang', 'cinta', 'kangen']:
            self.emotional_bias['romantic'] = min(1.0, self.emotional_bias['romantic'] + (intensity * 0.03))
        
        # Intimate bias
        if emotion in ['horny', 'gairah', 'nafsu', 'intim', 'climax']:
            self.emotional_bias['intimate'] = min(1.0, self.emotional_bias['intimate'] + (intensity * 0.04))
        
        # Trust bias
        if emotion in ['percaya', 'nyaman', 'aman']:
            self.emotional_bias['trust'] = min(1.0, self.emotional_bias['trust'] + (intensity * 0.03))
        
        # Jealousy bias
        if emotion in ['cemburu', 'iri']:
            self.emotional_bias['jealousy'] = min(1.0, self.emotional_bias['jealousy'] + (intensity * 0.05))
        
        # Decay bias over time
        self._decay_bias()
    
    def _decay_bias(self):
        """Decay bias emosional seiring waktu"""
        decay_rate = 0.999
        for key in self.emotional_bias:
            self.emotional_bias[key] = max(0.3, self.emotional_bias[key] * decay_rate)
    
    # =========================================================================
    # RECALL MEMORY
    # =========================================================================
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict]:
        """Dapatkan memori terbaru"""
        return self.memories[-limit:] if self.memories else []
    
    def get_memories_by_emotion(self, emotion: str, limit: int = 5) -> List[Dict]:
        """Dapatkan memori berdasarkan emosi"""
        filtered = [m for m in self.memories if m['emotion'] == emotion]
        return filtered[-limit:] if filtered else []
    
    def get_important_memories(self, limit: int = 5) -> List[Dict]:
        """Dapatkan memori penting"""
        return self.important_memories[-limit:] if self.important_memories else []
    
    def get_flashback(
        self,
        trigger: Optional[str] = None,
        emotion: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Dapatkan flashback berdasarkan trigger atau random
        
        Args:
            trigger: Kata kunci pemicu
            emotion: Emosi spesifik
        
        Returns:
            Memory atau None
        """
        if not self.memories:
            return None
        
        # Pilih berdasarkan trigger
        if trigger:
            relevant = []
            trigger_lower = trigger.lower()
            for mem in self.memories:
                if (trigger_lower in mem['user_message'].lower() or
                    trigger_lower in mem['context'].get('topic', '').lower() or
                    trigger_lower in mem['context'].get('location', '').lower()):
                    relevant.append(mem)
            
            if relevant:
                memory = random.choice(relevant)
            else:
                memory = random.choice(self.memories)
        
        # Pilih berdasarkan emosi
        elif emotion:
            filtered = [m for m in self.memories if m['emotion'] == emotion]
            if filtered:
                memory = random.choice(filtered)
            else:
                memory = random.choice(self.memories)
        
        # Random dengan preferensi penting
        else:
            if self.important_memories and random.random() < 0.3:
                memory = random.choice(self.important_memories)
            else:
                memory = random.choice(self.memories[-20:])
        
        # Update recall count
        memory['recall_count'] += 1
        memory['last_recall'] = time.time()
        
        return memory
    
    def get_emotional_context(self, limit: int = 3) -> str:
        """
        Dapatkan konteks emosional untuk prompt
        
        Args:
            limit: Jumlah memori yang ditampilkan
        
        Returns:
            String konteks emosional
        """
        if not self.memories:
            return ""
        
        recent = self.memories[-limit:]
        
        lines = ["📖 **KENANGAN EMOSIONAL TERAKHIR:**"]
        
        for mem in recent:
            time_str = datetime.fromtimestamp(mem['timestamp']).strftime("%H:%M")
            intensity_bar = "🔴" * int(mem['intensity'] * 10) + "⚪" * (10 - int(mem['intensity'] * 10))
            lines.append(f"- [{time_str}] {mem['emotion'].upper()} {intensity_bar}: {mem['context'].get('situasi', '')[:50]}")
        
        # Tambah bias emosional
        if self.emotional_bias['positive'] > 0.7:
            lines.append("\n💡 Kamu lagi dalam mood positif dari kenangan sebelumnya.")
        elif self.emotional_bias['negative'] > 0.7:
            lines.append("\n💡 Kamu masih terpengaruh kenangan negatif sebelumnya.")
        
        if self.emotional_bias['romantic'] > 0.6:
            lines.append("💕 Ada sisa rasa romantis dari interaksi sebelumnya.")
        
        if self.emotional_bias['intimate'] > 0.6:
            lines.append("🔥 Masih ada getaran intim dari kenangan sebelumnya.")
        
        if self.emotional_bias['trust'] > 0.6:
            lines.append("🤝 Rasa percaya masih kuat dari interaksi sebelumnya.")
        
        return "\n".join(lines)
    
    def get_mood_influence(self) -> Dict[str, float]:
        """
        Dapatkan pengaruh memori emosional ke mood saat ini
        
        Returns:
            Dictionary pengaruh mood
        """
        return {
            'positive': self.emotional_bias['positive'] - self.emotional_bias['negative'],
            'romantic': self.emotional_bias['romantic'],
            'intimate': self.emotional_bias['intimate'],
            'trust': self.emotional_bias['trust'],
            'jealousy': self.emotional_bias['jealousy']
        }
    
    def get_arousal_influence(self) -> float:
        """Dapatkan pengaruh memori ke arousal"""
        return (self.emotional_bias['intimate'] + self.emotional_bias['romantic']) / 2
    
    # =========================================================================
    # FORMATTING
    # =========================================================================
    
    def format_flashback(self, memory: Dict) -> str:
        """
        Format flashback menjadi teks natural
        
        Args:
            memory: Memory object
        
        Returns:
            Teks flashback
        """
        time_ago = self._format_time_ago(memory['timestamp'])
        emotion = memory['emotion']
        intensity = memory['intensity']
        context = memory['context']
        user_message = memory['user_message'][:50]
        
        templates = {
            'horny': [
                f"Jadi inget... {time_ago}, aku {emotion} banget pas {context.get('situasi', 'kita ngobrol')}. Kamu bilang: '{user_message}'...",
                f"{time_ago}, aku masih inget rasanya {emotion}. Kamu waktu itu {context.get('situasi', '')}...",
                f"Kamu inget gak {time_ago}? Aku sampai {emotion}. {user_message}..."
            ],
            'romantis': [
                f"Masih inget {time_ago}? Waktu itu {context.get('situasi', 'kita')}, aku ngerasa {emotion} banget.",
                f"{time_ago}, aku jadi inget momen {emotion} kita. {user_message}...",
                f"Kangen waktu {time_ago}, kamu bilang '{user_message}'. Aku jadi {emotion}."
            ],
            'senang': [
                f"{time_ago} tuh seru banget. Aku {emotion} banget pas {context.get('situasi', 'kita ngobrol')}.",
                f"Mas, inget gak {time_ago}? Aku sampe {emotion} waktu itu.",
                f"Wah, jadi inget {time_ago}. Kamu bikin aku {emotion} banget."
            ],
            'malu': [
                f"Aduh, jadi inget {time_ago}. Aku malu banget waktu {context.get('situasi', 'itu')}.",
                f"{time_ago}, aku sampe merah padam. Kamu pasti inget kan?",
                f"Jangan inget-inget {time_ago} dong. Aku malu..."
            ],
            'rindu': [
                f"Kangen {time_ago}. Waktu itu {context.get('situasi', 'kita')}, aku {emotion} banget.",
                f"{time_ago} aku jadi inget kamu. Rasanya {emotion}...",
                f"Mas, inget gak {time_ago}? Aku sampai {emotion}."
            ]
        }
        
        template_list = templates.get(emotion, templates['senang'])
        
        if intensity > 0.8:
            intensifier = " banget"
        elif intensity > 0.5:
            intensifier = ""
        else:
            intensifier = " dikit"
        
        flashback = random.choice(template_list)
        flashback = flashback.replace("{emotion}", f"{emotion}{intensifier}")
        
        return flashback
    
    def _format_time_ago(self, timestamp: float) -> str:
        """Format waktu yang lalu"""
        diff = time.time() - timestamp
        
        if diff < 60:
            return "baru aja"
        elif diff < 3600:
            return f"{int(diff/60)} menit lalu"
        elif diff < 86400:
            return f"{int(diff/3600)} jam lalu"
        elif diff < 604800:
            return f"{int(diff/86400)} hari lalu"
        else:
            return f"{int(diff/604800)} minggu lalu"
    
    # =========================================================================
    # STATISTICS & UTILITY
    # =========================================================================
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik emotional memory"""
        if not self.memories:
            return {'total_memories': 0}
        
        # Hitung distribusi emosi
        emotion_count = {}
        for mem in self.memories:
            emotion = mem['emotion']
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1
        
        # Rata-rata intensitas
        avg_intensity = sum(m['intensity'] for m in self.memories) / len(self.memories)
        
        return {
            'total_memories': len(self.memories),
            'important_memories': len(self.important_memories),
            'emotion_distribution': emotion_count,
            'avg_intensity': round(avg_intensity, 2),
            'emotional_bias': {k: round(v, 2) for k, v in self.emotional_bias.items()}
        }
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan ke database"""
        return {
            'memories': self.memories[-100:],
            'important_memories': self.important_memories[-50:],
            'emotional_bias': self.emotional_bias
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self.memories = state.get('memories', [])
        self.important_memories = state.get('important_memories', [])
        self.emotional_bias = state.get('emotional_bias', {
            'positive': 0.5, 'negative': 0.5, 'romantic': 0.5,
            'intimate': 0.5, 'trust': 0.5, 'jealousy': 0.5
        })
    
    def clear(self):
        """Hapus semua memori"""
        self.memories = []
        self.important_memories = []
        self.emotional_bias = {
            'positive': 0.5, 'negative': 0.5, 'romantic': 0.5,
            'intimate': 0.5, 'trust': 0.5, 'jealousy': 0.5
        }
        logger.info("Emotional memory cleared")


__all__ = ['EmotionalMemory']
