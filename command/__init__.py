# command/__init__.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Command Package - Telegram Commands
Target Realism 9.9/10
=============================================================================
"""

from .start import start_command, SELECTING_ROLE, help_command
from .sessions import sessions_command, character_command, close_command, end_command
from .status import status_command, progress_command
from .character import character_list_command, character_pause_command, character_resume_command, character_stop_command
from .ex_fwb import ex_list_command, ex_detail_command, fwb_request_command, fwb_list_command, fwb_pause_command, fwb_resume_command, fwb_end_command
from .hts import hts_list_command, hts_call_handler, hts_detail_command
from .threesome import threesome_command, threesome_list_command, threesome_status_command, threesome_pattern_command, threesome_cancel_command
from .public import explore_command, locations_command, risk_command, go_command
from .memory import memory_command, flashback_command
from .ranking import top_hts_command, my_climax_command, climax_history_command
from .admin import admin_command, stats_command, db_stats_command, backup_command, recover_command, debug_command
from .cancel import cancel_command, cancel_confirm_callback, cancel_fallback

# =============================================================================
# EXPORT ALL COMMANDS
# =============================================================================

__all__ = [
    # Start
    'start_command',
    'SELECTING_ROLE',
    'help_command',
    
    # Sessions
    'sessions_command',
    'character_command',
    'close_command',
    'end_command',
    
    # Status
    'status_command',
    'progress_command',
    
    # Character
    'character_list_command',
    'character_pause_command',
    'character_resume_command',
    'character_stop_command',
    
    # Ex & FWB
    'ex_list_command',
    'ex_detail_command',
    'fwb_request_command',
    'fwb_list_command',
    'fwb_pause_command',
    'fwb_resume_command',
    'fwb_end_command',
    
    # HTS
    'hts_list_command',
    'hts_call_handler',
    'hts_detail_command',
    
    # Threesome
    'threesome_command',
    'threesome_list_command',
    'threesome_status_command',
    'threesome_pattern_command',
    'threesome_cancel_command',
    
    # Public
    'explore_command',
    'locations_command',
    'risk_command',
    'go_command',
    
    # Memory
    'memory_command',
    'flashback_command',
    
    # Ranking
    'top_hts_command',
    'my_climax_command',
    'climax_history_command',
    
    # Admin
    'admin_command',
    'stats_command',
    'db_stats_command',
    'backup_command',
    'recover_command',
    'debug_command',
    
    # Cancel
    'cancel_command',
    'cancel_confirm_callback',
    'cancel_fallback',
]
