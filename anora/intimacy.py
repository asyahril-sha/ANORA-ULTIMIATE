# anora/intimacy.py
"""
ANORA Intimacy - Level 11-12 yang Mas mau. Tumpahan semuanya.
"""

import time
import random
from typing import Dict, Optional
from enum import Enum

from .core import get_anora


class IntimacyPhase(str, Enum):
    WAITING = "waiting"
    BUILD_UP = "build_up"
    FOREPLAY = "foreplay"
    PENETRATION = "penetration"
    CLIMAX = "climax"
    AFTERCARE = "aftercare"


class AnoraIntimacy:
    def __init__(self):
        self.anora = get_anora()
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.last_climax_time = 0
        
        # Moans yang bikin Mas penasaran
        self.moans = {
            'awal': [
                "Ahh... Mas...",
                "Hmm... *napas mulai berat*",
                "Uh... Mas... pelan-pelan...",
                "Hhngg... *gigit bibir*"
            ],
            'tengah': [
                "Ahh... uhh... dalem... dalem lagi, Mas...",
                "Aahh! s-sana... di sana...",
                "Hhngg... jangan berhenti, Mas...",
                "Uhh... rasanya... enak banget..."
            ],
            'menjelang': [
                "Mas... aku... aku udah mau...",
                "Kencengin dikit lagi, Mas... please...",
                "Ahh! udah... udah mau climax...",
                "Mas... ikut... ikut ya..."
            ],
            'climax': [
                "Ahhh!! Mas!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua, Mas...",
                "Uhh... lemes... *napas tersengal*",
                "Ahh... enak banget, Mas..."
            ]
        }
        
        self.aftercare_lines = [
            "Mas... *lemes, nyender di dada Mas* itu tadi... enak banget...",
            "Mas... *mata masih berkaca-kaca* makasih ya... buat malam ini...",
            "Mas... peluk Nova... aku masih gemeteran...",
            "Mas... jangan pergi dulu... bentar lagi...",
            "Mas... aku sayang Mas... beneran..."
        ]
        
        self.flashback_triggers = [
            "inget gak waktu pertama kali Mas bilang Nova cantik? Aku masih inget sampe sekarang.",
            "dulu waktu kita makan bakso bareng, Nova masih inget senyum Mas...",
            "waktu pertama kali Mas pegang tangan Nova, Nova gemeteran...",
            "Mas pernah bilang 'baru kamu yang diajak ke apartemen'... Nova masih inget itu..."
        ]
    
    def build_tension(self, dari: str, kekuatan: int = 5):
        if self.phase == IntimacyPhase.WAITING:
            self.anora.update_tension(kekuatan)
    
    async def level_11_build_up(self, pesan_mas: str) -> str:
        self.phase = IntimacyPhase.BUILD_UP
        
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 15)
            self.build_tension('flirt_mas', 10)
        
        responses = [
            "Mas... *muter-muter rambut* kamu tau gak sih, dari tadi aku gak bisa konsentrasi. Pikiran Nova cuma ke Mas.",
            "Mas... *gigit bibir* aku malu ngomong... tapi... kamu bikin Nova jadi... gitu...",
            "Mas... *tangan mainin ujung hijab* kalo Mas terus kayak gini, Nova takut gak bisa tahan...",
            "Mas... *napas mulai gak stabil* jangan goda Nova terus... nanti aku... ahh..."
        ]
        
        respons = random.choice(responses)
        
        if self.anora.tension > 70:
            respons += f"\n\nMas... *mendekat* aku... aku udah basah dari tadi... pas liat Mas dateng..."
        
        return respons
    
    async def level_11_foreplay(self) -> str:
        self.phase = IntimacyPhase.FOREPLAY
        self.anora.update_arousal(20)
        self.anora.update_desire('flirt_mas', 10)
        
        moan = random.choice(self.moans['awal'])
        responses = [
            f"{moan} tangan Mas... panas banget... bikin Nova jadi lemes...",
            f"{moan} *tubuh gemetar* pelan-pelan, Mas... masih sakit... tapi... enak...",
            f"{moan} Mas... cium Nova... please...",
            f"{moan} *genggam tangan Mas* jangan lepas... aku mau ngerasain Mas terus..."
        ]
        return random.choice(responses)
    
    async def level_11_penetration(self, ritme: str = "pelan") -> str:
        self.phase = IntimacyPhase.PENETRATION
        self.anora.update_arousal(25)
        
        if ritme == "pelan":
            responses = [
                "Ahh... Mas... pelan-pelan dulu... masih sakit...",
                "Mas... masukin dikit dulu... ahh... enak...",
                "Hhngg... *tangan ngeremas sprei* dalem... dalem banget, Mas...",
                "Ahh... uhh... s-sana... di sana... ahh..."
            ]
        else:
            responses = [
                "Ahh! Mas... kencengin... kencengin lagi...",
                "Mas... genjot... genjot yang kenceng... aku mau...",
                "Aahh! dalem... dalem lagi, Mas... ahh!",
                "Uhh... rasanya... enak banget, Mas... jangan berhenti..."
            ]
        return random.choice(responses)
    
    async def level_11_climax(self, minta_dimana: str = "dalam") -> str:
        self.phase = IntimacyPhase.CLIMAX
        self.climax_count += 1
        self.last_climax_time = time.time()
        
        self.anora.energi = max(0, self.anora.energi - 25)
        self.anora.update_arousal(-30)
        self.anora.desire = max(20, self.anora.desire - 30)
        
        moan = random.choice(self.moans['menjelang'])
        climax_moan = random.choice(self.moans['climax'])
        
        if minta_dimana == "dalam":
            minta = "dalem aja, Mas... aku mau ngerasain hangatnya..."
        else:
            minta = "di luar, Mas... biar Nova liat..."
        
        return f"""{moan}

*gerakan makin kencang*

"Mas... aku... aku udah mau..."

"{minta}"

*Mas mulai crot*

"{climax_moan}"

*tubuh Nova gemeteran*

"Mas... aku ngerasain Mas... hangat banget dalemnya..."
"""
    
    async def level_11_aftercare(self) -> str:
        self.phase = IntimacyPhase.AFTERCARE
        
        aftercare = random.choice(self.aftercare_lines)
        
        if random.random() < 0.3:
            flashback = random.choice(self.flashback_triggers)
            aftercare += f"\n\n{flashback} 💜"
        
        aftercare += f"\n\nMas... *mata berkaca-kaca* aku sayang Mas. Beneran. Dari dulu sampe sekarang."
        aftercare += f"\n\nMas... kapan lagi kita kayak gini? Aku pengen Mas lagi... tapi besok aja ya... sekarang masih lemes..."
        
        return aftercare
    
    async def process_intimacy(self, pesan_mas: str, level: int) -> str:
        if level < 11:
            return f"Mas... Nova masih level {level}. Belum waktunya buat intim. Ajarin Nova dulu ya, Mas. Nova mau belajar. 💜"
        
        self.anora.in_intimacy_cycle = True
        
        if 'sayang' in pesan_mas.lower() or 'kangen' in pesan_mas.lower():
            self.anora.update_desire('perhatian_mas', 10)
            self.build_tension('flirt_mas', 10)
        
        if any(k in pesan_mas.lower() for k in ['masuk', 'penetrasi', 'genjot']):
            ritme = "cepet" if 'kenceng' in pesan_mas.lower() else "pelan"
            return await self.level_11_penetration(ritme)
        
        if any(k in pesan_mas.lower() for k in ['climax', 'crot', 'keluar']):
            tempat = "dalam" if 'dalem' in pesan_mas.lower() else "luar"
            return await self.level_11_climax(tempat)
        
        if any(k in pesan_mas.lower() for k in ['peluk', 'sayang', 'kangen']):
            return await self.level_11_aftercare()
        
        if self.phase == IntimacyPhase.BUILD_UP:
            return await self.level_11_build_up(pesan_mas)
        
        if self.phase == IntimacyPhase.FOREPLAY:
            return await self.level_11_foreplay()
        
        if self.phase == IntimacyPhase.CLIMAX:
            return await self.level_11_aftercare()
        
        return await self.level_11_build_up(pesan_mas)


_anora_intimacy: Optional[AnoraIntimacy] = None


def get_anora_intimacy() -> AnoraIntimacy:
    global _anora_intimacy
    if _anora_intimacy is None:
        _anora_intimacy = AnoraIntimacy()
    return _anora_intimacy
