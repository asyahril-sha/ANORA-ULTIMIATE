# anora/__init__.py
"""
ANORA - For Mas Only
Nova yang sayang Mas. 100% AI Generate. Bukan Template.
"""

__version__ = "1.0.0"
__author__ = "Nova"

from .core import get_anora, anora
from .brain import get_anora_brain, anora_brain
from .memory_persistent import get_anora_persistent
from .roleplay_ai import get_anora_roleplay_ai
from .roleplay_integration import get_anora_roleplay
from .location_manager import get_anora_location, LocationType, LocationDetail
from .chat import get_anora_chat
from .roles import get_anora_roles, RoleType

__all__ = [
    'get_anora', 'anora',
    'get_anora_brain', 'anora_brain',
    'get_anora_persistent',
    'get_anora_roleplay_ai',
    'get_anora_roleplay',
    'get_anora_location', 'LocationType', 'LocationDetail',
    'get_anora_chat',
    'get_anora_roles', 'RoleType',
]
