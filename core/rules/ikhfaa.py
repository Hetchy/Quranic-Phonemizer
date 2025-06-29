from __future__ import annotations
from typing import List

from .rule import Rule
from ..tokenizer import Token
from ..phoneme import Letter, tanween_to_diacritic


class IkhfaaRule(Rule):
    """
    Ikhfaa rule for noon saakinah/tanween when followed by one of the 15 ikhfaa letters.
    """
    name = "ikhfaa"

    def process(self, tokens: List[Token], context) -> List[Token]:
        light_phoneme = self.config.get('light_phoneme')
        heavy_phoneme = self.config.get('heavy_phoneme')
        heavy_letters_phonemes = self.config.get('heavy_letters_phonemes', [])
        
        light_ikhfaa_ph = self._create_phoneme(light_phoneme)
        heavy_ikhfaa_ph = self._create_phoneme(heavy_phoneme)
        heavy_letters_phs = [self._create_phoneme(ph) for ph in heavy_letters_phonemes]
        noon_ph = Letter.NOON

        i = 0
        while i < len(tokens):
            cur_tok = tokens[i]
            next_tok = tokens[i+1] if i + 1 < len(tokens) else None
            
            # Attempt to process as a two-token rule first
            if (
                i + 1 < len(tokens)
                and cur_tok.tag == self.name
                and next_tok.tag == self.name
                and self.name not in cur_tok.consumed_by
                and self.name not in next_tok.consumed_by
            ):
                ikhfaa_ph = heavy_ikhfaa_ph if next_tok.phonemes[0] in heavy_letters_phs else light_ikhfaa_ph

                if cur_tok.phonemes == [noon_ph]: # Noon Saakinah
                    cur_tok.phonemes = [ikhfaa_ph]
                
                else: # cur_tok.phonemes[-1] is tanween
                    cur_tok.phonemes[-1] = tanween_to_diacritic(cur_tok.phonemes[-1])
                    cur_tok.phonemes.append(ikhfaa_ph)
                
                cur_tok.mark_consumed_by(self.name)
                next_tok.mark_consumed_by(self.name)
                i += 2

            # If not a two-token rule, check for single-token Ikhfaa (noon + ikhfaa letter)
            elif cur_tok.tag == self.name and self.name not in cur_tok.consumed_by:
                if len(cur_tok.phonemes) < 2:
                    raise ValueError(f"Ikhfaa rule applied to a token with less than 2 phonemes: {cur_tok.location}")
                ikhfaa_ph = heavy_ikhfaa_ph if cur_tok.phonemes[1] in heavy_letters_phs else light_ikhfaa_ph
                cur_tok.phonemes[0] = ikhfaa_ph
                cur_tok.mark_consumed_by(self.name)
                i += 1
            
            else: # not ikhfaa, continue
                i += 1
        
        return tokens

class IkhfaaShafawiRule(Rule):
    """
    Ikhfaa Shafawi rule (labial concealment) when meem saakinah is followed by baa.
    """
    name = "ikhfaa_shafawi"

    def process(self, tokens: List[Token], context) -> List[Token]:
        ikhfaa_shafawi_ph = self.config.get('shafawi_phoneme')
        ikhfaa_shafawi_ph = self._create_phoneme(ikhfaa_shafawi_ph)
        
        i = 0
        while i < len(tokens) - 1:
            cur_tok = tokens[i]
            next_token = tokens[i + 1]

            if (
                cur_tok.tag == self.name
                and next_token.tag == self.name
                and self.name not in cur_tok.consumed_by
                and self.name not in next_token.consumed_by
            ): # replace Meem Saakinah with Ikhfaa Shafawi phoneme
                if cur_tok.phonemes:
                    cur_tok.phonemes[-1] = ikhfaa_shafawi_ph
                    cur_tok.mark_consumed_by(self.name)
                    next_token.mark_consumed_by(self.name)
                    i += 2
            else:
                i += 1
        
        return tokens
