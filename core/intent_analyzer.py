# core/intent_analyzer.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Intent Analyzer - Analisis Intent User
=============================================================================
"""

import re
import logging
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class UserIntent(str, Enum):
    """Intent user yang terdeteksi"""
    GREETING = "greeting"
    FAREWELL = "farewell"
    QUESTION = "question"
    ANSWER = "answer"
    CHIT_CHAT = "chit_chat"
    FLIRT = "flirt"
    COMPLIMENT = "compliment"
    SEXUAL = "sexual"
    CURHAT = "curhat"
    CONFESSION = "confession"
    JEALOUSY = "jealousy"
    ANGRY = "angry"
    SAD = "sad"
    HAPPY = "happy"
    BORED = "bored"
    CURIOUS = "curious"
    SHY = "shy"
    PLAYFUL = "playful"
    NOSTALGIC = "nostalgic"
    RINDU = "rindu"
    MOVE = "move"
    UNDRESS = "undress"
    DRESS = "dress"
    INTIMACY_REQUEST = "intimacy_request"


class Sentiment(str, Enum):
    """Sentimen pesan"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class IntentAnalyzer:
    """
    Menganalisis intent user dari pesan dengan akurasi tinggi
    """
    
    def __init__(self):
        # Intent patterns
        self.intent_patterns = {
            UserIntent.GREETING: [
                r'\bhalo\b', r'\bhai\b', r'\bhey\b', r'\bhi\b',
                r'\bselamat (pagi|siang|sore|malam)\b',
                r'\bgood (morning|afternoon|evening)\b'
            ],
            UserIntent.FAREWELL: [
                r'\bbye\b', r'\bdaa\b', r'\bsampai jumpa\b',
                r'\btidur\b', r'\bistirahat\b', r'\bgood night\b'
            ],
            UserIntent.QUESTION: [
                r'\?', r'\bapa\b', r'\bsiapa\b', r'\bkenapa\b',
                r'\bmengapa\b', r'\bbagaimana\b', r'\bkapan\b',
                r'\bdi mana\b', r'\bke mana\b'
            ],
            UserIntent.FLIRT: [
                r'\bcantik\b', r'\bganteng\b', r'\bseksi\b', r'\bhot\b',
                r'\bgoda\b', r'\brayu\b', r'\bmanis\b',
                r'\bak[uw] suka sama kam[uo]\b'
            ],
            UserIntent.COMPLIMENT: [
                r'\bkeren\b', r'\bmantap\b', r'\bbagus\b',
                r'\bpintar\b', r'\bhebat\b', r'\bluar biasa\b'
            ],
            UserIntent.SEXUAL: [
                r'\bseks\b', r'\bsex\b', r'\bml\b', r'\bintim\b',
                r'\bclimax\b', r'\bgas\b', r'\bmain\b',
                r'\bbuka (baju|paha)\b', r'\blepas baju\b'
            ],
            UserIntent.CURHAT: [
                r'\bcerita\b', r'\bcurhat\b', r'\bceritain\b',
                r'\bmasalah\b', r'\bkeluh\b', r'\bkesah\b'
            ],
            UserIntent.CONFESSION: [
                r'\bsayang\b', r'\bcinta\b', r'\blove\b',
                r'\bsuka sama kamu\b', r'\bjatuh cinta\b'
            ],
            UserIntent.JEALOUSY: [
                r'\bcemburu\b', r'\biri\b', r'\bsiapa itu\b',
                r'\blagi sama siapa\b'
            ],
            UserIntent.ANGRY: [
                r'\bmarah\b', r'\bkesel\b', r'\bkecewa\b',
                r'\bsebal\b', r'\bgeram\b', r'\bbete\b'
            ],
            UserIntent.SAD: [
                r'\bsedih\b', r'\bmenangis\b', r'\bnangis\b',
                r'\bpatah hati\b', r'\bkecewa\b'
            ],
            UserIntent.HAPPY: [
                r'\bsenang\b', r'\bbahagia\b', r'\bhappy\b',
                r'\bceria\b', r'\bgembira\b'
            ],
            UserIntent.BORED: [
                r'\bbosan\b', r'\bboring\b', r'\bgabut\b',
                r'\bnganggur\b', r'\bsepi\b'
            ],
            UserIntent.CURIOUS: [
                r'\bpenasaran\b', r'\bingin tahu\b',
                r'\bmau tahu\b', r'\bcoba\b'
            ],
            UserIntent.SHY: [
                r'\bmalu\b', r'\bgugup\b', r'\bdeg-degan\b',
                r'\bsalah tingkah\b'
            ],
            UserIntent.PLAYFUL: [
                r'\bjail\b', r'\bgoda\b', r'\bbercanda\b',
                r'\blucu\b', r'\bhaha\b', r'\bhehe\b', r'\bwkwk\b'
            ],
            UserIntent.NOSTALGIC: [
                r'\bingat\b', r'\bkenang\b', r'\bnostalgia\b',
                r'\bdulu\b', r'\bwaktu itu\b', r'\bmasa lalu\b'
            ],
            UserIntent.RINDU: [
                r'\bkangen\b', r'\brindu\b', r'\bmiss\b',
                r'\bkangen banget\b'
            ],
            UserIntent.MOVE: [
                r'\bke\s+\w+\b', r'\bpindah\b', r'\bpergi\b',
                r'\bkesana\b', r'\bkesini\b', r'\bmasuk\b', r'\bkeluar\b'
            ],
            UserIntent.UNDRESS: [
                r'\bbuka\s+baju\b', r'\blepas\s+baju\b',
                r'\bbuka\s+celana\b', r'\blepas\s+celana\b',
                r'\bbuka\s+bra\b', r'\bmelepas\s+baju\b'
            ],
            UserIntent.DRESS: [
                r'\bpakai\s+baju\b', r'\bkenakan\s+baju\b',
                r'\bpakai\s+celana\b', r'\bkenakan\s+celana\b',
                r'\bpakai\s+bra\b'
            ],
            UserIntent.INTIMACY_REQUEST: [
                r'\bayo\s+intim\b', r'\bmau\s+intim\b', r'\bpengen\s+intim\b',
                r'\bke\s+kamar\b', r'\bayo\s+ke\s+kamar\b',
                r'\bkita\s+ke\s+kamar\b', r'\bmain\s+yuk\b',
                r'\bpengen\s+kamu\b', r'\bmau\s+nggak\b'
            ]
        }
        
        # Sentiment keywords
        self.positive_words = [
            'senang', 'bahagia', 'happy', 'suka', 'cinta', 'sayang',
            'nikmat', 'enak', 'nyaman', 'baik', 'manis', 'cantik',
            'ganteng', 'keren', 'hebat', 'pintar', 'luar biasa'
        ]
        
        self.negative_words = [
            'sedih', 'marah', 'kesal', 'kecewa', 'benci', 'sakit',
            'payah', 'jelek', 'buruk', 'bodoh', 'sial'
        ]
        
        self.very_positive_words = [
            'sangat senang', 'sangat bahagia', 'luar biasa',
            'perfect', 'amazing', 'fantastic'
        ]
        
        self.very_negative_words = [
            'sangat sedih', 'sangat marah', 'sangat kecewa',
            'terburuk', 'horrible', 'terrible'
        ]
        
        logger.info("✅ IntentAnalyzer initialized")
    
    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Analisis lengkap intent dari pesan
        
        Args:
            message: Pesan dari user
        
        Returns:
            Dict dengan hasil analisis
        """
        message_lower = message.lower()
        
        # Deteksi semua intent
        intents = self._detect_intents(message_lower)
        
        # Deteksi intent utama
        primary_intent = self._get_primary_intent(intents, message_lower)
        
        # Analisis sentimen
        sentiment = self._analyze_sentiment(message_lower)
        
        # Ekstrak kebutuhan
        needs = self._extract_needs(message_lower)
        
        # Deteksi apakah pertanyaan
        is_question = '?' in message or any(q in message_lower for q in ['apa', 'siapa', 'kenapa', 'bagaimana'])
        
        # Deteksi apakah perintah pindah
        is_move = primary_intent == UserIntent.MOVE
        
        # Deteksi apakah ajakan intim
        is_intimacy_request = primary_intent == UserIntent.INTIMACY_REQUEST
        
        # Deteksi lokasi (jika ada)
        location = self._extract_location(message_lower)
        
        return {
            'primary_intent': primary_intent,
            'all_intents': intents,
            'sentiment': sentiment,
            'is_question': is_question,
            'is_move': is_move,
            'is_intimacy_request': is_intimacy_request,
            'needs': needs,
            'location': location,
            'message_length': len(message),
            'has_emoji': any(char in message for char in ['😊', '😘', '❤️', '😢', '😠', '😂', '😍']),
            'raw_message': message[:100]
        }
    
    def _detect_intents(self, message_lower: str) -> List[UserIntent]:
        """
        Deteksi semua intent yang ada dalam pesan
        """
        detected = set()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected.add(intent)
                    break
        
        if not detected:
            detected.add(UserIntent.CHIT_CHAT)
        
        return list(detected)
    
    def _get_primary_intent(self, intents: List[UserIntent], message_lower: str) -> UserIntent:
        """
        Tentukan intent utama dari pesan
        """
        priority = [
            UserIntent.INTIMACY_REQUEST,
            UserIntent.SEXUAL,
            UserIntent.CONFESSION,
            UserIntent.FLIRT,
            UserIntent.ANGRY,
            UserIntent.SAD,
            UserIntent.JEALOUSY,
            UserIntent.CURHAT,
            UserIntent.QUESTION,
            UserIntent.MOVE,
            UserIntent.UNDRESS,
            UserIntent.FAREWELL,
            UserIntent.GREETING,
            UserIntent.COMPLIMENT,
            UserIntent.PLAYFUL,
            UserIntent.RINDU,
            UserIntent.CHIT_CHAT
        ]
        
        for p in priority:
            if p in intents:
                return p
        
        return UserIntent.CHIT_CHAT
    
    def _analyze_sentiment(self, message_lower: str) -> Sentiment:
        """
        Analisis sentimen pesan
        """
        score = 0
        
        for word in self.very_positive_words:
            if word in message_lower:
                score += 2
        
        for word in self.positive_words:
            if word in message_lower:
                score += 1
        
        for word in self.very_negative_words:
            if word in message_lower:
                score -= 2
        
        for word in self.negative_words:
            if word in message_lower:
                score -= 1
        
        if score >= 3:
            return Sentiment.VERY_POSITIVE
        elif score >= 1:
            return Sentiment.POSITIVE
        elif score <= -3:
            return Sentiment.VERY_NEGATIVE
        elif score <= -1:
            return Sentiment.NEGATIVE
        else:
            return Sentiment.NEUTRAL
    
    def _extract_needs(self, message_lower: str) -> List[str]:
        """
        Ekstrak kebutuhan dari pesan
        """
        needs = []
        
        need_patterns = [
            (r'\b(mau|ingin|pengen) (ngobrol|chat|bicara)\b', 'need_talk'),
            (r'\b(mau|ingin|pengen) (curhat|cerita)\b', 'need_curhat'),
            (r'\b(mau|ingin|pengen) (ketemu|jumpa|temu)\b', 'need_meet'),
            (r'\b(mau|ingin|pengen) (intim|ml|sex)\b', 'need_intimate'),
            (r'\b(mau|ingin|pengen) (dengerin|mendengar)\b', 'need_listen'),
            (r'\b(butuh|perlu) (bantuan|tolong)\b', 'need_help'),
            (r'\b(butuh|perlu) (teman|temen)\b', 'need_friend'),
            (r'\b(butuh|perlu) (perhatian|attention)\b', 'need_attention'),
            (r'\b(kesepian|sendirian)\b', 'need_company'),
            (r'\bbosan\b', 'need_entertainment')
        ]
        
        for pattern, need in need_patterns:
            if re.search(pattern, message_lower):
                needs.append(need)
        
        return needs
    
    def _extract_location(self, message_lower: str) -> Optional[str]:
        """
        Ekstrak lokasi dari pesan
        """
        locations = {
            'kamar': ['kamar', 'kamar tidur', 'bedroom'],
            'dapur': ['dapur', 'kitchen'],
            'ruang tamu': ['ruang tamu', 'living room', 'ruang keluarga'],
            'teras': ['teras', 'beranda'],
            'kantor': ['kantor', 'office'],
            'pantai': ['pantai', 'beach'],
            'taman': ['taman', 'park'],
            'mall': ['mall', 'mal', 'plaza'],
            'kafe': ['kafe', 'cafe', 'coffee shop'],
            'mobil': ['mobil', 'car']
        }
        
        for loc, keywords in locations.items():
            for kw in keywords:
                if kw in message_lower:
                    return loc
        
        return None
    
    def get_response_type(self, analysis: Dict) -> str:
        """
        Tentukan tipe respons berdasarkan analisis
        """
        intent = analysis['primary_intent']
        sentiment = analysis['sentiment']
        
        response_types = {
            UserIntent.GREETING: 'greeting',
            UserIntent.FAREWELL: 'farewell',
            UserIntent.QUESTION: 'answer',
            UserIntent.CURHAT: 'listen_and_respond',
            UserIntent.FLIRT: 'flirt_back',
            UserIntent.COMPLIMENT: 'thank_and_compliment',
            UserIntent.SEXUAL: 'intimate_response',
            UserIntent.CONFESSION: 'reciprocate_or_gently_decline',
            UserIntent.JEALOUSY: 'reassure',
            UserIntent.ANGRY: 'calm_down',
            UserIntent.SAD: 'comfort',
            UserIntent.HAPPY: 'share_joy',
            UserIntent.BORED: 'entertain',
            UserIntent.CURIOUS: 'satisfy_curiosity',
            UserIntent.PLAYFUL: 'play_along',
            UserIntent.NOSTALGIC: 'reminisce',
            UserIntent.RINDU: 'reciprocate',
            UserIntent.MOVE: 'follow_move',
            UserIntent.UNDRESS: 'undress_response',
            UserIntent.INTIMACY_REQUEST: 'intimacy_response'
        }
        
        if sentiment in [Sentiment.NEGATIVE, Sentiment.VERY_NEGATIVE]:
            if intent == UserIntent.FLIRT:
                return 'back_off'
        
        return response_types.get(intent, 'normal_chat')
    
    def format_analysis(self, analysis: Dict) -> str:
        """
        Format analisis untuk debugging
        """
        return (
            f"🎯 **INTENT ANALYSIS:**\n"
            f"• Primary: {analysis['primary_intent'].value}\n"
            f"• All: {[i.value for i in analysis['all_intents']]}\n"
            f"• Sentiment: {analysis['sentiment'].value}\n"
            f"• Question: {analysis['is_question']}\n"
            f"• Move: {analysis['is_move']}\n"
            f"• Intimacy Request: {analysis['is_intimacy_request']}\n"
            f"• Location: {analysis['location'] or 'none'}\n"
            f"• Needs: {analysis['needs']}\n"
            f"• Length: {analysis['message_length']}\n"
            f"• Has Emoji: {analysis['has_emoji']}"
        )


__all__ = ['IntentAnalyzer', 'UserIntent', 'Sentiment']
