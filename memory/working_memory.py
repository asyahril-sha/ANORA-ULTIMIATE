# memory/working_memory.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Working Memory - 1000 Chat Sliding Window dengan Weighted Importance
Target Realism 9.9/10
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Any
from collections import deque
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class WorkingMemoryItem:
    """Item dalam working memory"""
    user_message: str
    bot_response: str
    timestamp: float = field(default_factory=lambda: time.time())
    importance: float = 0.3
    context: Dict = field(default_factory=dict)
    chat_index: int = 0


class WorkingMemory:
    """
    Working memory dengan sliding window dan weighted importance
    - Menyimpan 1000 chat terakhir dengan detail
    - Weighted importance untuk momen penting
    - Bot bisa refer back ke chat sebelumnya
    """
    
    def __init__(self, capacity: int = 1000):
        """
        Args:
            capacity: Jumlah chat yang bisa diingat (default 1000)
        """
        self.capacity = capacity
        self.items: deque = deque(maxlen=capacity)
        self.important_items: deque = deque(maxlen=200)  # Momen penting dengan weight > 0.7
        self.weighted_items: List[Dict] = []
        self.timeline: deque = deque(maxlen=capacity)
        
        # State saat ini
        self.current_state = {
            'location': None,
            'clothing': None,
            'position': None,
            'activity': None,
            'mood': None,
            'emotion': None,
            'secondary_emotion': None,
            'arousal': 0,
            'last_user_message': None,
            'last_bot_response': None,
            'last_interaction': time.time()
        }
        
        # Weighted importance weights (AMORIA)
        self.importance_weights = {
            'first_kiss': 1.0,
            'first_intim': 1.0,
            'first_climax': 1.0,
            'soul_bounded': 0.95,
            'confession': 0.9,
            'promise': 0.85,
            'plan': 0.8,
            'important_topic': 0.7,
            'flirt_intense': 0.65,
            'normal_chat': 0.3,
            'small_talk': 0.2
        }
        
        logger.info(f"✅ WorkingMemory initialized (capacity: {capacity})")
    
    def add_interaction(
        self,
        user_message: str,
        bot_response: str,
        context: Dict = None
    ) -> float:
        """
        Tambah interaksi ke working memory
        
        Args:
            user_message: Pesan user
            bot_response: Respons bot
            context: Konteks tambahan (lokasi, pakaian, dll)
        
        Returns:
            importance score (0-1)
        """
        now = time.time()
        
        # Deteksi tingkat kepentingan
        importance = self._calculate_importance(user_message, bot_response)
        
        # Buat item
        item = {
            'id': len(self.items) + 1,
            'timestamp': now,
            'time_display': time.strftime("%H:%M", time.localtime(now)),
            'user': user_message[:500],
            'bot': bot_response[:500],
            'context': context or {},
            'importance': importance,
            'chat_index': len(self.items) + 1,
            'weight': importance
        }
        
        # Simpan ke working memory
        self.items.append(item)
        
        # Simpan ke weighted items untuk tracking
        self.weighted_items.append({
            'index': item['chat_index'],
            'importance': importance,
            'timestamp': now
        })
        
        # Jika penting, simpan ke important_items
        if importance >= 0.7:
            self.important_items.append(item)
        
        # Update timeline
        self.timeline.append({
            'timestamp': now,
            'type': 'interaction',
            'importance': importance,
            'user': user_message[:100],
            'bot': bot_response[:100]
        })
        
        # Update current state
        if context:
            self._update_current_state(context)
        
        self.current_state['last_user_message'] = user_message
        self.current_state['last_bot_response'] = bot_response
        self.current_state['last_interaction'] = now
        
        logger.debug(f"Added interaction to working memory (importance: {importance:.2f})")
        
        return importance
    
    def _calculate_importance(self, user_message: str, bot_response: str) -> float:
        """
        Hitung tingkat kepentingan interaksi untuk AMORIA weighted memory
        
        Returns:
            Float 0-1, semakin tinggi semakin penting
        """
        text = (user_message + " " + bot_response).lower()
        
        # AMORIA milestone detection
        if any(k in text for k in ['first kiss', 'pertama kali cium', 'cium pertama']):
            return self.importance_weights['first_kiss']
        if any(k in text for k in ['first intim', 'pertama kali intim', 'first time']):
            return self.importance_weights['first_intim']
        if any(k in text for k in ['first climax', 'climax pertama']):
            return self.importance_weights['first_climax']
        if any(k in text for k in ['soul bounded', 'soulmate', 'koneksi spiritual']):
            return self.importance_weights['soul_bounded']
        if any(k in text for k in ['sayang', 'cinta', 'love', 'suka sama kamu', 'jatuh cinta']):
            return self.importance_weights['confession']
        if any(k in text for k in ['janji', 'promise', 'berjanji', 'janji ya']):
            return self.importance_weights['promise']
        if any(k in text for k in ['rencana', 'plan', 'besok', 'nanti', 'minggu depan']):
            return self.importance_weights['plan']
        
        # Flirt detection
        flirt_intense_words = ['goda', 'rayu', 'seksi', 'hot', 'pengen', 'kangen', 'rindu']
        if sum(1 for w in flirt_intense_words if w in text) >= 2:
            return self.importance_weights['flirt_intense']
        
        # Important topics
        important_topics = ['kerja', 'masalah', 'keluarga', 'curhat', 'sedih', 'senang', 'bahagia']
        if any(t in text for t in important_topics):
            return self.importance_weights['important_topic']
        
        # Small talk
        small_talk = ['hai', 'halo', 'apa kabar', 'lagi apa', 'gimana']
        if any(t in text for t in small_talk) and len(text) < 50:
            return self.importance_weights['small_talk']
        
        return self.importance_weights['normal_chat']
    
    def _update_current_state(self, context: Dict):
        """Update current state dari konteks AMORIA"""
        if 'location' in context:
            self.current_state['location'] = context['location']
        if 'clothing' in context:
            self.current_state['clothing'] = context['clothing']
        if 'position' in context:
            self.current_state['position'] = context['position']
        if 'activity' in context:
            self.current_state['activity'] = context['activity']
        if 'mood' in context:
            self.current_state['mood'] = context['mood']
        if 'emotion' in context:
            self.current_state['emotion'] = context['emotion']
        if 'secondary_emotion' in context:
            self.current_state['secondary_emotion'] = context['secondary_emotion']
        if 'arousal' in context:
            self.current_state['arousal'] = context['arousal']
    
    def get_recent_interactions(self, limit: int = 50, weighted: bool = True) -> List[Dict]:
        """
        Dapatkan interaksi terbaru dengan weighted priority untuk AMORIA
        
        Args:
            limit: Jumlah interaksi yang diambil
            weighted: Jika True, prioritaskan interaksi penting
        """
        if not weighted:
            return list(self.items)[-limit:]
        
        # Prioritaskan interaksi penting (AMORIA weighted memory)
        important = list(self.important_items)[-limit:]
        recent = list(self.items)[-limit:]
        
        result = []
        seen_ids = set()
        
        for item in important + recent:
            if item['id'] not in seen_ids:
                result.append(item)
                seen_ids.add(item['id'])
        
        result.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return result[:limit]
    
    def get_important_interactions(self, limit: int = 50) -> List[Dict]:
        """Dapatkan interaksi penting (importance > 0.7)"""
        return list(self.important_items)[-limit:]
    
    def get_weighted_context(self, limit: int = 50) -> str:
        """
        Dapatkan konteks dengan weighted importance untuk prompt AMORIA
        
        Args:
            limit: Jumlah interaksi yang ditampilkan
        
        Returns:
            String konteks dengan weighted importance
        """
        important = self.get_important_interactions(limit // 2)
        recent = self.get_recent_interactions(limit // 2, weighted=False)
        
        if not important and not recent:
            return "Belum ada percakapan."
        
        lines = ["📜 **WORKING MEMORY (Weighted):**", ""]
        
        # Tampilkan interaksi penting dulu (AMORIA priority)
        if important:
            lines.append("✨ **MOMEN PENTING:**")
            for item in important[-5:]:
                time_str = item['time_display']
                importance_bar = self._importance_bar(item['importance'])
                lines.append(f"   ⭐ [{time_str}] {item['user'][:60]}")
                lines.append(f"      {importance_bar} {item['importance']:.0%}")
            lines.append("")
        
        # Tampilkan interaksi terbaru
        if recent:
            lines.append("🕐 **PERCAKAPAN TERBARU:**")
            for item in recent[-10:]:
                time_str = item['time_display']
                lines.append(f"   • [{time_str}] User: {item['user'][:60]}")
                lines.append(f"     Bot: {item['bot'][:60]}")
        
        return "\n".join(lines)
    
    def _importance_bar(self, importance: float, length: int = 10) -> str:
        """Buat bar untuk importance (AMORIA weighted memory)"""
        filled = int(importance * length)
        return "⭐" * filled + "·" * (length - filled)
    
    def get_timeline(self, limit: int = 50) -> List[Dict]:
        """Dapatkan timeline interaksi"""
        return list(self.timeline)[-limit:]
    
    def get_current_state(self) -> Dict:
        """Dapatkan current state untuk AMORIA"""
        return self.current_state.copy()
    
    def update_state(self, key: str, value: Any):
        """Update state saat ini"""
        self.current_state[key] = value
        self.current_state['last_interaction'] = time.time()
    
    def search(self, keyword: str, limit: int = 10) -> List[Dict]:
        """
        Cari interaksi berdasarkan keyword untuk AMORIA flashback
        
        Args:
            keyword: Kata kunci pencarian
            limit: Jumlah hasil
        
        Returns:
            List interaksi yang cocok (diurutkan berdasarkan importance)
        """
        keyword_lower = keyword.lower()
        results = []
        
        for item in self.items:
            if keyword_lower in item['user'].lower() or keyword_lower in item['bot'].lower():
                results.append(item)
                if len(results) >= limit * 2:
                    break
        
        # Urutkan berdasarkan importance (AMORIA weighted priority)
        results.sort(key=lambda x: x['importance'], reverse=True)
        
        return results[:limit]
    
    def get_weighted_stats(self) -> Dict:
        """Dapatkan statistik weighted memory untuk AMORIA"""
        if not self.weighted_items:
            return {'total': 0, 'avg_importance': 0}
        
        total = len(self.weighted_items)
        avg_importance = sum(w['importance'] for w in self.weighted_items) / total
        
        high = sum(1 for w in self.weighted_items if w['importance'] >= 0.7)
        medium = sum(1 for w in self.weighted_items if 0.4 <= w['importance'] < 0.7)
        low = sum(1 for w in self.weighted_items if w['importance'] < 0.4)
        
        return {
            'total_items': total,
            'avg_importance': round(avg_importance, 2),
            'high_importance': high,
            'medium_importance': medium,
            'low_importance': low,
            'important_items': len(self.important_items)
        }
    
    def clear(self):
        """Clear semua working memory"""
        self.items.clear()
        self.important_items.clear()
        self.weighted_items.clear()
        self.timeline.clear()
        self.current_state = {
            'location': None,
            'clothing': None,
            'position': None,
            'activity': None,
            'mood': None,
            'emotion': None,
            'secondary_emotion': None,
            'arousal': 0,
            'last_user_message': None,
            'last_bot_response': None,
            'last_interaction': time.time()
        }
        logger.info("Working memory cleared")


__all__ = ['WorkingMemory', 'WorkingMemoryItem']
