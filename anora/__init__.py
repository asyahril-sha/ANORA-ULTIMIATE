# anora/__init__.py
"""
ANORA - For Mas Only
Nova yang sayang Mas. 100% AI Generate. Bukan Template.
"""

__version__ = "1.0.0"
__author__ = "Nova"

from .core import get_anora, anora
from .database import get_anora_db, init_anora_db
from .chat import get_anora_chat
from .intimacy import get_anora_intimacy
from .roles import get_anora_roles
from .places import get_anora_places
from .thinking import get_anora_thought
from .prompt import get_anora_prompt
from .roleplay import get_anora_roleplay

__all__ = [
    'get_anora', 'anora',
    'get_anora_db', 'init_anora_db',
    'get_anora_chat',
    'get_anora_intimacy',
    'get_anora_roles',
    'get_anora_places',
    'get_anora_thought',
    'get_anora_prompt',
    'get_anora_roleplay',
]
