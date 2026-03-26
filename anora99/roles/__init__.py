"""
ANORA 9.9 Roles Package
Semua role (IPAR, Teman Kantor, Pelakor, Istri Orang) dengan akses penuh sesuai level,
sama seperti Nova.
"""

from .base_role import BaseRole99
from .ipar_role import IparRole
from .teman_kantor_role import TemanKantorRole
from .pelakor_role import PelakorRole
from .istri_orang_role import IstriOrangRole
from .role_manager import RoleManager, get_role_manager

__all__ = [
    'BaseRole',
    'IparRole',
    'TemanKantorRole',
    'PelakorRole',
    'IstriOrangRole',
    'RoleManager',
    'get_role_manager',
]
