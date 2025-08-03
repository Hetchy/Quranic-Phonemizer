"""
core/tokenizer.py
=================
Break a list of location keys into a list of *Token* objects:

    - plain segments   → Token(tag=None)
    - <rule class=x>…  → Token(tag='x')

Numeric verse-number tokens (just Arabic-Indic digits) are skipped.
"""

from __future__ import annotations

import re
import yaml
from dataclasses import dataclass, replace, field
from typing import List, Set, Tuple, Dict
from pathlib import Path
from .phoneme import Phoneme

from .loader import load_db, keys_for_reference

_TAG_RE  = re.compile(r"<rule class=([a-zA-Z0-9_-]+)>(.*?)</rule>", re.DOTALL)
_DIGIT_RE = re.compile(r"^[\u0660-\u0669]+$")        # Arabic-Indic digits

DATA_DIR = Path(__file__).resolve().parent.parent / "resources"

@dataclass(slots=True)
class Token:
    text: str
    tag: str | None
    location: str
    is_start: bool = False
    is_end: bool = False
    phonemes: List[Phoneme] = field(default_factory=list)
    consumed_by: Set[str] = field(default_factory=set)

    def mark_consumed_by(self, rule_name: str) -> None:
        self.consumed_by.add(rule_name)

    @staticmethod
    def get_word_phonemes_split(tokens: List['Token'], tok_idx: int, ph_idx: int) -> Tuple[List['Phoneme'], List['Phoneme']]:
        """
        Get the phonemes before and after ph_idx in the word corresponding to the token's word.
        `tok_idx` refers to the token index in the `tokens` list.
        `ph_idx` refers to a specific phoneme in the token at `tok_idx`.
        Returns two arrays: (phonemes_before, phonemes_after).
        Both arrays will be empty lists if there are no phonemes before/after respectively.
        """
        # Validate tok_idx bounds
        if tok_idx < 0 or tok_idx >= len(tokens):
            raise IndexError(f"tok_idx {tok_idx} is out of bounds for tokens list with {len(tokens)} tokens")
        
        token = tokens[tok_idx]
        
        # Validate ph_idx bounds for this token
        if ph_idx < 0 or ph_idx >= len(token.phonemes):
            raise IndexError(f"ph_idx {ph_idx} is out of bounds for token with {len(token.phonemes)} phonemes")
        
        current_token_idx = tok_idx
        
        # Find the start of the word by expanding left
        word_start = current_token_idx
        while word_start > 0 and tokens[word_start - 1].location == token.location:
            word_start -= 1
        
        # Find the end of the word by expanding right
        word_end = current_token_idx
        while word_end < len(tokens) - 1 and tokens[word_end + 1].location == token.location:
            word_end += 1
        
        # Collect all phonemes from word tokens and find the split point
        word_phonemes = []
        split_idx = 0
        
        for i in range(word_start, word_end + 1):
            token = tokens[i]
            if i < current_token_idx:
                # Tokens before current token
                word_phonemes.extend(token.phonemes)
            elif i == current_token_idx:
                # Current token - calculate split index
                split_idx = len(word_phonemes) + ph_idx
                word_phonemes.extend(token.phonemes)
            else:
                # Tokens after current token
                word_phonemes.extend(token.phonemes)
        
        # Split the phonemes at the specified index
        phs_before = word_phonemes[:split_idx] if split_idx > 0 else []
        phs_after = word_phonemes[split_idx + 1:] if split_idx + 1 < len(word_phonemes) else []
        
        return phs_before, phs_after

    @staticmethod
    def get_word_phonemes(tokens: List['Token'], tok_idx: int) -> List['Phoneme']:
        """
        Get all phonemes for the word corresponding to the token's location.
        `tok_idx` refers to the token index in the `tokens` list.
        Returns a list of all phonemes in the word.
        """
        # Validate tok_idx bounds
        if tok_idx < 0 or tok_idx >= len(tokens):
            raise IndexError(f"tok_idx {tok_idx} is out of bounds for tokens list with {len(tokens)} tokens")
        
        token = tokens[tok_idx]
        current_token_idx = tok_idx
        
        # Find the start of the word by expanding left
        word_start = current_token_idx
        while word_start > 0 and tokens[word_start - 1].location == token.location:
            word_start -= 1
        
        # Find the end of the word by expanding right
        word_end = current_token_idx
        while word_end < len(tokens) - 1 and tokens[word_end + 1].location == token.location:
            word_end += 1
        
        # Collect all phonemes from word tokens
        word_phonemes = []
        for i in range(word_start, word_end + 1):
            word_phonemes.extend(tokens[i].phonemes)
        
        return word_phonemes


