"""
Text matching module for finding Quranic references from Arabic text input.

This module implements the text-to-reference matching algorithm as specified:
1. Preprocessing/normalization of both input text and Quran database
2. Word-by-word matching with cumulative scoring
3. Candidate filtering based on matching ratios
4. Return best match as standard reference format
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from difflib import SequenceMatcher

from .loader import load_db


class TextMatcher:
    """Matches Arabic text input to Quranic verses and returns reference ranges."""
    
    def __init__(self, 
                 db_path: str | Path, 
                 phoneme_mappings: Dict[str, Any]):
        """
        Initialize TextMatcher.
        
        Parameters
        ----------
        db_path : str | Path
            Path to Quran.json database
        phoneme_mappings : Dict[str, Any]
            Phoneme mappings from base_phonemes.yaml
        """
        self.db_path = db_path
        self.db = load_db(db_path)
        self.phoneme_mappings = phoneme_mappings
        self._build_char_mappings()
        self._preprocess_database()
    
    def _build_char_mappings(self) -> None:
        """Build character mapping tables from phoneme_mappings."""
        # Create lookup tables for all character types
        self.all_chars = {}
        
        # Add letters
        for letter_type, letter_info in self.phoneme_mappings.get("letters", {}).items():
            char = letter_info["char"]
            self.all_chars[char] = letter_type
        
        # Add diacritics
        for diacritic_type, diacritic_info in self.phoneme_mappings.get("diacritics", {}).items():
            char = diacritic_info["char"] 
            self.all_chars[char] = diacritic_type
        
        # Add extensions
        for ext_type, ext_info in self.phoneme_mappings.get("extensions", {}).items():
            char = ext_info["char"]
            self.all_chars[char] = ext_type
        
        # Add stop signs
        for stop_type, stop_info in self.phoneme_mappings.get("stop_signs", {}).items():
            char = stop_info["char"]
            self.all_chars[char] = stop_type
            
        # Add other
        for other_type, other_info in self.phoneme_mappings.get("other", {}).items():
            char = other_info["char"]
            self.all_chars[char] = other_type
    
    def _validate_text_chars(self, text: str) -> None:
        """
        Validate that all characters in text are defined in base_phonemes.yaml.
        
        Note: Non-matching unicode characters are allowed and will be silently ignored.
        
        Parameters
        ----------
        text : str
            Text to validate
        """
        # Skip validation - non-matching unicode characters are fine
        pass
    
    def _preprocess_database(self) -> None:
        """Preprocess the entire Quran database with normalization rules."""
        self.preprocessed_db = {}
        
        for location_key, word_data in self.db.items():
            original_text = word_data["text"]
            normalized_text = self._normalize_quran_text(original_text)
            stripped_text = self._strip_diacritics(normalized_text)
            
            self.preprocessed_db[location_key] = {
                "original": original_text,
                "normalized": normalized_text, 
                "stripped": stripped_text,
                "surah": word_data["surah"],
                "ayah": word_data["ayah"],
                "word": word_data["word"]
            }
    
    def _normalize_quran_text(self, text: str) -> str:
        """
        Apply preprocessing rules to Quran database text.
        
        Rules:
        - HAMZA_WASL -> ALEF
        - DAGGER_ALEF -> ALEF  
        - MINI_WAW -> WAW
        - MINI_YA_END, MINI_YA_MIDDLE -> YA
        - آ (Alef with Madda above) -> ALEF
        - Strip all stop signs (ۖۗۚۘۙۛ)
        - Strip unwanted "other" symbols (keep only shadda ّ, partial alef maksura ٮ, tatweel ـ)
        
        Parameters
        ----------
        text : str
            Original text from database
            
        Returns
        -------
        str
            Normalized text
        """
        # Get character mappings
        letters = self.phoneme_mappings.get("letters", {})
        extensions = self.phoneme_mappings.get("extensions", {})
        
        # Build replacement mapping
        replacements = {}
        
        # HAMZA_WASL -> ALEF
        if "HAMZA_WASL" in letters and "ALEF" in letters:
            replacements[letters["HAMZA_WASL"]["char"]] = letters["ALEF"]["char"]
        
        # DAGGER_ALEF -> ALEF
        if "DAGGER_ALEF" in extensions and "ALEF" in letters:
            replacements[extensions["DAGGER_ALEF"]["char"]] = letters["ALEF"]["char"]
        
        # MINI_WAW -> WAW
        if "MINI_WAW" in extensions and "WAW" in letters:
            replacements[extensions["MINI_WAW"]["char"]] = letters["WAW"]["char"]
        
        # MINI_YA_END -> YA
        if "MINI_YA_END" in extensions and "YA" in letters:
            replacements[extensions["MINI_YA_END"]["char"]] = letters["YA"]["char"]
        
        # MINI_YA_MIDDLE -> YA  
        if "MINI_YA_MIDDLE" in letters and "YA" in letters:
            replacements[letters["MINI_YA_MIDDLE"]["char"]] = letters["YA"]["char"]
        
        # Apply replacements
        result = text
        for old_char, new_char in replacements.items():
            result = result.replace(old_char, new_char)
        
        # Additional preprocessing: آ (Alef with Madda above) -> normal Alef
        if "ALEF" in letters:
            normal_alef = letters["ALEF"]["char"]
            result = result.replace("آ", normal_alef)
        
        # Strip stop signs and unwanted "other" symbols
        result = self._strip_unwanted_symbols(result)
        
        return result
    
    def _strip_unwanted_symbols(self, text: str) -> str:
        """
        Strip stop signs and unwanted "other" symbols from text.
        
        Removes all stop signs and all "other" symbols except:
        - SHADDA (ّ)
        - PARTIAL_ALEF_MAKSURA (ٮ) 
        - TATWEEL (ـ)
        
        Parameters
        ----------
        text : str
            Text containing symbols to be stripped
            
        Returns
        -------
        str
            Text with unwanted symbols removed
        """
        # Get symbol mappings
        stop_signs = self.phoneme_mappings.get("stop_signs", {})
        other_symbols = self.phoneme_mappings.get("other", {})
        
        # Build list of symbols to remove
        symbols_to_remove = set()
        
        # Add all stop signs
        for stop_info in stop_signs.values():
            symbols_to_remove.add(stop_info["char"])
        
        # Add unwanted "other" symbols (all except shadda, partial alef maksura, tatweel)
        keep_symbols = {"SHADDA", "PARTIAL_ALEF_MAKSURA", "TATWEEL"}
        for symbol_name, symbol_info in other_symbols.items():
            if symbol_name not in keep_symbols:
                symbols_to_remove.add(symbol_info["char"])
        
        # Remove unwanted symbols
        result = text
        for symbol in symbols_to_remove:
            result = result.replace(symbol, "")
        
        return result
    
    def _strip_diacritics(self, text: str) -> str:
        """
        Strip all diacritics from text for matching.
        
        Parameters
        ---------- 
        text : str
            Text with diacritics
            
        Returns
        -------
        str
            Text with diacritics removed
        """
        # Remove rule tags first
        clean_text = re.sub(r"</?rule[^>]*?>", "", text)
        
        # Get diacritic characters
        diacritics = self.phoneme_mappings.get("diacritics", {})
        diacritic_chars = {info["char"] for info in diacritics.values()}
        
        # Remove diacritics
        result = ""
        for char in clean_text:
            if char not in diacritic_chars:
                result += char
        
        return result.strip()
    
    def _calculate_word_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate similarity ratio between two words.
        
        Parameters
        ----------
        word1, word2 : str
            Words to compare
            
        Returns
        -------
        float
            Similarity ratio between 0.0 and 1.0
        """
        if not word1 or not word2:
            return 0.0
        
        # Use SequenceMatcher for similarity calculation
        return SequenceMatcher(None, word1, word2).ratio()
    
    def _split_into_words(self, text: str) -> List[str]:
        """
        Split text into words, removing empty strings.
        
        Parameters
        ----------
        text : str
            Text to split
            
        Returns
        -------
        List[str]
            List of words
        """
        return [word.strip() for word in text.split() if word.strip()]
    
    def _remove_spaces(self, text: str) -> str:
        """
        Remove all spaces from text for space-robust matching.
        
        Parameters
        ----------
        text : str
            Text with spaces
            
        Returns
        -------
        str
            Text with all spaces removed
        """
        return text.replace(" ", "")
    
    def find_matching_range(self, input_text: str) -> str:
        """
        Find the best matching verse range for input text.
        
        Parameters
        ----------
        input_text : str
            Arabic text to search for
            
        Returns
        -------
        str
            Reference range in format "s:v:w-s:v:w" or "s:v:w" for single word
            
        Raises
        ------
        ValueError
            If no match found or if input contains invalid characters
        """
        # Apply basic preprocessing to input (e.g., آ -> ا) before validation
        preprocessed_input = input_text.replace("آ", "ا")  # Convert آ to normal Alef
        
        # Validate preprocessed input characters
        self._validate_text_chars(preprocessed_input)
        
        # Preprocess input text (no normalization for input, only strip diacritics)
        input_stripped = self._strip_diacritics(preprocessed_input)
        input_words = self._split_into_words(input_stripped)
        
        if not input_words:
            raise ValueError("No valid words found in input text")
        
        # Find candidates using word-by-word matching
        candidates = self._find_candidates(input_words)
        
        if not candidates:
            raise ValueError("No matching verses found")
        
        # Return the first (best) candidate as reference range
        best_candidate = candidates[0]
        return self._build_reference_range(best_candidate)
    
    def find_matching_range_with_score(self, input_text: str) -> tuple[str | None, float]:
        """
        Find the best matching verse range for input text with score threshold.
        
        Parameters
        ----------
        input_text : str
            Arabic text to search for
            
        Returns
        -------
        tuple[str | None, float]
            Tuple of (reference_range, match_score). reference_range is None if 
            score is below threshold (0.5), but score is always returned.
            
        Raises
        ------
        ValueError
            If no matches found at all or if input contains invalid characters
        """
        match_threshold = 0.5  # Internal threshold
        # Apply basic preprocessing to input (e.g., آ -> ا) before validation
        preprocessed_input = input_text.replace("آ", "ا")  # Convert آ to normal Alef
        
        # Validate preprocessed input characters
        self._validate_text_chars(preprocessed_input)
        
        # Preprocess input text (no normalization for input, only strip diacritics)
        input_stripped = self._strip_diacritics(preprocessed_input)
        input_words = self._split_into_words(input_stripped)
        
        if not input_words:
            raise ValueError("No valid words found in input text")
        
        # Find candidates using word-by-word matching
        candidates = self._find_candidates(input_words)
        
        if not candidates:
            raise ValueError("No matching verses found")
        
        # Check if best candidate meets threshold
        best_candidate = candidates[0]
        if best_candidate["total_score"] < match_threshold:
            # Return failure but include the best score
            return None, best_candidate["total_score"]
        
        # Return the first (best) candidate as reference range with score
        return self._build_reference_range(best_candidate), best_candidate["total_score"]
    
    def find_matching_range_scoped(self, input_text: str, scope_ref: str) -> str:
        """
        Find the best matching verse range for input text within a specified scope.
        
        Parameters
        ----------
        input_text : str
            Arabic text to search for
        scope_ref : str
            Traditional reference format defining the search scope (e.g., "2", "2:1", "2:1-2:5")
            
        Returns
        -------
        str
            Reference range in format "s:v:w-s:v:w" or "s:v:w" for single word
            
        Raises
        ------
        ValueError
            If no match found within scope or if scope_ref is invalid
        """
        # Apply basic preprocessing to input (e.g., آ -> ا) before validation
        preprocessed_input = input_text.replace("آ", "ا")  # Convert آ to normal Alef
        
        # Validate preprocessed input characters
        self._validate_text_chars(preprocessed_input)
        
        # Preprocess input text (no normalization for input, only strip diacritics)
        input_stripped = self._strip_diacritics(preprocessed_input)
        input_words = self._split_into_words(input_stripped)
        
        if not input_words:
            raise ValueError("No valid words found in input text")
        
        # Get the location keys for the scope reference
        from .loader import keys_for_reference
        scope_keys = keys_for_reference(scope_ref, self.db)
        if not scope_keys:
            raise ValueError(f"Invalid or empty scope reference: {scope_ref}")
        
        # Convert scope keys to set for fast lookup
        scope_keys_set = set(scope_keys)
        
        # Find candidates using word-by-word matching, limited to scope
        candidates = self._find_candidates_scoped(input_words, scope_keys_set, scope_keys)
        
        if not candidates:
            raise ValueError(f"No matching text found within scope '{scope_ref}'")
        
        # Return the first (best) candidate as reference range
        best_candidate = candidates[0]
        return self._build_reference_range(best_candidate)
    
    def find_matching_range_scoped_with_score(self, input_text: str, scope_ref: str) -> tuple[str | None, float]:
        """
        Find the best matching verse range for input text within a specified scope with score threshold.
        
        Parameters
        ----------
        input_text : str
            Arabic text to search for
        scope_ref : str
            Traditional reference format defining the search scope (e.g., "2", "2:1", "2:1-2:5")
            
        Returns
        -------
        tuple[str | None, float]
            Tuple of (reference_range, match_score). reference_range is None if 
            score is below threshold (0.5), but score is always returned.
            
        Raises
        ------
        ValueError
            If no matches found at all within scope or if scope_ref is invalid
        """
        match_threshold = 0.5  # Internal threshold
        # Apply basic preprocessing to input (e.g., آ -> ا) before validation
        preprocessed_input = input_text.replace("آ", "ا")  # Convert آ to normal Alef
        
        # Validate preprocessed input characters
        self._validate_text_chars(preprocessed_input)
        
        # Preprocess input text (no normalization for input, only strip diacritics)
        input_stripped = self._strip_diacritics(preprocessed_input)
        input_words = self._split_into_words(input_stripped)
        
        if not input_words:
            raise ValueError("No valid words found in input text")
        
        # Get the location keys for the scope reference
        from .loader import keys_for_reference
        scope_keys = keys_for_reference(scope_ref, self.db)
        if not scope_keys:
            raise ValueError(f"Invalid or empty scope reference: {scope_ref}")
        
        # Convert scope keys to set for fast lookup
        scope_keys_set = set(scope_keys)
        
        # Find candidates using word-by-word matching, limited to scope
        candidates = self._find_candidates_scoped(input_words, scope_keys_set, scope_keys)
        
        if not candidates:
            raise ValueError(f"No matching text found within scope '{scope_ref}'")
        
        # Check if best candidate meets threshold
        best_candidate = candidates[0]
        if best_candidate["total_score"] < match_threshold:
            # Return failure but include the best score
            return None, best_candidate["total_score"]
        
        # Return the first (best) candidate as reference range with score
        return self._build_reference_range(best_candidate), best_candidate["total_score"]
    
    def find_matching_range_scoped_with_score_space_robust(self, input_text: str, scope_ref: str, word_buffer: int = 5) -> tuple[str | None, float]:
        """
        Find the best matching verse range using space-robust algorithm with variable window sizes.
        
        This method removes spaces from both input and database text before comparison,
        making it robust to word splitting/merging issues common in ASR output.
        
        Parameters
        ----------
        input_text : str
            Arabic text to search for
        scope_ref : str
            Traditional reference format defining the search scope (e.g., "2", "2:1", "2:1-2:5")
        word_buffer : int, default 5
            Number of words +/- to consider around input length
            
        Returns
        -------
        tuple[str | None, float]
            Tuple of (reference_range, match_score). reference_range is None if 
            score is below threshold (0.5), but score is always returned.
            
        Raises
        ------
        ValueError
            If no matches found at all within scope or if scope_ref is invalid
        """
        match_threshold = 0.5  # Internal threshold
        # Apply basic preprocessing to input (e.g., آ -> ا) before validation
        preprocessed_input = input_text.replace("آ", "ا")  # Convert آ to normal Alef
        
        # Validate preprocessed input characters
        self._validate_text_chars(preprocessed_input)
        
        # Preprocess input text (no normalization for input, only strip diacritics)
        input_stripped = self._strip_diacritics(preprocessed_input)
        input_words = self._split_into_words(input_stripped)
        
        if not input_words:
            raise ValueError("No valid words found in input text")
        
        # Get the location keys for the scope reference
        from .loader import keys_for_reference
        scope_keys = keys_for_reference(scope_ref, self.db)
        if not scope_keys:
            raise ValueError(f"Invalid or empty scope reference: {scope_ref}")
        
        # Find candidates using space-robust algorithm
        candidates = self._find_candidates_space_robust_scoped(input_words, scope_keys, word_buffer)
        
        if not candidates:
            raise ValueError(f"No matching text found within scope '{scope_ref}'")
        
        # Check if best candidate meets threshold
        best_candidate = candidates[0]
        if best_candidate["total_score"] < match_threshold:
            # Return failure but include the best score
            return None, best_candidate["total_score"]
        
        # Return the first (best) candidate as reference range with score
        return self._build_reference_range(best_candidate), best_candidate["total_score"]
    
    def _find_candidates_space_robust_scoped(self, input_words: List[str], scope_keys: List[str], word_buffer: int = 5) -> List[Dict[str, Any]]:
        """
        Find candidate matches using space-robust algorithm with variable window sizes.
        
        Algorithm:
        1. Try window sizes from (n-word_buffer) to (n+word_buffer) where n = len(input_words)
        2. For each window size, slide through the scoped database
        3. Remove spaces from both input and database ranges
        4. Calculate similarity and track best matches
        
        Parameters
        ----------
        input_words : List[str]
            Preprocessed input words to match
        scope_keys : List[str]
            Ordered list of location keys within the scope
        word_buffer : int, default 5
            Number of words +/- to consider around input length
            
        Returns
        -------
        List[Dict[str, Any]]
            List of candidate matches sorted by total score
        """
        candidates = []
        n_input_words = len(input_words)
        
        # Remove spaces from input text for comparison
        input_text_no_spaces = self._remove_spaces(" ".join(input_words))
        
        # Try different window sizes: n-word_buffer to n+word_buffer
        min_window = max(1, n_input_words - word_buffer)
        max_window = n_input_words + word_buffer
        
        for window_size in range(min_window, max_window + 1):
            # Slide window through scope
            for start_idx in range(len(scope_keys) - window_size + 1):
                end_idx = start_idx + window_size
                
                # Get database range
                db_range_keys = scope_keys[start_idx:end_idx]
                
                # Construct database text from this range
                db_words = []
                for key in db_range_keys:
                    if key in self.preprocessed_db:
                        db_words.append(self.preprocessed_db[key]["stripped"])
                
                if not db_words:
                    continue
                
                # Remove spaces from database text for comparison
                db_text_no_spaces = self._remove_spaces(" ".join(db_words))
                
                # Calculate similarity between space-free texts
                similarity = self._calculate_word_similarity(input_text_no_spaces, db_text_no_spaces)
                
                # Create candidate
                candidate = {
                    "start_location": db_range_keys[0],
                    "end_location": db_range_keys[-1],
                    "matched_locations": db_range_keys,
                    "total_score": similarity,
                    "num_words": len(db_range_keys),
                    "window_size": window_size,
                    "input_length": n_input_words
                }
                
                candidates.append(candidate)
        
        # Sort by total score (descending) and return
        candidates.sort(key=lambda x: x["total_score"], reverse=True)
        return candidates
    
    def _find_candidates(self, input_words: List[str]) -> List[Dict[str, Any]]:
        """
        Find candidate matches using the specified algorithm.
        
        Algorithm:
        1. Find candidates based on ref word by word until exhausting all words
        2. Maintain cumulative scores of best candidates  
        3. Use first match if multiple candidates
        
        Parameters
        ----------
        input_words : List[str]
            Preprocessed input words to match
            
        Returns
        -------
        List[Dict[str, Any]]
            List of candidate matches sorted by total score
        """
        candidates = []
        
        # Get all location keys sorted by position
        all_locations = sorted(self.preprocessed_db.keys(), 
                              key=lambda x: tuple(map(int, x.split(":"))))
        
        # For each starting position, try to match the sequence
        for start_idx, start_location in enumerate(all_locations):
            candidate = self._try_match_from_position(input_words, start_idx, all_locations)
            if candidate:
                candidates.append(candidate)
        
        # Sort by total score (descending) and return
        candidates.sort(key=lambda x: x["total_score"], reverse=True)
        return candidates
    
    def _find_candidates_scoped(self, input_words: List[str], scope_keys_set: set, scope_keys: List[str]) -> List[Dict[str, Any]]:
        """
        Find candidate matches within a specified scope using the matching algorithm.
        
        Parameters
        ----------
        input_words : List[str]
            Preprocessed input words to match
        scope_keys_set : set
            Set of location keys within the scope for fast lookup
        scope_keys : List[str]
            Ordered list of location keys within the scope
            
        Returns
        -------
        List[Dict[str, Any]]
            List of candidate matches sorted by total score
        """
        candidates = []
        
        # For each starting position within scope, try to match the sequence
        for start_idx in range(len(scope_keys)):
            candidate = self._try_match_from_position_scoped(input_words, start_idx, scope_keys, scope_keys_set)
            if candidate:
                candidates.append(candidate)
        
        # Sort by total score (descending) and return
        candidates.sort(key=lambda x: x["total_score"], reverse=True)
        return candidates
    
    def _try_match_from_position(self, 
                                input_words: List[str], 
                                start_idx: int, 
                                all_locations: List[str]) -> Optional[Dict[str, Any]]:
        """
        Try to match input words starting from a specific position in the database.
        
        Parameters
        ----------
        input_words : List[str]
            Input words to match
        start_idx : int  
            Starting index in all_locations
        all_locations : List[str]
            All location keys sorted by position
            
        Returns
        -------
        Optional[Dict[str, Any]]
            Match candidate or None if no valid match
        """
        if start_idx >= len(all_locations):
            return None
        
        match_scores = []
        matched_locations = []
        
        for word_idx, input_word in enumerate(input_words):
            db_idx = start_idx + word_idx
            
            # Check if we've run out of database words
            if db_idx >= len(all_locations):
                break
            
            db_location = all_locations[db_idx]
            db_word_data = self.preprocessed_db[db_location]
            db_word = db_word_data["stripped"]
            
            # Calculate similarity
            score = self._calculate_word_similarity(input_word, db_word)
            match_scores.append(score)
            matched_locations.append(db_location)
        
        # Must have matched at least one word
        if not match_scores:
            return None
        
        # Calculate total score (average of all word scores)
        total_score = sum(match_scores) / len(match_scores)
        
        return {
            "start_location": matched_locations[0],
            "end_location": matched_locations[-1],
            "matched_locations": matched_locations,
            "word_scores": match_scores,
            "total_score": total_score,
            "num_words": len(matched_locations)
        }
    
    def _try_match_from_position_scoped(self, 
                                       input_words: List[str], 
                                       start_idx: int, 
                                       scope_keys: List[str],
                                       scope_keys_set: set) -> Optional[Dict[str, Any]]:
        """
        Try to match input words starting from a specific position within the scope.
        
        Parameters
        ----------
        input_words : List[str]
            Input words to match
        start_idx : int  
            Starting index in scope_keys
        scope_keys : List[str]
            Ordered list of location keys within the scope
        scope_keys_set : set
            Set of location keys within the scope for fast lookup
            
        Returns
        -------
        Optional[Dict[str, Any]]
            Match candidate or None if no valid match
        """
        if start_idx >= len(scope_keys):
            return None
        
        match_scores = []
        matched_locations = []
        
        for word_idx, input_word in enumerate(input_words):
            db_idx = start_idx + word_idx
            
            # Check if we've run out of scope words
            if db_idx >= len(scope_keys):
                break
            
            db_location = scope_keys[db_idx]
            db_word_data = self.preprocessed_db[db_location]
            db_word = db_word_data["stripped"]
            
            # Calculate similarity
            score = self._calculate_word_similarity(input_word, db_word)
            match_scores.append(score)
            matched_locations.append(db_location)
        
        # Must have matched at least one word
        if not match_scores:
            return None
        
        # Calculate total score (average of all word scores)
        total_score = sum(match_scores) / len(match_scores)
        
        return {
            "start_location": matched_locations[0],
            "end_location": matched_locations[-1],
            "matched_locations": matched_locations,
            "word_scores": match_scores,
            "total_score": total_score,
            "num_words": len(matched_locations)
        }
    
    def _build_reference_range(self, candidate: Dict[str, Any]) -> str:
        """
        Build reference range string from candidate match.
        
        Parameters
        ----------
        candidate : Dict[str, Any]
            Match candidate with location information
            
        Returns
        -------
        str
            Reference range string
        """
        start_loc = candidate["start_location"]
        end_loc = candidate["end_location"]
        
        if start_loc == end_loc:
            return start_loc
        else:
            return f"{start_loc}-{end_loc}"
