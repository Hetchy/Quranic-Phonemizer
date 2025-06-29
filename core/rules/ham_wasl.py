from __future__ import annotations
from typing import List

from .rule import Rule
from ..tokenizer import Token

class HamWaslRule(Rule):
    name = "ham_wasl"

    def process(self, tokens: List[Token], context) -> List[Token]:
        for tok_idx, tok in enumerate(tokens):
            if tok.text[0] == "ٱ":
                tok.mark_consumed_by(self.name)

                # Iltiqaa Sakinayan
                if tok_idx > 0:
                    prev_tok = tokens[tok_idx - 1]
                    if prev_tok.tag == "slnt":
                        prev_tok = tokens[tok_idx - 2]
                    if len(prev_tok.phonemes) > 0 and prev_tok.phonemes[-1] == ":":
                        prev_tok.phonemes.pop()
                    elif len(prev_tok.phonemes) > 0 and prev_tok.phonemes[-1].is_tanween():
                        prev_tok.phonemes.append(self._create_phoneme("i", "diacritics"))
                
                if not tok.is_start:
                    continue # silent when not beginning on the word, so skip

                if ( # noun case: always fatha
                    len(tok.text) > 1 and tok.text[1] == "ل"
                    or tokens[tok_idx + 1].tag == "laam_shamsiyah"
                    or (len(tokens[tok_idx + 1].text) > 0 and tokens[tok_idx + 1].text[0] == "ل")
                ):
                    ham_wasl_phs = [
                        self._create_phoneme("ʔ", "letters"),
                        self._create_phoneme("a", "diacritics")
                    ]
                    tok.phonemes = ham_wasl_phs + tok.phonemes
                
                else: # verb case: damma or kasra
                    phs = Token.get_word_phonemes(tokens, tok_idx)
                    
                    third_letter_ph_idx = None
                    letter_count = 1
                    for i, ph in enumerate(phs):
                        if ph.is_letter():
                            letter_count += 1
                            if letter_count == 3:
                                third_letter_ph_idx = i
                                break
                    
                    if third_letter_ph_idx is not None:
                        diacritic = phs[third_letter_ph_idx + 1]
                        if diacritic.name == "SHADDA":
                            diacritic = phs[third_letter_ph_idx + 2]
                        
                        if diacritic.name == "DAMMA":
                            vowel = "u"
                        elif diacritic.name in ["FATHA", "KASRA"]:
                            vowel = "i"
                        else:
                            raise ValueError(f"unknown hamza wasl case: {diacritic.name}")
                    else:
                        raise ValueError("no third letter found")
                    
                    ham_wasl_phs = [
                        self._create_phoneme("ʔ", "letters"),
                        self._create_phoneme(vowel, "diacritics")
                    ]
                    tok.phonemes = ham_wasl_phs + tok.phonemes
        
        return tokens