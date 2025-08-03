#!/usr/bin/env python3
"""
Demo script for the modularized phonemizer.
"""

from core import Phonemizer

def main():
    """Demonstrate the modularized phonemizer."""
    print("Quranic Phonemizer - Modularized Version Demo")
    print("=" * 50)
    
    # Create phonemizer instance
    phonemizer = Phonemizer()
    
    # Test with verse 1:1
    print("\nPhonemizing verse 1:1...")
    result = phonemizer.phonemize("1:1")
    
    print(f"Reference: {result.reference}")
    print(f"Text: {result.text}")
    print(f"Phonemes: {result.phonemes}")
    
    # Test with a single word
    print("\nPhonemizing word 1:1:1 (بِسۡمِ)...")
    result = phonemizer.phonemize("1:1:1")
    
    print(f"Reference: {result.reference}")
    print(f"Text: {result.text}")
    print(f"Phonemes: {result.phonemes}")

if __name__ == "__main__":
    main()