class Tokenizer:
    """Tokenizer that lazily loads the Qurʾānic DB and emits :class:`Token` objects."""

    def __init__(self, db_path: str | Path = DATA_DIR / "Quran.json",
                 *, special_words_path: str | Path = DATA_DIR / "special_words.yaml") -> None:
        self.db_path = str(db_path)
        self.special_words_path = str(special_words_path)
        self.db: Dict[str, dict] = {}
        self.special_words: Dict[str, Dict] = {}
        self.load_db(self.db_path)
        self.special_words = self._load_special_words(self.special_words_path)

    def load_db(self, db_path: str | Path) -> Dict[str, dict]:
        """Load the Qurʾānic JSON DB from ``db_path``."""
        self.db_path = str(db_path)
        self.db = load_db(self.db_path)
        return self.db

    # -------------------------- helpers -------------------------- #
    @staticmethod
    def _strip_rule_tags(text: str) -> List[Tuple[str | None, str]]:
        """Convert one word (possibly containing embedded ``<rule>``) into tokens."""
        tokens: List[Tuple[str | None, str]] = []
        idx = 0
        for m in _TAG_RE.finditer(text):
            if m.start() > idx:
                plain = text[idx:m.start()]
                if plain:
                    tokens.append((None, plain))
            rule, inner = m.group(1), m.group(2)
            tokens.append((rule, inner))
            idx = m.end()

        if idx < len(text):
            rest = text[idx:]
            if rest:
                tokens.append((None, rest))

        return tokens

    @staticmethod
    def _load_special_words(special_words_path: str) -> Dict[str, Dict]:
        """Load special words from YAML file."""
        try:
            with open(special_words_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            location_map: Dict[str, Dict] = {}
            for special_word in data.get("special_words", []):
                for location in special_word.get("locations", []):
                    location_map[location] = special_word
            return location_map
        except (FileNotFoundError, yaml.YAMLError):
            return {}

    # ------------------------- public API ------------------------ #
    def tokenize(self, ref: str, *, stops: List[str] | None = None) -> List[Token]:
        """Resolve ``ref`` and return a list of :class:`Token` objects."""
        stops = stops or []

        stop_chars_map = {
            "preferred_continue": "\u06D6",  # ۖ
            "preferred_stop": "\u06D7",      # ۗ
            "optional_stop": "\u06DA",       # ۚ
            "compulsory_stop": "\u06D8",     # ۘ
            "prohibited_stop": "\u06D9",     # ۙ
        }

        valid_stops = {"verse"} | set(stop_chars_map.keys())
        invalid_stops = set(stops) - valid_stops
        if invalid_stops:
            raise ValueError(
                f"Invalid stop types: {invalid_stops}. Valid types are: {valid_stops}"
            )

        target_stop_chars: Set[str] = set()
        verse_boundaries = False
        for stop_type in stops:
            if stop_type == "verse":
                verse_boundaries = True
            elif stop_type in stop_chars_map:
                target_stop_chars.add(stop_chars_map[stop_type])

        if not self.db:
            self.load_db(self.db_path)

        locations = keys_for_reference(ref, self.db)
        toks: List[Token] = []

        special_words_map = self.special_words

        for loc in locations:
            raw = self.db[loc]["text"]
            if isinstance(raw, list):
                raw = "".join(raw)

            stripped = re.sub(r"</?rule[^>]*?>", "", raw)
            if _DIGIT_RE.fullmatch(stripped.strip()):
                continue

            if loc in special_words_map:
                special_word = special_words_map[loc]
                combined_text = re.sub(r"</?rule[^>]*?>", "", raw)
                phonemes = [
                    Phoneme(phoneme=ph, name="", cp=0, char="", category="special")
                    for ph in special_word.get("phonemes", [])
                ]
                token = Token(text=combined_text, tag="special", location=loc, phonemes=phonemes)
                toks.append(token)
            else:
                for tag, txt in self._strip_rule_tags(raw):
                    if txt:
                        token = Token(text=txt, tag=tag, location=loc)
                        if target_stop_chars and any(c in txt for c in target_stop_chars):
                            token = replace(token, is_end=True)
                        toks.append(token)

        if toks:
            if target_stop_chars:
                for i in range(len(toks) - 1):
                    if toks[i].is_end:
                        toks[i + 1] = replace(toks[i + 1], is_start=True)

            if verse_boundaries:
                prev_verse = None
                for i, token in enumerate(toks):
                    s, v, _ = token.location.split(":")
                    current_verse = f"{s}:{v}"

                    if prev_verse != current_verse:
                        toks[i] = replace(toks[i], is_start=True)

                    next_token = toks[i + 1] if i + 1 < len(toks) else None
                    if next_token is None:
                        toks[i] = replace(toks[i], is_end=True)
                    else:
                        next_s, next_v, _ = next_token.location.split(":")
                        next_verse = f"{next_s}:{next_v}"
                        if current_verse != next_verse:
                            toks[i] = replace(toks[i], is_end=True)

                    prev_verse = current_verse

            toks[0] = replace(toks[0], is_start=True)
            toks[-1] = replace(toks[-1], is_end=True)

        return toks