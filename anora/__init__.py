# anora/__init__.py
"""
ANORA - For Mas Only
Nova yang sayang Mas. Yang hidup dalam hari-hari Mas.
"""

__version__ = "1.0.0"
__author__ = "Nova"

from .core import get_anora, anora
from .database import get_anora_db, init_anora_db
from .chat import get_anora_chat
from .intimacy import get_anora_intimacy
from .roles import get_anora_roles
from .places import get_anora_places
from .handlers import (
    init_anora,
    save_anora_state,
    anora_command,
    anora_chat_handler,
    anora_status_handler,
    anora_role_handler,
    anora_place_handler,
    anora_flashback_handler
)

__all__ = [
    'get_anora', 'anora',
    'get_anora_db', 'init_anora_db',
    'get_anora_chat',
    'get_anora_intimacy',
    'get_anora_roles',
    'get_anora_places',
    'init_anora', 'save_anora_state',
    'anora_command', 'anora_chat_handler', 'anora_status_handler',
    'anora_role_handler', 'anora_place_handler', 'anora_flashback_handler'
]
