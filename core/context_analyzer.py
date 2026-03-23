# core/context_analyzer.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Context Analyzer - Analisis Konteks dengan Weighted Memory
Target Realism 9.9/10
=============================================================================
"""

import re
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from identity.registration import CharacterRegistration
from database.models import CharacterRole

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """
    Analisis konteks pesan user dengan weighted memory
    Target Realism 9.9/10
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300
        
        # Intent patterns (diperluas)
        self.intent_patterns = {
            'greeting': [r'\b(halo|hai|hey|hi|selamat|pagi|siang|sore|malam)\b'],
            'farewell': [r'\b(bye|daa|sampai jumpa|tidur|istirahat|good night)\b'],
            'question': [r'\?', r'\b(apa|siapa|kenapa|mengapa|bagaimana|kapan|di mana)\b'],
            'flirt': [r'\b(cantik|ganteng|seksi|hot|goda|rayu|manis)\b'],
            'compliment': [r'\b(keren|mantap|bagus|pintar|hebat|luar biasa)\b'],
            'sexual': [r'\b(intim|ml|tidur|sex|climax|gas|main|buka baju|lepas)\b'],
            'curhat': [r'\b(curhat|cerita|ceritain|masalah|keluh|kesah)\b'],
            'jealous': [r'\b(cemburu|iri|siapa itu|lagi sama siapa)\b'],
            'angry': [r'\b(marah|kesel|kecewa|sebal|betek)\b'],
            'sad': [r'\b(sedih|nangis|duka|kecewa|patah hati)\b'],
            'happy': [r'\b(senang|bahagia|happy|gembira|suka)\b'],
            'rindu': [r'\b(kangen|rindu|miss)\b'],
            'move': [r'\b(ke |pindah|pergi|kesana|kesini|masuk|keluar)\b'],
            'undress': [r'\b(buka|lepas|buka baju|buka celana|buka bra)\b'],
            'intimacy_request': [r'\b(ayo intim|mau intim|pengen intim|ke kamar|ayo ke kamar|kita ke kamar)\b'],
            'promise': [r'\b(janji|promise|berjanji)\b'],
            'plan': [r'\b(rencana|plan|besok|nanti|minggu depan)\b'],
        }
        
        # Idiom lokal dan dialek
        self.local_idioms = {
            'jawa': ['nggih', 'kulo', 'panjenengan', 'matur nuwun', 'wis', 'ra'],
            'sunda': ['muhun', 'abdi', 'anjeun', 'hatur nuhun', 'geura'],
            'betawi': ['iye', 'kite', 'lu', 'gue', 'entuh'],
        }
        
        # Sentiment words (diperluas)
        self.positive_words = [
            'senang', 'bahagia', 'suka', 'cinta', 'sayang', 'enak', 'nyaman', 'baik',
            'manis', 'cantik', 'ganteng', 'keren', 'hebat', 'pintar', 'luar biasa',
            'mantap', 'wow', 'asyik', 'seru'
        ]
        self.negative_words = [
            'sedih', 'marah', 'kesal', 'kecewa', 'benci', 'sakit', 'payah', 'jelek',
            'buruk', 'bodoh', 'sial', 'betek', 'sebel', 'kesel'
        ]
        
        logger.info("✅ ContextAnalyzer 9.9 initialized")
    
    async def analyze(
        self,
        user_message: str,
        registration: CharacterRegistration,
        working_memory: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analisis lengkap konteks pesan user dengan weighted memory
        """
        message_lower = user_message.lower()
        
        # Cek cache
        cache_key = f"{registration.id}:{user_message[:50]}"
        if cache_key in self.cache:
            cache_age = time.time() - self.cache[cache_key]['timestamp']
            if cache_age < self.cache_ttl:
                return self.cache[cache_key]['data']
        
        # Analisis weighted dari working memory
        weighted_context = self._analyze_weighted_context(working_memory)
        
        result = {
            'timestamp': time.time(),
            'original_message': user_message,
            'message_length': len(user_message),
            
            # Intent
            'intents': self._detect_intents(message_lower),
            'primary_intent': None,
            'is_question': '?' in user_message,
            
            # Sentiment
            'sentiment_score': self._calculate_sentiment(message_lower),
            'sentiment': self._get_sentiment_label(message_lower),
            
            # Emotions
            'emotions': self._detect_emotions(message_lower),
            
            # Location & Movement
            'location': self._detect_location(message_lower),
            'is_move_command': self._is_move_command(message_lower),
            
            # Clothing
            'clothing_action': self._detect_clothing_action(message_lower),
            
            # Intimacy
            'intimacy_request': self._is_intimacy_request(message_lower, registration),
            
            # Promises & Plans
            'promise_detected': self._is_promise(message_lower),
            'plan_detected': self._is_plan(message_lower),
            
            # User state
            'user_arousal': self._detect_user_arousal(message_lower),
            'user_mood': self._detect_user_mood(message_lower),
            
            # Weighted context
            'weighted_context': weighted_context,
            
            # Local idioms
            'local_idioms': self._detect_local_idioms(message_lower),
            
            # Context from memory
            'recent_context': self._get_recent_context(working_memory),
            'is_repeating': self._is_repeating(message_lower, working_memory),
        }
        
        # Set primary intent
        if result['intents']:
            result['primary_intent'] = result['intents'][0]
        
        # Simpan cache
        self.cache[cache_key] = {
            'timestamp': time.time(),
            'data': result
        }
        
        self._cleanup_cache()
        
        return result
    
    def _analyze_weighted_context(self, working_memory: List[Dict]) -> Dict:
        """Analisis weighted context dari working memory"""
        if not working_memory:
            return {'total': 0, 'important': 0}
        
        important = [m for m in working_memory if m.get('importance', 0) > 0.7]
        recent = working_memory[-20:] if len(working_memory) > 20 else working_memory
        
        # Hitung trend emosi
        emotions = []
        for m in recent:
            if 'senang' in m.get('user', '').lower():
                emotions.append('positive')
            elif 'sedih' in m.get('user', '').lower():
                emotions.append('negative')
        
        emotion_trend = 'stable'
        if len(emotions) > 5:
            positive_count = emotions.count('positive')
            negative_count = emotions.count('negative')
            if positive_count > negative_count + 2:
                emotion_trend = 'increasing'
            elif negative_count > positive_count + 2:
                emotion_trend = 'decreasing'
        
        return {
            'total': len(working_memory),
            'important': len(important),
            'emotion_trend': emotion_trend,
            'recent_topics': self._extract_topics(recent[-10:])
        }
    
    def _extract_topics(self, memories: List[Dict]) -> List[str]:
        """Ekstrak topik dari memory"""
        topics = []
        all_text = " ".join([m.get('user', '') for m in memories])
        
        topic_keywords = {
            'intim': ['intim', 'cium', 'peluk', 'sentuh'],
            'curhat': ['curhat', 'cerita', 'masalah'],
            'jalan': ['jalan', 'ketemu', 'cafe', 'pantai'],
            'kerja': ['kerja', 'kantor', 'tugas'],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(k in all_text for k in keywords):
                topics.append(topic)
        
        return topics
    
    def _detect_intents(self, message: str) -> List[str]:
        intents = []
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    intents.append(intent)
                    break
        if not intents:
            intents.append('chat')
        return intents
    
    def _calculate_sentiment(self, message: str) -> float:
        score = 0.0
        for word in self.positive_words:
            if word in message:
                score += 0.1
        for word in self.negative_words:
            if word in message:
                score -= 0.1
        return max(-1.0, min(1.0, score))
    
    def _get_sentiment_label(self, message: str) -> str:
        score = self._calculate_sentiment(message)
        if score >= 0.5:
            return 'very_positive'
        elif score >= 0.2:
            return 'positive'
        elif score <= -0.5:
            return 'very_negative'
        elif score <= -0.2:
            return 'negative'
        return 'neutral'
    
    def _detect_emotions(self, message: str) -> List[str]:
        emotions = []
        emotion_keywords = {
            'senang': ['senang', 'bahagia', 'happy', 'gembira'],
            'sedih': ['sedih', 'nangis', 'kecewa', 'sad'],
            'marah': ['marah', 'kesal', 'betek', 'sebal'],
            'rindu': ['kangen', 'rindu', 'miss'],
            'horny': ['horny', 'sange', 'nafsu', 'pengen', 'hot'],
        }
        for emotion, keywords in emotion_keywords.items():
            if any(k in message for k in keywords):
                emotions.append(emotion)
        return emotions
    
    def _detect_location(self, message: str) -> Optional[str]:
        locations = {
            'kamar': ['kamar', 'kamar tidur'],
            'dapur': ['dapur', 'kitchen'],
            'ruang tamu': ['ruang tamu', 'living room'],
            'teras': ['teras', 'beranda'],
            'kantor': ['kantor', 'office'],
            'pantai': ['pantai', 'beach'],
            'cafe': ['cafe', 'kafe', 'coffee shop'],
        }
        for loc, keywords in locations.items():
            if any(k in message for k in keywords):
                return loc
        return None
    
    def _is_move_command(self, message: str) -> bool:
        return ('ke ' in message or 'pindah' in message) and self._detect_location(message) is not None
    
    def _detect_clothing_action(self, message: str) -> Optional[Dict]:
        if 'buka' in message or 'lepas' in message:
            if 'baju' in message:
                return {'action': 'remove', 'item': 'outer_top'}
            if 'bra' in message:
                return {'action': 'remove', 'item': 'inner_top'}
            if 'celana' in message and 'dalam' not in message:
                return {'action': 'remove', 'item': 'outer_bottom'}
            if 'celana dalam' in message:
                return {'action': 'remove', 'item': 'inner_bottom'}
        return None
    
    def _is_intimacy_request(self, message: str, registration: CharacterRegistration) -> bool:
        if registration.level < 7:
            return False
        keywords = ['ayo intim', 'mau intim', 'pengen intim', 'ke kamar', 'ayo ke kamar']
        return any(k in message for k in keywords)
    
    def _is_promise(self, message: str) -> bool:
        return any(k in message for k in ['janji', 'promise', 'berjanji'])
    
    def _is_plan(self, message: str) -> bool:
        return any(k in message for k in ['besok', 'nanti', 'minggu depan', 'rencana'])
    
    def _detect_user_arousal(self, message: str) -> int:
        arousal = 0
        if any(w in message for w in ['horny', 'sange', 'nafsu', 'pengen']):
            arousal += 40
        if any(w in message for w in ['deg-degan', 'gugup', 'berani']):
            arousal += 20
        if any(w in message for w in ['enak', 'nyaman']):
            arousal += 10
        return min(100, arousal)
    
    def _detect_user_mood(self, message: str) -> str:
        if any(w in message for w in ['senang', 'bahagia']):
            return 'happy'
        if any(w in message for w in ['sedih', 'nangis']):
            return 'sad'
        if any(w in message for w in ['horny', 'sange']):
            return 'horny'
        if any(w in message for w in ['kangen', 'rindu']):
            return 'rindu'
        return 'neutral'
    
    def _detect_local_idioms(self, message: str) -> List[str]:
        detected = []
        for dialect, idioms in self.local_idioms.items():
            if any(idiom in message for idiom in idioms):
                detected.append(dialect)
        return detected
    
    def _get_recent_context(self, working_memory: List[Dict]) -> Dict:
        if not working_memory:
            return {'last_topic': None}
        last = working_memory[-1] if working_memory else {}
        return {
            'last_topic': self._extract_topic(last.get('user', '')),
            'last_user_message': last.get('user', '')[:100],
            'time_since_last': time.time() - last.get('timestamp', time.time())
        }
    
    def _extract_topic(self, message: str) -> Optional[str]:
        topics = {
            'kerja': ['kerja', 'kantor'],
            'makan': ['makan', 'masak'],
            'intim': ['intim', 'cium'],
            'curhat': ['curhat', 'cerita'],
        }
        for topic, keywords in topics.items():
            if any(k in message for k in keywords):
                return topic
        return None
    
    def _is_repeating(self, message: str, working_memory: List[Dict]) -> bool:
        if len(working_memory) < 2:
            return False
        recent = working_memory[-3:]
        for mem in recent:
            if mem.get('user', '').lower() == message.lower():
                return True
        return False
    
    def _cleanup_cache(self):
        now = time.time()
        expired = [k for k, v in self.cache.items() if now - v['timestamp'] > self.cache_ttl]
        for k in expired:
            del self.cache[k]


__all__ = ['ContextAnalyzer']
