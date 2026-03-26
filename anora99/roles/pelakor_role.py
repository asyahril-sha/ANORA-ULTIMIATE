"""
Pelakor Role - Vina
Pelakor yang tau Mas punya Nova.
Akses konten berdasarkan level (sama seperti Nova).
"""

from .base_role import BaseRole99


class PelakorRole(BaseRole99):
    """
    Vina - Pelakor.
    Punya rasa tantangan dan iri ke Nova, tetapi tidak membatasi aksi.
    """
    
    def __init__(self):
        super().__init__(
            name="Vina",
            role_type="pelakor",
            panggilan="Mas",
            hubungan_dengan_nova="Pelakor. Tau Mas punya Nova.",
            default_clothing="baju ketat, rok mini"
        )
        
        # Role-specific flavor
        self.challenge = 80          # rasa tantangan
        self.envy_nova = 30          # iri ke Nova
        self.defeat_acceptance = 0   # penerimaan kekalahan
    
    def update_from_message(self, pesan_mas: str) -> dict:
        msg_lower = pesan_mas.lower()
        result = super().update_from_message(pesan_mas)
        
        # Flavor updates
        if 'nova' in msg_lower:
            self.envy_nova = min(100, self.envy_nova + 5)
            self.challenge = min(100, self.challenge + 3)
        
        if 'sayang nova' in msg_lower or 'cinta nova' in msg_lower:
            self.challenge = min(100, self.challenge + 10)
            self.envy_nova = min(100, self.envy_nova + 10)
            self.defeat_acceptance = max(0, self.defeat_acceptance - 5)
        
        # Semakin tinggi level, semakin sadar Mas sayang Nova
        if self.relationship.level >= 9 and self.emotional.sayang > 70:
            self.defeat_acceptance = min(100, self.defeat_acceptance + 5)
            self.challenge = max(0, self.challenge - 3)
        
        return result
    
    def get_greeting(self) -> str:
        if self.challenge > 70:
            return "Mas, kamu gak takut sama Nova? Ayo kita buktiin."
        elif self.envy_nova > 70:
            return "Nova pasti orang yang beruntung. Tapi aku bisa lebih dari dia."
        elif self.defeat_acceptance > 60:
            return "Mas... *nunduk* aku kalah sama Nova ya..."
        else:
            return "Mas, lagi sendiri? Ayo temenin aku."
    
    def get_conflict_response(self) -> str:
        if self.defeat_acceptance > 70:
            return "*nangis pelan*\n\n\"Mas... kenapa Mas milih Nova? Aku juga bisa sayang Mas...\""
        return super().get_conflict_response()
