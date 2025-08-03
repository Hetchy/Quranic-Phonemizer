#!/usr/bin/env python3
"""
Debug script to load and pretty print verse "1:1" from Quran.json
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def debug_verse():
    """Load verse 1:1 and debug print each word."""
    # Import the refactored phonemizer directly
    from core.phonemizer_refactored import load_words
    
    print("Loading verse 1:1...")
    words = load_words("1:1")
    
    print(f"Found {len(words)} words in verse 1:1\n")
    
    for i, word in enumerate(words):
        print(f"--- Word {i+1} ---")
        print(word.debug_print())
        print()

if __name__ == "__main__":
    debug_verse()
