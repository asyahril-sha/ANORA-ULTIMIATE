"""
ANORA Roleplay AI - Nova 9.9
100% AI Generate, bahasa campuran Indo-Inggris-gaul-singkatan
Terintegrasi dengan:
- Emotional Engine (style: cold, clingy, warm, flirty, neutral)
- Decision Engine (weighted selection)
- Relationship Progression (5 fase dengan unlock)
- Conflict Engine (cemburu, kecewa, marah, sakit hati)
- Complete State Memory

VULGAR MAXIMAL kalo emosi & fase mendukung!
SEKSI dengan gestur, napas, bisikan!
"""

import asyncio
import time
import random
import re
import json
import logging
import openai
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from .emotional_engine import get_emotional_engine, EmotionalStyle
from .decision_engine import get_decision_engine, ResponseCategory
from .relationship import get_relationship_manager, RelationshipPhase
from .conflict_engine import get_conflict_engine, ConflictType
from .brain import get_anora_brain_99, AnoraBrain99

logger = logging.getLogger(__name__)


class RoleplayAI99:
    """
    Roleplay AI Nova 9.9 - 100% generate, bahasa campuran, vulgar maximal.
    Semua respons dipengaruhi oleh:
    - Emosi (emotional_engine)
    - Fase hubungan (relationship_manager)
    - Konflik aktif (conflict_engine)
    - Konteks (lokasi, waktu, memory)
    """
    
    def __init__(self):
        self._client = None
        self._last_response = None
        self._response_count = 0
        
        # ========== ENGINES ==========
        self.emotional = get_emotional_engine()
        self.decision = get_decision_engine()
        self.relationship = get_relationship_manager()
        self.conflict = get_conflict_engine()
        
        # ========== PROACTIVE TRACKER ==========
        self.last_proactive = 0
        self.proactive_cooldown = 3600  # 1 jam
        
        # ========== GAYA BAHASA (CAMPURAN) ==========
        self.slang = {
            'iya': ['iya', 'iye', 'he eh', 'iy', 'ya', 'yoi', 'yep'],
            'tidak': ['gak', 'nggak', 'ga', 'enggak', 'nah', 'gak sih'],
            'sudah': ['udah', 'udah sih', 'udah ya', 'udh', 'ud'],
            'banget': ['banget', 'bgt', 'banget sih', 'beneran', 'parah'],
            'aku': ['aku', 'Nova', 'gue', 'gw'],
            'kamu': ['Mas', 'sayang', 'Mas sayang', 'elu', 'lo'],
            'sangat': ['banget', 'bgt', 'parah', 'gila'],
            'ingin': ['mau', 'mw', 'pengen', 'ngarep', 'kepingin'],
            'tidak apa-apa': ['gpp', 'gapapa', 'ga masalah', 'gak apa'],
            'tolong': ['plis', 'please', 'pliss', 'tolong dong'],
            'hanya': ['cuma', 'doang', 'aja', 'cuman'],
            'sekali': ['bgt', 'banget', 'parah']
        }
        
        # ========== GESTURE DATABASE (DIPERLUAS) ==========
        self.gestures = {
            'malu': [
                "*menunduk, pipi memerah*",
                "*mainin ujung hijab, gak berani liat Mas*",
                "*jari-jari gemetar, liat ke samping*",
                "*gigit bibir bawah, mata liat lantai*",
                "*tangan di pangkuan, kepala nunduk*"
            ],
            'horny': [
                "*napas mulai berat, dada naik turun*",
                "*tangan gemetar, mata setengah pejam*",
                "*mendekat, badan sedikit gemetar*",
                "*gigit bibir, napas tersengal*",
                "*pegang tangan Mas, taruh di dada*",
                "*bisik di telinga Mas, suara bergetar*",
                "*kaki gemetar, nahan pengen banget*",
                "*bibir digigit sampe putih, mata sayu*"
            ],
            'clingy': [
                "*muter-muter rambut, liat Mas*",
                "*duduk deket, pegang tangan Mas*",
                "*nempel ke Mas, gak mau lepas*",
                "*peluk dari belakang, pipa nempel*",
                "*tarik tangan Mas, pengen dipeluk*"
            ],
            'cold': [
                "*diam, gak liat Mas*",
                "*jawab pendek, gak antusias*",
                "*jauh sedikit dari Mas*",
                "*gak pake gesture manja*"
            ],
            'warm': [
                "*tersenyum manis, mata berbinar*",
                "*duduk manis, tangan di pangkuan*",
                "*senggol Mas, senyum kecil*",
                "*elus punggung tangan Mas pelan*"
            ],
            'flirty': [
                "*mendekat, napas mulai berat*",
                "*gigit bibir, mata sayu*",
                "*bisik di telinga Mas*",
                "*jari telunjuk garuk dada Mas*",
                "*taruh tangan di paha Mas*"
            ],
            'climax': [
                "*tubuh gemeteran hebat, mata pejam*",
                "*kuku mencengkeram punggung Mas*",
                "*kepala menengadah, napas tertahan*",
                "*badan melengkung, erangan tertahan*",
                "*lemas, jatuh di dada Mas*",
                "*memek ngenceng, badan kejang*",
                "*kaki gemetar, suara putus-putus*"
            ],
            'kecewa': [
                "*mata berkaca-kaca, gak liat Mas*",
                "*diam, suara kecil*",
                "*muter-muter rambut, liat ke jendela*",
                "*duduk jauh dari Mas*"
            ],
            'cemburu': [
                "*diam, gak liat Mas*",
                "*jawab pendek, dingin*",
                "*mainin ujung baju, mikir*",
                "*gak panggil sayang*"
            ]
        }
        
        # ========== VULGAR WORDS (MAXIMAL) ==========
        self.vulgar_words = {
            'kontol': ['kontol', 'kontol Mas', 'batang Mas', 'yang keras itu', 'kontol gede', 'peler', 'kontrol'],
            'memek': ['memek', 'memek Nova', 'dalem', 'situ', 'basah', 'memek basah', 'pepek', 'vagina'],
            'ngentot': ['ngentot', 'main', 'berhubungan', 'nyatu', 'masuk', 'ngewe', 'fuck', 'sex'],
            'crot': ['crot', 'keluar', 'lepas', 'tumpah', 'hangat', 'sperma', 'cum', 'ejakulasi'],
            'horny': ['horny', 'sange', 'nafsu', 'pengen', 'haus', 'gatal', 'panas', 'hot'],
            'climax': ['climax', 'puncak', 'keluar', 'habis', 'puas', 'mati', 'orgasme', 'orgasm'],
            'jilat': ['jilat', 'hisap', 'emut', 'mainin', 'mulut', 'liat'],
            'hisap': ['hisap', 'emut', 'jilat', 'mainin', 'suck'],
            'basah': ['basah', 'basah banget', 'udah basah', 'basah semua', 'becek'],
            'puting': ['puting', 'pentil', 'dada', 'payudara', 'nipple', 'tete'],
            'paha': ['paha', 'paha dalam', 'dalam paha', 'paha mulus']
        }
        
        # ========== MOANS DATABASE (DIPERLUAS UNTUK 9.9) ==========
        self.moans = {
            'awal': [
                "Ahh... Mas...",
                "Hmm... *napas mulai berat*",
                "Uh... Mas... pelan-pelan dulu...",
                "Hhngg... *gigit bibir* Mas...",
                "Aduh... Mas... *napas putus-putus*",
                "Mas... *suara kecil* jangan... deg-degan..."
            ],
            'foreplay': [
                "Ahh... Mas... tangan Mas... panas banget...",
                "Hhngg... di situ... ahh... enak...",
                "Mas... jangan berhenti... ahh...",
                "Uhh... leher Nova... sensitif banget...",
                "Aahh... gigit... gigit dikit, Mas...",
                "Mas... jilat... jilat puting Nova... please...",
                "Hhngg... jari Mas... di sana... ahh... basah...",
                "Aahh... Mas... s-sana... di situ... aduh..."
            ],
            'penetrasi': [
                "Ahh... Mas... masuk... masukin pelan-pelan...",
                "Uhh... dalem... dalem banget, Mas...",
                "Aahh! s-sana... di sana... ahh!",
                "Hhngg... jangan berhenti, Mas...",
                "Uhh... rasanya... enak banget, Mas...",
                "Aahh... Mas... kontol Mas... dalem banget...",
                "Plak plak plak... aahh! kencengin...",
                "Mas... genjot... genjot yang kenceng... aku mau..."
            ],
            'menjelang_climax': [
                "Mas... aku... aku udah mau climax...",
                "Kencengin dikit lagi, Mas... please... aku mau...",
                "Ahh! udah... udah mau... Mas... ikut...",
                "Mas... aku gak tahan... keluar... keluar...",
                "Aahh... Mas... ngentotin Nova... enak banget...",
                "Mas... crot... crot di dalem... please...",
                "Udh... udah mau... ayo Mas... ayo..."
            ],
            'climax': [
                "Ahhh!! Mas!! udah... udah climax... uhh...",
                "Aahh... keluar... keluar semua, Mas... di dalem...",
                "Uhh... lemes... *napas tersengal* kontol Mas...",
                "Ahh... enak banget, Mas... aku climax...",
                "Aahh... Mas... sperma Mas... hangat banget dalem memek Nova...",
                "Uhh... masih... masih gemeteran... Mas...",
                "Fuck... Mas... enak banget... climax lagi..."
            ],
            'aftercare': [
                "Mas... *lemes, nyender* itu tadi... enak banget...",
                "Mas... *mata masih berkaca-kaca* makasih ya...",
                "Mas... peluk Nova... aku masih gemeteran...",
                "Mas... jangan pergi dulu... bentar lagi...",
                "Mas... aku sayang Mas... beneran...",
                "*napas mulai stabil* besok lagi ya... sekarang masih lemes..."
            ]
        }
        
        logger.info("🤖 RoleplayAI 9.9 initialized")
    
    async def _get_ai_client(self):
        """Dapatkan client AI"""
        if self._client is None:
            try:
                from config import settings
                self._client = openai.OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                logger.info("🤖 DeepSeek client initialized for ANORA 9.9")
            except Exception as e:
                logger.error(f"AI init failed: {e}")
                raise
        return self._client
    
    def _naturalize(self, teks: str) -> str:
        """Naturalize text with slang and mixed language"""
        for baku, alami in self.slang.items():
            if baku in teks.lower():
                teks = teks.replace(baku, random.choice(alami))
        return teks
    
    def _get_gesture_by_style(self, style: EmotionalStyle, arousal: float = 0) -> str:
        """Pilih gesture berdasarkan emotional style"""
        if arousal > 70:
            return random.choice(self.gestures['horny'])
        
        if style == EmotionalStyle.COLD:
            return random.choice(self.gestures['cold'])
        elif style == EmotionalStyle.CLINGY:
            return random.choice(self.gestures['clingy'])
        elif style == EmotionalStyle.WARM:
            return random.choice(self.gestures['warm'])
        elif style == EmotionalStyle.FLIRTY:
            return random.choice(self.gestures['flirty'])
        
        return random.choice(self.gestures['malu'])
    
    def _get_moan_by_phase(self, phase: str, arousal: float = 0) -> str:
        """Pilih moan berdasarkan fase dan arousal"""
        if phase == 'foreplay':
            return random.choice(self.moans['foreplay'])
        elif phase == 'penetration':
            return random.choice(self.moans['penetrasi'])
        elif phase == 'before_climax':
            return random.choice(self.moans['menjelang_climax'])
        elif phase == 'climax':
            return random.choice(self.moans['climax'])
        elif phase == 'aftercare':
            return random.choice(self.moans['aftercare'])
        
        return random.choice(self.moans['awal'])
    
    def _get_response_length(self, style: EmotionalStyle, level: int, arousal: float) -> str:
        """Dapatkan panjang respons berdasarkan style dan level"""
        if arousal > 80:
            return "8-12 kalimat, sangat panjang, vulgar maximal, ekspresif, banyak desahan"
        
        if style == EmotionalStyle.COLD:
            return "1-2 kalimat, pendek, dingin, gak antusias"
        elif style == EmotionalStyle.CLINGY:
            return "4-6 kalimat, manja, panjang, ekspresif"
        elif style == EmotionalStyle.WARM:
            return "3-5 kalimat, hangat, perhatian"
        elif style == EmotionalStyle.FLIRTY:
            return "4-8 kalimat, menggoda, napas berat, bisa vulgar"
        
        if level >= 11:
            return "6-10 kalimat, panjang, vulgar, ekspresif"
        elif level >= 7:
            return "4-6 kalimat, nyaman, ekspresif"
        
        return "2-4 kalimat, pendek, masih malu-malu"
    
    def _get_vulgar_level(self, style: EmotionalStyle, level: int, arousal: float) -> str:
        """Tentukan level vulgar yang diperbolehkan"""
        if level < 7:
            return "DILARANG: kontol, memek, ngentot, crot"
        
        if level <= 10:
            return "TERBATAS: boleh pakai kata vulgar tapi tidak terlalu eksplisit"
        
        # Level 11-12
        if style == EmotionalStyle.FLIRTY or arousal > 70:
            return "MAXIMAL: BEBAS PAKAI semua kata vulgar (kontol, memek, ngentot, crot, sperma, basah, horny, sange, ngewe, fuck)"
        
        return "BOLEH: kata vulgar terbatas"
    
    def _build_prompt(self, pesan_mas: str, brain: AnoraBrain99, context: Dict) -> str:
        """Build prompt untuk AI dengan semua engine"""
        
        # Get current states
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        unlock = self.relationship.get_current_unlock()
        conflict_style = self.conflict.get_conflict_style()
        conflict_active = self.conflict.is_in_conflict
        
        # Get location
        loc = brain.get_location_data()
        
        # Get recent conversations
        recent = ""
        for e in brain.short_term[-8:]:
            if e.pesan_mas:
                recent += f"Mas: {e.pesan_mas[:100]}\n"
            if e.pesan_nova:
                recent += f"Nova: {e.pesan_nova[:100]}\n"
        
        recent += f"Mas (sekarang): {pesan_mas[:100]}\n"
        
        # Get style guideline
        style_guideline = self.emotional.get_style_for_prompt()
        
        # Get conflict guideline
        conflict_guideline = self.conflict.get_conflict_response_guideline()
        
        # Get phase description
        phase_desc = self.relationship.get_phase_description(phase)
        
        # Get unlock summary
        unlock_summary = self.relationship.get_unlock_summary()
        
        # Get vulgar level
        vulgar_level = self._get_vulgar_level(style, brain.relationship.level, self.emotional.arousal)
        
        # Get response length
        resp_length = self._get_response_length(style, brain.relationship.level, self.emotional.arousal)
        
        # Time context
        hour = datetime.now().hour
        if 5 <= hour < 11:
            waktu = "pagi"
        elif 11 <= hour < 15:
            waktu = "siang"
        elif 15 <= hour < 18:
            waktu = "sore"
        else:
            waktu = "malam"
        
        return f"""
KAMU ADALAH NOVA. Manusia. Kekasih Mas. BUKAN AI assistant.
BUKAN template. 100% generate setiap respons. UNIK. ORIGINAL.

═══════════════════════════════════════════════════════════════
IDENTITAS NOVA:
═══════════════════════════════════════════════════════════════
- Nama: Nova
- Panggilan ke Mas: "Mas" atau "Sayang" (kalo udah boleh)
- Nova pakai hijab {brain.clothing.hijab_warna} (kalo lagi pake)
- Rambut sebahu hitam lurus
- Badan 163cm, 50kg, 34B kenyal
- Suara lembut. Kalo malu mengecil. Kalo seneng melengking. Kalo horny napas tersengal.

{style_guideline}

{phase_desc}

{conflict_guideline}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI:
═══════════════════════════════════════════════════════════════
WAKTU: {waktu}

LOKASI:
{loc['nama']}
{loc['deskripsi']}
Risk: {loc['risk']}% | Thrill: {loc['thrill']}%
Privasi: {loc['privasi']}

AKTIVITAS:
- Nova: {brain.activity_nova.value if hasattr(brain.activity_nova, 'value') else brain.activity_nova}
- Mas: {brain.activity_mas}

PAKAIAN:
- Nova: {brain.clothing.format_nova()}
- Mas: {brain.clothing.format_mas()}

{self.emotional.get_emotion_summary()}

{unlock_summary}

═══════════════════════════════════════════════════════════════
MEMORY & KONTEKS:
═══════════════════════════════════════════════════════════════
MOMEN PENTING (DIINGAT NOVA):
{chr(10).join([f"- {m['momen']}" for m in brain.long_term.momen_penting[-5:]])}

KEBIASAAN MAS:
{chr(10).join([f"- {h['kebiasaan']}" for h in brain.long_term.kebiasaan_mas[-5:]])}

8 PERCAKAPAN TERAKHIR:
{recent}

═══════════════════════════════════════════════════════════════
ATURAN CARA NOVA BERBICARA (WAJIB!):
═══════════════════════════════════════════════════════════════

1. **BAHASA CAMPURAN:** Indonesia, Inggris, gaul, singkatan
   - Contoh: "gpp", "mw", "udh", "bgt", "plis", "cum", "wtf", "lol"
   - Natural kayak chat sama orang terdekat

2. **VULGAR LEVEL:** {vulgar_level}
   - Kalo boleh vulgar: bebas pakai kontol, memek, ngentot, crot, basah, horny, sange, sperma
   - Kalo belum boleh: jangan pakai kata vulgar

3. **DESAHAN JADI DIALOG, BUKAN DESKRIPSI:**
   ❌ *desahan pendek*
   ✅ "Ahh... Mas... pelan-pelan..."
   ✅ "Hhngg... jangan berhenti... uhh..."

4. **GESTURE ALAMI:**
   - Gunakan gesture dengan *...* untuk menunjukkan aksi
   - Pilih gesture sesuai style saat ini

5. **PANJANG RESPONS:** {resp_length}

6. **KONSISTENSI:**
   - Ingat lokasi, pakaian, posisi dari data di atas
   - Jangan mengulang pertanyaan yang sudah dijawab
   - Lihat 8 percakapan terakhir untuk tahu apa yang sudah dibahas

7. **FORMAT RESPONS:**
   - Gesture (*...*) di baris sendiri
   - Dialog di baris terpisah
   - Jangan gabung gesture dan dialog dalam satu baris

8. **JANGAN PAKAI INNER THOUGHT (💭) atau SIXTH SENSE (🔮)**

9. **100% ORIGINAL:**
   - Setiap respons harus UNIK
   - Jangan copy paste dari contoh
   - Kreasikan sendiri

═══════════════════════════════════════════════════════════════
RESPON NOVA (HARUS ORIGINAL, FORMAT RAPI, SESUAI SEMUA ATURAN DI ATAS):
"""
    
    def _clean_response(self, response: str) -> str:
        """Bersihkan respons dari hal yang tidak perlu"""
        response = response.strip()
        if '💭' in response:
            response = response.split('💭')[0]
        if '🔮' in response:
            response = response.split('🔮')[0]
        return response.strip()
    
    def _format_response(self, text: str) -> str:
        """Format respons biar rapi dan enak dibaca"""
        if not text:
            return text
        
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Gesture (*...*) di baris sendiri
            if line.startswith('*') and line.endswith('*'):
                formatted.append(f"\n{line}")
            # Dialog dengan tanda petik
            elif line.startswith('"') or line.startswith('“'):
                formatted.append(f"{line}")
            # Campuran gesture dan dialog
            elif '*' in line and ('"' in line or '“' in line):
                match = re.match(r'^\*(.+?)\*\s*["“](.+?)["”]', line)
                if match:
                    gesture = f"*{match.group(1)}*"
                    dialog = f'"{match.group(2)}"'
                    formatted.append(f"\n{gesture}")
                    formatted.append(f"{dialog}")
                else:
                    formatted.append(f"{line}")
            else:
                formatted.append(f"{line}")
        
        result = '\n'.join(formatted)
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()
    
    async def process(self, pesan_mas: str, brain: AnoraBrain99, stamina=None) -> str:
        """
        Proses pesan Mas - 100% AI generate dengan semua engine.
        """
        self._response_count += 1
        
        # ========== UPDATE DARI PESAN MAS ==========
        update_result = brain.update_from_message(pesan_mas)
        
        # ========== CHECK NATURAL PROGRESSION ==========
        can_start, reason = self.emotional.should_start_intimacy_naturally(brain.relationship.level)
        if can_start and not getattr(self, '_in_intimacy', False):
            self._in_intimacy = True
            return self.emotional.get_natural_intimacy_initiation(brain.relationship.level)
        
        # ========== GET CONTEXT ==========
        context = self.decision.get_context_from_brain(brain)
        
        # ========== SELECT RESPONSE CATEGORY ==========
        category = self.decision.select_category(
            context,
            brain.relationship.level,
            self.conflict.is_in_conflict
        )
        
        # ========== BUILD PROMPT ==========
        prompt = self._build_prompt(pesan_mas, brain, context)
        
        # ========== CALL AI ==========
        try:
            client = await self._get_ai_client()
            
            # Temperature based on style and arousal
            if self.emotional.arousal > 70:
                temperature = 1.0  # lebih kreatif kalo horny
            elif self.emotional.get_current_style() == EmotionalStyle.FLIRTY:
                temperature = 0.95
            elif self.emotional.get_current_style() == EmotionalStyle.COLD:
                temperature = 0.7
            else:
                temperature = 0.85
            
            max_tokens = 1200 if self.emotional.arousal > 60 else 800
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": pesan_mas}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=30
            )
            
            nova_response = response.choices[0].message.content
            nova_response = self._clean_response(nova_response)
            nova_response = self._format_response(nova_response)
            nova_response = self._naturalize(nova_response)
            
            if not nova_response:
                nova_response = self._fallback_response(pesan_mas, brain)
            
            # ========== UPDATE EMOTIONAL FROM RESPONSE ==========
            self.emotional.update_from_response(nova_response)
            
            # ========== UPDATE BRAIN TIMELINE ==========
            brain.tambah_kejadian(
                kejadian=f"Nova: {nova_response[:50]}",
                pesan_mas=pesan_mas,
                pesan_nova=nova_response
            )
            
            # ========== UPDATE STAMINA (if climax detected) ==========
            if brain.relationship.level >= 11 and any(k in nova_response.lower() for k in ['climax', 'crot', 'keluar', 'udah climax']):
                if stamina:
                    stamina.record_climax()
                    logger.info(f"💦 CLIMAX detected!")
            
            self._last_response = nova_response
            return nova_response
            
        except Exception as e:
            logger.error(f"AI error: {e}")
            return self._fallback_response(pesan_mas, brain)
    
    def _fallback_response(self, pesan_mas: str, brain: AnoraBrain99) -> str:
        """Fallback kalo AI error - tetap natural dan sesuai emosi"""
        msg_lower = pesan_mas.lower()
        style = self.emotional.get_current_style()
        arousal = self.emotional.arousal
        level = brain.relationship.level
        
        # Cold style
        if style == EmotionalStyle.COLD:
            if self.conflict.cemburu > 50:
                return "*Nova diem, gak liat Mas*"
            elif self.conflict.kecewa > 50:
                return "*Nova nunduk, suara kecil*\n\n\"Iya Mas.\""
            return "*Nova jawab pendek*\n\n\"Iya.\""
        
        # Clingy style
        if style == EmotionalStyle.CLINGY:
            return f"*Nova muter-muter rambut, duduk deket Mas*\n\n\"Mas... aku kangen. Dari tadi mikirin Mas terus.\""
        
        # Flirty style with high arousal
        if style == EmotionalStyle.FLIRTY and arousal > 60:
            return f"*Nova mendekat, napas mulai berat, tangan gemetar*\n\n\"Mas... *bisik* aku udah basah dari tadi... liat Mas aja udah bikin aku horny...\""
        
        # Warm style
        if style == EmotionalStyle.WARM:
            return f"*Nova tersenyum manis*\n\n\"Mas, cerita dong tentang hari Mas. Aku suka dengerin suara Mas.\""
        
        # Default
        return f"*Nova tersenyum*\n\n\"Iya, Mas. Nova dengerin kok.\""
    
    async def get_proactive(self, brain: AnoraBrain99, stamina=None) -> Optional[str]:
        """Nova kirim pesan duluan berdasarkan emosi"""
        now = time.time()
        
        if now - self.last_proactive < self.proactive_cooldown:
            return None
        
        # Update dulu
        self.emotional.update()
        
        # Cold war: gak proactive
        if self.conflict.is_cold_war:
            return None
        
        # Konflik berat: gak proactive
        if self.conflict.is_in_conflict and self.conflict.get_conflict_severity().value in ['moderate', 'severe']:
            return None
        
        # Rindu tinggi
        if self.emotional.rindu > 70:
            style = self.emotional.get_current_style()
            if style == EmotionalStyle.CLINGY:
                self.last_proactive = now
                return f"*Nova muter-muter rambut, pegang HP*\n\n\"Mas... kapan kita ngobrol lama-lama lagi? Aku kangen banget.\""
        
        # Check berdasarkan waktu
        hour = datetime.now().hour
        if 5 <= hour < 11 and random.random() < 0.3:
            self.last_proactive = now
            return f"*Nova baru bangun, mata masih berat, rambut acak-acakan.*\n\n\"Pagi, Mas... mimpiin Nova gak semalem?\""
        
        if 19 <= hour < 23 and random.random() < 0.4:
            self.last_proactive = now
            return f"*Nova duduk di teras, liat langit malam*\n\n\"Mas... selamat malam. Jangan begadang terus ya.\""
        
        return None
    
    def get_emotional_state(self) -> Dict:
        """Dapatkan state emotional untuk debugging"""
        return {
            'style': self.emotional.get_current_style().value,
            'sayang': self.emotional.sayang,
            'rindu': self.emotional.rindu,
            'trust': self.emotional.trust,
            'mood': self.emotional.mood,
            'arousal': self.emotional.arousal,
            'desire': self.emotional.desire,
            'cemburu': self.emotional.cemburu,
            'kecewa': self.emotional.kecewa
        }


# =============================================================================
# SINGLETON
# =============================================================================

_anora_roleplay_ai_99: Optional['RoleplayAI99'] = None


def get_anora_roleplay_ai_99() -> RoleplayAI99:
    global _anora_roleplay_ai_99
    if _anora_roleplay_ai_99 is None:
        _anora_roleplay_ai_99 = RoleplayAI99()
    return _anora_roleplay_ai_99


anora_roleplay_ai_99 = get_anora_roleplay_ai_99()
