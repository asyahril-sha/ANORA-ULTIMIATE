# utils/preferences.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
REDIRECT: Preferences classes are now in tracking/preferences.py
This file is kept for backward compatibility only.
=============================================================================
"""

import warnings

warnings.warn(
    "Importing from utils.preferences is deprecated. "
    "Use 'from tracking.preferences import PreferencesLearner, PreferenceCategory, PreferenceItem' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Redirect to tracking.preferences
from tracking.preferences import (
    PreferencesLearner,
    PreferenceCategory,
    PreferenceItem
)

__all__ = [
    'PreferencesLearner',
    'PreferenceCategory',
    'PreferenceItem'
]
