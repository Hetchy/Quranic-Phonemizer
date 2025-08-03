#!/usr/bin/env python3
"""
Test script for the modularized phonemizer.
"""

from core.phonemizer_refactored import Phonemizer

def test_phonemizer():
    """Test the modularized phonemizer with a simple example."""
    print("Testing modularized phonemizer...")
    
    # Create phonemizer instance
    phonemizer = Phonemizer()
    
    # Test with verse 1:1
    result = phonemizer.phonemize("1:1")
    
    print(f"Reference: {result.reference}")
    print(f"Text: {result.text}")
    print(f"Phonemes: {result.phonemes}")
    
    # Test with a single word
    result = phonemizer.phonemize("1:1:1")
    
    print(f"\nReference: {result.reference}")
    print(f"Text: {result.text}")
    print(f"Phonemes: {result.phonemes}")

if __name__ == "__main__":
    test_phonemizer()
