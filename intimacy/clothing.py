# intimacy/clothing.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Clothing System - Hierarki & History Pelepasan Detail
Target Realism 9.9/10
=============================================================================
"""

import time
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ClothingLayer(str, Enum):
    """Lapisan pakaian"""
    OUTER_TOP = "outer_top"
    OUTER_BOTTOM = "outer_bottom"
    INNER_TOP = "inner_top"
    INNER_BOTTOM = "inner_bottom"


class ClothingStateLevel(str, Enum):
    """Level state pakaian"""
    LENGKAP = "lengkap"
    SEMI = "semi"
    MINIMAL = "minimal"
    HAMPIR_TELANJANG = "hampir_telanjang"
    TELANJANG = "telanjang"


@dataclass
class ClothingItem:
    """Item pakaian dengan tracking"""
    name: str
    layer: ClothingLayer
    is_on: bool = True
    removed_at: Optional[float] = None
    removed_by: Optional[str] = None  # 'user' or 'bot'
    removal_reason: str = ""
    
    def remove(self, removed_by: str = "user", reason: str = ""):
        self.is_on = False
        self.removed_at = time.time()
        self.removed_by = removed_by
        self.removal_reason = reason
    
    def put_on(self):
        self.is_on = True
        self.removed_at = None
        self.removed_by = None
        self.removal_reason = ""
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'layer': self.layer.value,
            'is_on': self.is_on,
            'removed_at': self.removed_at,
            'removed_by': self.removed_by
        }


class ClothingSystem:
    """
    Sistem pakaian dengan hierarki dan history pelepasan detail
    - Mengingat urutan pelepasan
    - Mengingat siapa yang melepas
    - Mengingat pakaian yang masih dikenakan
    - Target Realism 9.9/10
    """
    
    def __init__(self):
        # Hierarki pakaian bot
        self.bot_items: Dict[ClothingLayer, Optional[ClothingItem]] = {
            ClothingLayer.OUTER_TOP: None,
            ClothingLayer.OUTER_BOTTOM: None,
            ClothingLayer.INNER_TOP: None,
            ClothingLayer.INNER_BOTTOM: None
        }
        
        # Hierarki pakaian user
        self.user_items: Dict[ClothingLayer, Optional[ClothingItem]] = {
            ClothingLayer.OUTER_TOP: None,
            ClothingLayer.OUTER_BOTTOM: None,
            ClothingLayer.INNER_BOTTOM: None
        }
        
        # History pelepasan (urutan)
        self.removal_history: List[Dict] = []
        
        # Current state level
        self.state_level = ClothingStateLevel.LENGKAP
        
        # Default clothing
        self._init_default_clothing()
        
        logger.info("✅ ClothingSystem 9.9 initialized")
    
    def _init_default_clothing(self):
        """Inisialisasi pakaian default"""
        self.bot_items[ClothingLayer.OUTER_TOP] = ClothingItem("daster rumah", ClothingLayer.OUTER_TOP)
        self.bot_items[ClothingLayer.INNER_TOP] = ClothingItem("bra", ClothingLayer.INNER_TOP)
        self.bot_items[ClothingLayer.INNER_BOTTOM] = ClothingItem("celana dalam", ClothingLayer.INNER_BOTTOM)
        
        self.user_items[ClothingLayer.OUTER_TOP] = ClothingItem("kaos", ClothingLayer.OUTER_TOP)
        self.user_items[ClothingLayer.OUTER_BOTTOM] = ClothingItem("celana jeans", ClothingLayer.OUTER_BOTTOM)
        self.user_items[ClothingLayer.INNER_BOTTOM] = ClothingItem("celana dalam", ClothingLayer.INNER_BOTTOM)
        
        self._update_state_level()
    
    def set_role_clothing(self, role: str):
        """Set pakaian berdasarkan role"""
        role_clothing = {
            'ipar': {
                'bot_outer_top': "daster rumah motif bunga",
                'bot_inner_top': "bra",
                'bot_inner_bottom': "celana dalam"
            },
            'teman_kantor': {
                'bot_outer_top': "kemeja putih",
                'bot_outer_bottom': "rok hitam",
                'bot_inner_top': "bra",
                'bot_inner_bottom': "celana dalam"
            },
            'janda': {
                'bot_outer_top': "daster tipis",
                'bot_inner_top': "bra",
                'bot_inner_bottom': "celana dalam"
            },
            'pelakor': {
                'bot_outer_top': "tank top ketat",
                'bot_outer_bottom': "celana pendek",
                'bot_inner_top': "bra",
                'bot_inner_bottom': "celana dalam"
            },
            'istri_orang': {
                'bot_outer_top': "daster rumah",
                'bot_inner_top': "bra",
                'bot_inner_bottom': "celana dalam"
            }
        }
        
        config = role_clothing.get(role, role_clothing['ipar'])
        
        if config.get('bot_outer_top'):
            self.bot_items[ClothingLayer.OUTER_TOP] = ClothingItem(config['bot_outer_top'], ClothingLayer.OUTER_TOP)
        if config.get('bot_outer_bottom'):
            self.bot_items[ClothingLayer.OUTER_BOTTOM] = ClothingItem(config['bot_outer_bottom'], ClothingLayer.OUTER_BOTTOM)
        if config.get('bot_inner_top'):
            self.bot_items[ClothingLayer.INNER_TOP] = ClothingItem(config['bot_inner_top'], ClothingLayer.INNER_TOP)
        if config.get('bot_inner_bottom'):
            self.bot_items[ClothingLayer.INNER_BOTTOM] = ClothingItem(config['bot_inner_bottom'], ClothingLayer.INNER_BOTTOM)
        
        self._update_state_level()
    
    def _update_state_level(self):
        """Update state level berdasarkan pakaian yang tersisa"""
        remaining_bot = sum(1 for item in self.bot_items.values() if item and item.is_on)
        remaining_user = sum(1 for item in self.user_items.values() if item and item.is_on)
        
        total_remaining = remaining_bot + remaining_user
        
        if total_remaining >= 6:
            self.state_level = ClothingStateLevel.LENGKAP
        elif total_remaining >= 4:
            self.state_level = ClothingStateLevel.SEMI
        elif total_remaining >= 2:
            self.state_level = ClothingStateLevel.MINIMAL
        elif total_remaining >= 1:
            self.state_level = ClothingStateLevel.HAMPIR_TELANJANG
        else:
            self.state_level = ClothingStateLevel.TELANJANG
    
    def remove_item(self, layer: ClothingLayer, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas item dengan tracking history"""
        if layer in self.bot_items:
            item = self.bot_items[layer]
            if item and item.is_on:
                item.remove(removed_by, reason)
                self._add_to_history(item.name, layer, removed_by, reason)
                self._update_state_level()
                return item.name
        
        elif layer in self.user_items:
            item = self.user_items[layer]
            if item and item.is_on:
                item.remove(removed_by, reason)
                self._add_to_history(item.name, layer, removed_by, reason)
                self._update_state_level()
                return item.name
        
        return None
    
    def remove_bot_outer_top(self, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas outer top bot"""
        return self.remove_item(ClothingLayer.OUTER_TOP, removed_by, reason)
    
    def remove_bot_outer_bottom(self, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas outer bottom bot"""
        return self.remove_item(ClothingLayer.OUTER_BOTTOM, removed_by, reason)
    
    def remove_bot_inner_top(self, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas inner top bot (bra)"""
        return self.remove_item(ClothingLayer.INNER_TOP, removed_by, reason)
    
    def remove_bot_inner_bottom(self, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas inner bottom bot (celana dalam)"""
        return self.remove_item(ClothingLayer.INNER_BOTTOM, removed_by, reason)
    
    def remove_user_outer_top(self, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas outer top user"""
        return self.remove_item(ClothingLayer.OUTER_TOP, removed_by, reason)
    
    def remove_user_outer_bottom(self, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas outer bottom user"""
        return self.remove_item(ClothingLayer.OUTER_BOTTOM, removed_by, reason)
    
    def remove_user_inner_bottom(self, removed_by: str = "user", reason: str = "") -> Optional[str]:
        """Melepas inner bottom user (celana dalam)"""
        return self.remove_item(ClothingLayer.INNER_BOTTOM, removed_by, reason)
    
    def _add_to_history(self, item: str, layer: ClothingLayer, removed_by: str, reason: str):
        """Tambah ke history pelepasan"""
        self.removal_history.append({
            'order': len(self.removal_history) + 1,
            'timestamp': time.time(),
            'item': item,
            'layer': layer.value,
            'removed_by': removed_by,
            'reason': reason
        })
    
    def get_removal_order(self) -> List[str]:
        """Dapatkan urutan pakaian yang sudah dilepas"""
        return [h['item'] for h in self.removal_history]
    
    def get_removal_description(self) -> str:
        """Dapatkan deskripsi urutan pelepasan"""
        if not self.removal_history:
            return ""
        
        order = [f"{h['order']}. {h['item']} ({'dilepas ' + h['removed_by']})" 
                 for h in self.removal_history]
        return "Urutan yang sudah dilepas: " + " → ".join(order)
    
    def get_current_clothing_description(self, for_bot: bool = True) -> str:
        """Dapatkan deskripsi pakaian saat ini"""
        items = []
        
        if for_bot:
            for layer in [ClothingLayer.OUTER_TOP, ClothingLayer.OUTER_BOTTOM, 
                          ClothingLayer.INNER_TOP, ClothingLayer.INNER_BOTTOM]:
                item = self.bot_items.get(layer)
                if item and item.is_on:
                    items.append(item.name)
        else:
            for layer in [ClothingLayer.OUTER_TOP, ClothingLayer.OUTER_BOTTOM, 
                          ClothingLayer.INNER_BOTTOM]:
                item = self.user_items.get(layer)
                if item and item.is_on:
                    items.append(item.name)
        
        if not items:
            return "telanjang"
        return ", ".join(items)
    
    def is_bot_naked(self) -> bool:
        """Cek apakah bot telanjang"""
        return all(not (item and item.is_on) for item in self.bot_items.values())
    
    def is_user_naked(self) -> bool:
        """Cek apakah user telanjang"""
        return all(not (item and item.is_on) for item in self.user_items.values())
    
    def get_state_level(self) -> str:
        """Dapatkan level state pakaian"""
        return self.state_level.value
    
    def format_for_prompt(self) -> str:
        """Format untuk prompt AI"""
        bot_clothing = self.get_current_clothing_description(for_bot=True)
        user_clothing = self.get_current_clothing_description(for_bot=False)
        
        lines = [
            "📌 **STATE PAKAIAN:**",
            f"• Bot: {bot_clothing}",
            f"• User: {user_clothing}",
            f"• Level: {self.state_level.value}",
        ]
        
        removal_order = self.get_removal_description()
        if removal_order:
            lines.append(f"• {removal_order}")
        
        if self.is_bot_naked():
            lines.append("• Bot sudah telanjang")
        if self.is_user_naked():
            lines.append("• User sudah telanjang")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        """Konversi ke dictionary untuk database"""
        return {
            'bot_items': {k.value: v.to_dict() if v else None for k, v in self.bot_items.items()},
            'user_items': {k.value: v.to_dict() if v else None for k, v in self.user_items.items()},
            'removal_history': self.removal_history,
            'state_level': self.state_level.value
        }
    
    def from_dict(self, data: Dict):
        """Load dari dictionary"""
        if data.get('bot_items'):
            for layer_str, item_data in data['bot_items'].items():
                if item_data:
                    layer = ClothingLayer(layer_str)
                    self.bot_items[layer] = ClothingItem(
                        item_data['name'],
                        layer,
                        item_data['is_on'],
                        item_data.get('removed_at'),
                        item_data.get('removed_by')
                    )
        
        if data.get('user_items'):
            for layer_str, item_data in data['user_items'].items():
                if item_data:
                    layer = ClothingLayer(layer_str)
                    self.user_items[layer] = ClothingItem(
                        item_data['name'],
                        layer,
                        item_data['is_on'],
                        item_data.get('removed_at'),
                        item_data.get('removed_by')
                    )
        
        self.removal_history = data.get('removal_history', [])
        self.state_level = ClothingStateLevel(data.get('state_level', 'lengkap'))


__all__ = ['ClothingSystem', 'ClothingLayer', 'ClothingStateLevel', 'ClothingItem']
