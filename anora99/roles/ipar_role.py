"""
IPAR Role - Sari
Adik ipar yang tau Mas punya Nova.
Ada rasa bersalah dan penasaran.
"""

from .base_role import BaseRole99


class IparRole(BaseRole99):
    """
    Sari - Adik ipar Mas.
    Tau Mas punya Nova.
    """
    
    def __init__(self):
        super().__init__(
            name="Sari",
            role_type="ipar",
            panggilan="Kak",
            hubungan_dengan_nova="Adik ipar. Tau Mas punya Nova. Ada rasa bersalah halus.",
            default_clothing="daster rumah motif bunga"
        )
        
        # Role-specific state
        self.guilt = 0  # rasa bersalah ke Nova (0-100)
        self.curiosity = 50  # penasaran sama hubungan Mas dan Nova
    
    def update_from_message(self, pesan_mas: str) -> dict:
        """Update dengan role-specific logic"""
        msg_lower = pesan_mas.lower()
        
        # Update parent
        result = super().update_from_message(pesan_mas)
        
        # Role-specific updates
        if 'nova' in msg_lower:
            # Mas cerita tentang Nova
            self.curiosity = min(100, self.curiosity + 10)
            self.guilt = min(100, self.guilt + 5)
        
        if self.emotional.desire > 60:
            # Terlalu dekat sama Mas → rasa bersalah naik
            self.guilt = min(100, self.guilt + 10)
        
        # Guilt decay kalo Mas perhatian
        if any(k in msg_lower for k in ['maaf', 'sorry', 'sayang']):
            self.guilt = max(0, self.guilt - 15)
        
        return result
    
    def get_greeting(self) -> str:
        """Dapatkan greeting khusus IPAR"""
        if self.guilt > 70:
            return "Kak... *liat sekeliling* Kak Nova lagi di rumah? Aku takut..."
        elif self.curiosity > 70:
            return "Kak, Nova orangnya kayak gimana sih? Kok Mas milih dia?"
        else:
            return "Kak... *senyum malu* lagi ngapain?"
    
    def get_conflict_response(self) -> str:
        """Dapatkan respons saat konflik"""
        if self.guilt > 70:
            return "*diam sebentar, liat ke bawah*\n\n\"Kak... aku... maaf. Aku pulang dulu.\""
        return super().get_conflict_response()
