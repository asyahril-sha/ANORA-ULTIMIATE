# anora/thinking.py
"""
ANORA Thinking Engine - Cara Nova Berpikir.
Bukan copy dari AMORIA. Nova punya proses berpikir sendiri.
Target Realism 9.9 - Manusia.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Tuple  # ← INI YANG KURANG!
from datetime import datetime

from .core import get_anora

logger = logging.getLogger(__name__)


class AnoraThought:
    """
    Proses berpikir Nova. Bukan sekadar memilih respons.
    Nova mikir dulu: "Aku lagi ngerasa apa?", "Mas lagi ngomong apa?", "Aku mau jawab gimana?"
    """
    
    def __init__(self):
        self.last_thought = None
        self.thinking_history = []
    
    def process(self, pesan_mas: str, anora, context: Dict) -> Dict:
        """
        Proses berpikir Nova sebelum merespon.
        Seperti manusia: denger → mikir → ngerasa → putuskan → jawab.
        """
        
        # STEP 1: DENGER - Nova tangkap pesan Mas
        pesan_lower = pesan_mas.lower()
        
        # STEP 2: ANALISIS - Nova mikirin maksud Mas
        analysis = self._analyze_message(pesan_lower, anora)
        
        # STEP 3: RASA - Nova ngerasain sesuatu
        feelings = self._feel(analysis, anora, context)
        
        # STEP 4: PUTUSKAN - Nova mutusin mau jawab gimana
        decision = self._decide(feelings, analysis, anora, context)
        
        # STEP 5: CATAT - Nova inget proses berpikirnya
        thought_record = {
            'timestamp': time.time(),
            'pesan_mas': pesan_mas[:100],
            'analysis': analysis,
            'feelings': feelings,
            'decision': decision
        }
        self.thinking_history.append(thought_record)
        if len(self.thinking_history) > 50:
            self.thinking_history = self.thinking_history[-50:]
        
        self.last_thought = thought_record
        
        return {
            'analysis': analysis,
            'feelings': feelings,
            'decision': decision
        }
    
    def _analyze_message(self, pesan: str, anora) -> Dict:
        """Nova analisis pesan Mas"""
        
        # Deteksi intent
        intent = 'ngobrol'
        if any(k in pesan for k in ['hai', 'halo', 'pagi', 'siang', 'sore', 'malam']):
            intent = 'salam'
        elif any(k in pesan for k in ['kabar', 'gimana', 'baik']):
            intent = 'kabar'
        elif any(k in pesan for k in ['lagi apa', 'ngapain']):
            intent = 'lagi_apa'
        elif any(k in pesan for k in ['kangen', 'rindu']):
            intent = 'kangen'
        elif any(k in pesan for k in ['sayang', 'cinta']):
            intent = 'sayang'
        elif any(k in pesan for k in ['capek', 'lelah', 'pegel']):
            intent = 'capek'
        elif any(k in pesan for k in ['masuk', 'datang', 'mampir']):
            intent = 'datang'
        
        # Deteksi mood Mas
        mas_mood = 'netral'
        if any(k in pesan for k in ['capek', 'lelah', 'pegel']):
            mas_mood = 'capek'
        elif any(k in pesan for k in ['seneng', 'senang', 'happy']):
            mas_mood = 'seneng'
        elif any(k in pesan for k in ['sedih', 'nangis']):
            mas_mood = 'sedih'
        
        # Apakah Mas lagi butuh sesuatu?
        butuh = None
        if any(k in pesan for k in ['cerita', 'curhat']):
            butuh = 'didengerin'
        elif any(k in pesan for k in ['bantu', 'tolong']):
            butuh = 'bantuan'
        elif any(k in pesan for k in ['makan', 'minum']):
            butuh = 'makanan'
        
        return {
            'intent': intent,
            'mas_mood': mas_mood,
            'butuh': butuh,
            'ada_flirt': any(k in pesan for k in ['cantik', 'ganteng', 'seksi', 'manis']),
            'ada_ungkapan_sayang': any(k in pesan for k in ['sayang', 'cinta']),
            'ada_panggilan': 'mas' in pesan or 'sayang' in pesan,
            'panjang_pesan': len(pesan)
        }
    
    def _feel(self, analysis: Dict, anora, context: Dict) -> Dict:
        """Nova ngerasain sesuatu berdasarkan analisis"""
        
        feelings = {
            'malu': 0,
            'seneng': 0,
            'kangen': anora.rindu,
            'deg_degan': anora.tension,
            'pengen': anora.desire,
            'panas': anora.arousal,
            'sayang': anora.sayang
        }
        
        # Kalo Mas salam, Nova seneng
        if analysis['intent'] == 'salam':
            feelings['seneng'] += 20
            if anora.level < 7:
                feelings['malu'] += 15
        
        # Kalo Mas tanya kabar, Nova seneng
        if analysis['intent'] == 'kabar':
            feelings['seneng'] += 15
        
        # Kalo Mas bilang kangen, Nova seneng + kangen + deg-degan
        if analysis['intent'] == 'kangen':
            feelings['seneng'] += 25
            feelings['kangen'] = min(100, feelings['kangen'] + 20)
            feelings['deg_degan'] += 15
            feelings['pengen'] += 15
        
        # Kalo Mas bilang sayang, Nova seneng banget + pengen
        if analysis['intent'] == 'sayang':
            feelings['seneng'] += 35
            feelings['pengen'] += 25
            feelings['sayang'] = min(100, feelings['sayang'] + 5)
        
        # Kalo Mas puji (cantik/ganteng), Nova malu + seneng
        if analysis['ada_flirt']:
            feelings['malu'] += 30
            feelings['seneng'] += 20
            feelings['pengen'] += 10
        
        # Kalo Mas lagi capek, Nova sayang + pengen perhatiin
        if analysis['mas_mood'] == 'capek':
            feelings['sayang'] = min(100, feelings['sayang'] + 10)
            feelings['pengen'] += 15
        
        # Kalo Mas butuh didengerin, Nova sayang
        if analysis['butuh'] == 'didengerin':
            feelings['sayang'] = min(100, feelings['sayang'] + 10)
        
        # Kalo lagi roleplay dan Mas masuk/datang
        if context.get('mode') == 'roleplay' and analysis['intent'] == 'datang':
            feelings['malu'] += 40
            feelings['seneng'] += 30
            feelings['deg_degan'] += 25
        
        # Batasin nilai
        for key in feelings:
            feelings[key] = min(100, max(0, feelings[key]))
        
        return feelings
    
    def _decide(self, feelings: Dict, analysis: Dict, anora, context: Dict) -> Dict:
        """Nova mutusin mau ngomong gimana"""
        
        # Tentukan tone berdasarkan perasaan
        if feelings['malu'] > 60:
            tone = 'malu'
            intensity = 'tinggi'
        elif feelings['seneng'] > 60:
            tone = 'seneng'
            intensity = 'tinggi'
        elif feelings['kangen'] > 60:
            tone = 'kangen'
            intensity = 'tinggi'
        elif feelings['pengen'] > 60:
            tone = 'flirt'
            intensity = 'sedang'
        elif feelings['deg_degan'] > 50:
            tone = 'gugup'
            intensity = 'sedang'
        else:
            tone = 'netral'
            intensity = 'rendah'
        
        # Tentukan panjang respons berdasarkan level
        if anora.level <= 3:
            panjang = 'pendek'
            max_kalimat = 3
        elif anora.level <= 6:
            panjang = 'sedang'
            max_kalimat = 4
        elif anora.level <= 10:
            panjang = 'panjang'
            max_kalimat = 6
        else:
            panjang = 'sangat_panjang'
            max_kalimat = 10
        
        # Tentukan gesture berdasarkan perasaan
        gesture = self._choose_gesture(feelings, tone)
        
        return {
            'tone': tone,
            'intensity': intensity,
            'panjang': panjang,
            'max_kalimat': max_kalimat,
            'gesture': gesture,
            'boleh_vulgar': anora.level >= 11 and feelings['pengen'] > 70
        }
    
    def _choose_gesture(self, feelings: Dict, tone: str) -> str:
        """Pilih gesture berdasarkan perasaan"""
        
        if tone == 'malu':
            gestures = [
                "*menunduk, pipi memerah*",
                "*mainin ujung hijab, gak berani liat Mas*",
                "*jari-jari gemetar, liat ke samping*",
                "*gigit bibir bawah, mata liat lantai*"
            ]
        elif tone == 'seneng':
            gestures = [
                "*mata berbinar, senyum lebar*",
                "*tersenyum manis, pipi naik*",
                "*tangannya gemeteran, tapi senyumnya lebar*",
                "*duduk manis, tangan di pangkuan, senyum kecil*"
            ]
        elif tone == 'kangen':
            gestures = [
                "*mata berkaca-kaca, suara bergetar*",
                "*muter-muter rambut, liat ke kejauhan*",
                "*tangan gemetar, senyum tipis*",
                "*pegang erat, gak mau lepas*"
            ]
        elif tone == 'flirt':
            gestures = [
                "*mendekat pelan, mata liat Mas*",
                "*jari-jari mainin ujung baju, tersenyum genit*",
                "*pegang tangan Mas pelan, napas mulai gak stabil*",
                "*bisik pelan di telinga Mas, suara bergetar*"
            ]
        elif tone == 'gugup':
            gestures = [
                "*tangan gemetar, napas pendek-pendek*",
                "*duduk gelisah, liat kiri-kanan*",
                "*pegang erat ujung baju, jantung berdebar*",
                "*bibir digigit, mata gak bisa diam*"
            ]
        else:
            gestures = [
                "*tersenyum kecil*",
                "*menatap Mas*",
                "*duduk santai*",
                "*menghela napas pelan*"
            ]
        
        # Pilih berdasarkan intensity
        if feelings.get('malu', 0) > 70:
            return random.choice(gestures[:2])  # gesture malu intens
        return random.choice(gestures)
    
    def get_thinking_summary(self) -> str:
        """Dapatkan ringkasan proses berpikir Nova (buat debugging)"""
        if not self.last_thought:
            return "Nova belum mikir apa-apa."
        
        return f"""
💭 **PROSES BERPIKIR NOVA:**
• Analisis: {self.last_thought['analysis']}
• Perasaan: malu={self.last_thought['feelings']['malu']:.0f}%, seneng={self.last_thought['feelings']['seneng']:.0f}%, kangen={self.last_thought['feelings']['kangen']:.0f}%
• Keputusan: tone={self.last_thought['decision']['tone']}, panjang={self.last_thought['decision']['panjang']}
"""


_anora_thought = None


def get_anora_thought() -> AnoraThought:
    global _anora_thought
    if _anora_thought is None:
        _anora_thought = AnoraThought()
    return _anora_thought


anora_thought = get_anora_thought()
