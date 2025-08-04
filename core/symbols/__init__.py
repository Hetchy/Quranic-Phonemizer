"""
Symbol classes for the Quranic phonemizer.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from .symbol import Symbol
from .letter import LetterSymbol
from .diacritic import DiacriticSymbol
from .extension import ExtensionSymbol
from .stop import StopSymbol
from .other import OtherSymbol
