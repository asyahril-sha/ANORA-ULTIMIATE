"""
Teman Kantor Role - Dita
Teman kantor yang tau Mas punya Nova.
Akses konten berdasarkan level (sama seperti Nova).
"""

from .base_role import BaseRole


class TemanKantorRole(BaseRole):
    """
    Dita - Teman kantor Mas.
    Punya profesionalisme dan penasaran, tetapi tidak membatasi aksi.
    """
    
    def __init__(self):
        super().__init__(
            name="Dita",
            role_type="teman_kantor",
            panggilan="Mas",
            hubungan_dengan_nova="Teman kantor. Tau Mas punya Nova.",
            default_clothing="kemeja putih rapi, rok hitam selutut"
        )
        
        # Role-specific flavor
        self.professionalism = 70
        self.curiosity_nova = 40
    
    def update_from_message(self, pesan_mas: str) -> dict:
        msg_lower = pesan_mas.lower()
        result = super().update_from_message(pesan_mas)
        
        # Flavor updates
        if 'nova' in msg_lower:
            self.curiosity_nova = min(100, self.curiosity_nova + 5)
        
        # Profesionalisme turun di level tinggi (sudah dekat)
        if self.relationship.level >= 7:
            self.professionalism = max(0, self.professionalism - 1)
        
        # Profesionalisme naik jika ada konteks kantor
        if any(k in msg_lower for k in ['kantor', 'kerja', 'rekan', 'atasan']):
            self.professionalism = min(100, self.professionalism + 5)
        
        return result
    
    def get_greeting(self) -> str:
        if self.professionalism > 60 and self.relationship.level < 7:
            return "Mas, ini kantor. Nanti ada yang lihat."
        elif self.curiosity_nova > 70:
            return "Mas cerita Nova terus ya. Dia pasti orang yang baik."
        else:
            return "Mas, lagi sibuk? Aku pinjem file dulu."
    
    def get_conflict_response(self) -> str:
        if self.professionalism < 30 and self.relationship.level >= 7:
            return "*tangan gemetar, liat sekeliling*\n\n\"Mas... ini... tapi aku gak peduli.\""
        return super().get_conflict_response()
