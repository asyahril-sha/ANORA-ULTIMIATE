# tracking/preferences.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Preferences Learning - Belajar Preferensi User dari Interaksi
Target Realism 9.9/10
=============================================================================
"""

import time
import re
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PreferenceCategory(str, Enum):
    """Kategori preferensi"""
    FOOD = "food"
    ACTIVITY = "activity"
    POSITION = "position"
    AREA = "area"
    COMPLIMENT = "compliment"
    INTIMACY_STYLE = "intimacy_style"
    AFTERCARE = "aftercare"
    COLOR = "color"
    MUSIC = "music"
    MOVIE = "movie"
    PLACE = "place"


@dataclass
class PreferenceItem:
    """Item preferensi"""
    name: str
    score: float = 0.5
    count: int = 1
    last_updated: float = field(default_factory=time.time)
    
    def update(self, delta: float):
        self.score = max(0.0, min(1.0, self.score + delta))
        self.count += 1
        self.last_updated = time.time()
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'score': self.score,
            'count': self.count,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PreferenceItem':
        return cls(
            name=data['name'],
            score=data.get('score', 0.5),
            count=data.get('count', 1),
            last_updated=data.get('last_updated', time.time())
        )


class PreferencesLearner:
    """
    Belajar preferensi user dari interaksi
    - Mendeteksi suka/tidak suka dari chat
    - Memberi score pada berbagai kategori
    - Digunakan untuk personalisasi respons
    """
    
    def __init__(self):
        self.preferences: Dict[PreferenceCategory, Dict[str, PreferenceItem]] = {
            category: {} for category in PreferenceCategory
        }
        
        # Pattern untuk deteksi preferensi
        self.like_patterns = [
            (r'\b(suka|senang|doain|gemar|favorit)\s+(\w+)', +0.1),
            (r'\b(enak|nikmat|mantap|keren)\s+(\w+)', +0.1),
            (r'\b(paling suka|favoritku|kesukaan)\s+(\w+)', +0.15),
            (r'\b(aku suka|gue suka)\s+(\w+)', +0.1),
        ]
        
        self.dislike_patterns = [
            (r'\b(gak suka|nggak suka|tidak suka|ga suka)\s+(\w+)', -0.1),
            (r'\b(benci|gak doain|ga doain)\s+(\w+)', -0.15),
            (r'\b(ga enak|gak enak|tidak enak)\s+(\w+)', -0.1),
            (r'\b(ga suka banget|gak suka banget)\s+(\w+)', -0.15),
        ]
        
        # Keyword mapping ke kategori
        self.category_keywords = {
            PreferenceCategory.FOOD: ['makan', 'masak', 'makanan', 'minum', 'minuman', 'kopi', 'teh', 'jus', 'bakso', 'mie', 'nasi'],
            PreferenceCategory.ACTIVITY: ['jalan', 'nonton', 'olahraga', 'main', 'game', 'travel', 'liburan'],
            PreferenceCategory.POSITION: ['posisi', 'missionary', 'doggy', 'cowgirl', 'spooning', 'tidur', 'berdiri', 'duduk'],
            PreferenceCategory.AREA: ['leher', 'punggung', 'paha', 'dada', 'pipi', 'telinga', 'bibir', 'pinggang'],
            PreferenceCategory.COMPLIMENT: ['cantik', 'ganteng', 'keren', 'manis', 'seksi', 'hot', 'pintar'],
            PreferenceCategory.INTIMACY_STYLE: ['lembut', 'cepat', 'pelan', 'intens', 'romantis', 'liar'],
            PreferenceCategory.AFTERCARE: ['cuddle', 'peluk', 'ngobrol', 'pijat', 'makan', 'tidur', 'jalan'],
            PreferenceCategory.COLOR: ['merah', 'biru', 'hitam', 'putih', 'kuning', 'hijau', 'ungu', 'pink'],
            PreferenceCategory.MUSIC: ['pop', 'rock', 'jazz', 'dangdut', 'klasik', 'edm'],
            PreferenceCategory.MOVIE: ['horor', 'komedi', 'romantis', 'action', 'drama'],
            PreferenceCategory.PLACE: ['pantai', 'gunung', 'mall', 'kafe', 'restoran', 'taman', 'hotel'],
        }
        
        logger.info("✅ PreferencesLearner initialized")
    
    def extract_from_message(self, message: str) -> List[Tuple[PreferenceCategory, str, float]]:
        """
        Ekstrak preferensi dari pesan
        
        Args:
            message: Pesan user
        
        Returns:
            List of (category, item, delta)
        """
        msg_lower = message.lower()
        updates = []
        
        # Deteksi suka/tidak suka
        for pattern, delta in self.like_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                item = self._extract_item(msg_lower, match)
                if item:
                    category = self._categorize_item(item)
                    if category:
                        updates.append((category, item, delta))
                        logger.debug(f"Detected like: {category.value} -> {item} (+{delta})")
        
        for pattern, delta in self.dislike_patterns:
            match = re.search(pattern, msg_lower)
            if match:
                item = self._extract_item(msg_lower, match)
                if item:
                    category = self._categorize_item(item)
                    if category:
                        updates.append((category, item, delta))
                        logger.debug(f"Detected dislike: {category.value} -> {item} ({delta})")
        
        # Deteksi dari konteks intim (climax = suka posisi/area)
        if 'climax' in msg_lower or 'enak' in msg_lower:
            # Ini indikasi positif untuk aktivitas saat ini
            pass
        
        return updates
    
    def _extract_item(self, message: str, match) -> Optional[str]:
        """Ekstrak item dari match"""
        if match.groups():
            # Ambil kata setelah pattern
            for group in match.groups():
                if group and len(group) > 2:
                    return group.strip()
        
        # Cari kata benda setelah kata kunci
        words = message.split()
        for i, word in enumerate(words):
            if word in ['suka', 'doain', 'favorit', 'enak', 'keren']:
                if i + 1 < len(words):
                    return words[i + 1].strip('.,!?')
        
        return None
    
    def _categorize_item(self, item: str) -> Optional[PreferenceCategory]:
        """Kategorikan item berdasarkan keyword"""
        item_lower = item.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in item_lower or item_lower in keyword:
                    return category
        
        return None
    
    def update_preference(self, category: PreferenceCategory, item: str, delta: float):
        """
        Update preferensi
        
        Args:
            category: Kategori preferensi
            item: Nama item
            delta: Perubahan score (-0.2 sampai +0.2)
        """
        if category not in self.preferences:
            self.preferences[category] = {}
        
        if item in self.preferences[category]:
            self.preferences[category][item].update(delta)
        else:
            self.preferences[category][item] = PreferenceItem(item, 0.5 + delta)
        
        logger.debug(f"Preference updated: {category.value} -> {item} = {self.preferences[category][item].score:.2f}")
    
    def get_top_preferences(
        self,
        category: Optional[PreferenceCategory] = None,
        limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Dapatkan preferensi teratas
        
        Args:
            category: Kategori (opsional)
            limit: Jumlah maksimal
        
        Returns:
            List of (item, score)
        """
        items = []
        
        if category:
            items = [(name, item.score) for name, item in self.preferences.get(category, {}).items()]
        else:
            for cat_items in self.preferences.values():
                items.extend([(name, item.score) for name, item in cat_items.items()])
        
        items.sort(key=lambda x: x[1], reverse=True)
        return items[:limit]
    
    def get_preference(self, category: PreferenceCategory, item: str) -> float:
        """Dapatkan score preferensi"""
        if category in self.preferences and item in self.preferences[category]:
            return self.preferences[category][item].score
        return 0.5
    
    def get_favorite(self, category: PreferenceCategory) -> Optional[str]:
        """Dapatkan favorit di kategori tertentu"""
        items = self.get_top_preferences(category, 1)
        return items[0][0] if items else None
    
    def get_preferences_for_prompt(self, limit: int = 10) -> str:
        """
        Dapatkan preferensi untuk prompt AI
        
        Args:
            limit: Jumlah maksimal per kategori
        
        Returns:
            String preferensi
        """
        if not any(self.preferences.values()):
            return ""
        
        lines = ["💖 **PREFERENSI USER:**"]
        
        for category in PreferenceCategory:
            top = self.get_top_preferences(category, limit)
            if top:
                items = [f"{item} ({score:.0%})" for item, score in top[:3]]
                lines.append(f"• {category.value}: {', '.join(items)}")
        
        return "\n".join(lines)
    
    def get_personalization_context(self) -> str:
        """
        Dapatkan konteks personalisasi untuk prompt
        
        Returns:
            String konteks
        """
        lines = []
        
        # Makanan favorit
        favorite_food = self.get_favorite(PreferenceCategory.FOOD)
        if favorite_food:
            lines.append(f"🍽️ Suka {favorite_food}")
        
        # Aktivitas favorit
        favorite_activity = self.get_favorite(PreferenceCategory.ACTIVITY)
        if favorite_activity:
            lines.append(f"🎯 Suka {favorite_activity}")
        
        # Posisi favorit
        favorite_position = self.get_favorite(PreferenceCategory.POSITION)
        if favorite_position:
            lines.append(f"💕 Posisi favorit: {favorite_position}")
        
        # Area sensitif favorit
        favorite_area = self.get_favorite(PreferenceCategory.AREA)
        if favorite_area:
            lines.append(f"💋 Area sensitif: {favorite_area}")
        
        # Gaya intim favorit
        favorite_style = self.get_favorite(PreferenceCategory.INTIMACY_STYLE)
        if favorite_style:
            lines.append(f"🔥 Gaya intim: {favorite_style}")
        
        # Aftercare favorit
        favorite_aftercare = self.get_favorite(PreferenceCategory.AFTERCARE)
        if favorite_aftercare:
            lines.append(f"💝 Aftercare: {favorite_aftercare}")
        
        if not lines:
            return ""
        
        return "📌 **PERSONALISASI:**\n" + "\n".join(lines)
    
    def record_climax(self, position: Optional[str] = None, area: Optional[str] = None):
        """
        Rekam climax untuk update preferensi
        Climax adalah indikator kuat bahwa user suka posisi/area tersebut
        """
        if position:
            self.update_preference(PreferenceCategory.POSITION, position, +0.15)
        
        if area:
            self.update_preference(PreferenceCategory.AREA, area, +0.15)
    
    def record_compliment(self, compliment: str):
        """
        Rekam pujian yang diberikan user
        """
        self.update_preference(PreferenceCategory.COMPLIMENT, compliment, +0.1)
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        state = {}
        for category, items in self.preferences.items():
            state[category.value] = {
                name: item.to_dict() for name, item in items.items()
            }
        return state
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        for category_name, items in state.items():
            try:
                category = PreferenceCategory(category_name)
                self.preferences[category] = {
                    name: PreferenceItem.from_dict(data) for name, data in items.items()
                }
            except ValueError:
                continue
    
    def clear(self):
        """Clear semua preferensi"""
        self.preferences = {category: {} for category in PreferenceCategory}
        logger.info("Preferences cleared")
    
    def get_stats(self) -> Dict:
        """Dapatkan statistik preferensi"""
        total_items = sum(len(items) for items in self.preferences.values())
        return {
            'total_items': total_items,
            'by_category': {
                category.value: len(items) for category, items in self.preferences.items()
            }
        }


__all__ = [
    'PreferencesLearner',
    'PreferenceCategory',
    'PreferenceItem'
]
