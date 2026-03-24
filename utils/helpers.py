# utils/helpers.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Helper Functions
=============================================================================
"""

import random
import re
import time
from typing import List, Optional, Dict, Any


def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    return text.strip()[:500]


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def extract_keywords(text: str, limit: int = 5) -> List[str]:
    """Extract keywords from text"""
    import re
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return list(set(words))[:limit]


def similarity_score(text1: str, text2: str) -> float:
    """Simple similarity score between two texts"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    return len(intersection) / max(len(words1), len(words2))


def format_number(num: int) -> str:
    """Format number with thousands separator"""
    return f"{num:,}".replace(",", ".")


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable"""
    if seconds < 60:
        return f"{seconds} detik"
    elif seconds < 3600:
        return f"{seconds // 60} menit"
    elif seconds < 86400:
        return f"{seconds // 3600} jam"
    else:
        return f"{seconds // 86400} hari"


def time_ago(timestamp: float) -> str:
    """Format timestamp to time ago"""
    diff = time.time() - timestamp
    
    if diff < 60:
        return "baru saja"
    elif diff < 3600:
        return f"{int(diff/60)} menit lalu"
    elif diff < 86400:
        return f"{int(diff/3600)} jam lalu"
    else:
        return f"{int(diff/86400)} hari lalu"


def calculate_age(birth_year: int) -> int:
    """Calculate age from birth year"""
    import datetime
    return datetime.datetime.now().year - birth_year


def generate_temp_id() -> str:
    """Generate temporary ID"""
    import uuid
    return uuid.uuid4().hex[:8]


def parse_command_args(args: List[str]) -> Dict[str, Any]:
    """Parse command arguments"""
    result = {}
    for i, arg in enumerate(args):
        if '=' in arg:
            key, value = arg.split('=', 1)
            result[key] = value
        else:
            result[f'arg_{i}'] = arg
    return result


def validate_role(role: str) -> bool:
    """Validate role name"""
    valid_roles = ['ipar', 'teman_kantor', 'janda', 'pelakor', 
                   'istri_orang', 'pdkt', 'sepupu', 'teman_sma', 'mantan']
    return role.lower() in valid_roles


def validate_intimacy_level(level: int) -> bool:
    """Validate intimacy level (1-12)"""
    return 1 <= level <= 12


def random_percentage() -> float:
    """Generate random percentage"""
    return random.random()


def random_choice_weighted(items: List[Any], weights: List[float]) -> Any:
    """Choose item with weighted probability"""
    return random.choices(items, weights=weights, k=1)[0]


def random_sentence(words: List[str], min_words: int = 3, max_words: int = 8) -> str:
    """Generate random sentence from word list"""
    count = random.randint(min_words, max_words)
    selected = random.sample(words, min(count, len(words)))
    return " ".join(selected).capitalize() + "."


def get_local_greeting(dialect: str = None) -> str:
    """Get greeting in local dialect"""
    greetings = {
        'jawa': ['nggih', 'sugeng enjing'],
        'sunda': ['muhun', 'sampurasun'],
        'betawi': ['iye', 'pagi']
    }
    if dialect and dialect in greetings:
        return random.choice(greetings[dialect])
    return random.choice(['hai', 'halo'])


def get_local_affection(dialect: str = None) -> str:
    """Get affection expression in local dialect"""
    affections = {
        'jawa': ['kula tresno', 'kangen'],
        'sunda': ['abdi bogoh', 'kangen'],
        'betawi': ['gue sayang', 'kangen']
    }
    if dialect and dialect in affections:
        return random.choice(affections[dialect])
    return random.choice(['sayang', 'cinta'])


def mix_local_language(text: str, chance: float = 0.3) -> str:
    """Mix text with local language"""
    if random.random() > chance:
        return text
    
    replacements = {
        'iya': random.choice(['nggih', 'muhun', 'iye']),
        'tidak': random.choice(['ora', 'teu', 'kagak']),
        'aku': random.choice(['aku', 'abdi', 'gue']),
        'kamu': random.choice(['kowe', 'anjeun', 'lu']),
        'sayang': random.choice(['tresno', 'bogoh', 'sayang'])
    }
    
    for key, value in replacements.items():
        if key in text.lower():
            text = text.replace(key, value, 1)
            break
    
    return text


__all__ = [
    'sanitize_input', 'truncate_text', 'extract_keywords', 'similarity_score',
    'format_number', 'format_duration', 'time_ago', 'calculate_age',
    'generate_temp_id', 'parse_command_args', 'validate_role', 'validate_intimacy_level',
    'random_percentage', 'random_choice_weighted', 'random_sentence',
    'get_local_greeting', 'get_local_affection', 'mix_local_language'
]
