"""
Idgham (assimilation) rules for Tajweed.

This module contains all idgham rules, including:
- Ghunnah: noon/meem with shadda (technically idgham on the same letter)
- Idgham Ghunnah: with nasal sound 
- Idgham without Ghunnah: no nasal sound
- Idgham Shafawi: labial assimilation
- Idgham Mutajanisayn: similar sounds assimilation
- Idgham Mutaqaribayn: close sounds assimilation

Idgham (إدغام) is the process of assimilating certain letters when they
appear in specific combinations.
"""

from __future__ import annotations
from typing import List

from .rule import Rule
from ..tokenizer import Token
from ..phoneme import Letter, Diacritic
from ..phoneme import tanween_to_diacritic


class GhunnahRule(Rule):
    name = "ghunnah"
        
    def process(self, tokens: List[Token], context) -> List[Token]:
        for tok in tokens:
            if tok.tag == self.name and self.name not in tok.consumed_by:
                nasalized_map = self.config.get('nasalized_map', {})
                noon_phoneme = nasalized_map.get('n')
                meem_phoneme = nasalized_map.get('m')
                
                nasalized_noon_ph = self._create_phoneme(noon_phoneme)
                nasalized_meem_ph = self._create_phoneme(meem_phoneme)
                
                ghunnah_ph = tok.phonemes[0]
                if ghunnah_ph == Letter.NOON:
                    tok.phonemes = [nasalized_noon_ph]
                elif ghunnah_ph == Letter.MEEM:
                    tok.phonemes = [nasalized_meem_ph]
                
                tok.mark_consumed_by(self.name)
        
        return tokens


class IdghamGhunnahRule(Rule):
    name = "idgham_ghunnah"

    def process(self, tokens: List[Token], context) -> List[Token]:        
        nasalized_map = self.config.get('nasalized_map')
        nasalized_map = {k: self._create_phoneme(v) for k, v in nasalized_map.items()}
        
        i = 0
        while i < len(tokens) - 1:
            cur_tok = tokens[i]
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            
            if ( # both tokens are tagged
                next_tok
                and cur_tok.tag == self.name
                and next_tok.tag == self.name
                and self.name not in cur_tok.consumed_by
                and self.name not in next_tok.consumed_by
            ):
                cur_ph = cur_tok.phonemes
                next_ph = next_tok.phonemes
                if cur_ph[-1].is_tanween():
                    cur_ph[-1] = tanween_to_diacritic(cur_ph[-1])
                
                elif cur_ph[-1] == Letter.NOON:
                    cur_ph.pop() # remove noon
                
                else:
                    raise ValueError(f"Invalid Idgham Ghunnah rule in {cur_tok.location}:\n{cur_tok.phonemes}\n{next_tok.phonemes}")  
                
                # nasalize j/n/m/w
                if next_ph[0] in nasalized_map:
                    next_ph[0] = nasalized_map[next_ph[0]]
                else:
                    i += 2
                    continue
                
                # remove shaddah on third token
                has_shaddah = tokens[i+2].phonemes[0] == Diacritic.SHADDA
                if has_shaddah:
                    tokens[i + 2].phonemes.pop(0)

                cur_tok.mark_consumed_by(self.name)
                next_tok.mark_consumed_by(self.name)
                i += 2
            else:
                i += 1
        
        return tokens


class IdghamWoGhunnahRule(Rule):
    name = "idgham_wo_ghunnah"

    def process(self, tokens: List[Token], context) -> List[Token]:
        i = 0
        while i < len(tokens) - 1:
            cur_tok = tokens[i]
            next_tok = tokens[i+1] if i + 1 < len(tokens) else None
            
            if (
                next_tok
                and cur_tok.tag == self.name
                and next_tok.tag == self.name
                and self.name not in cur_tok.consumed_by
                and self.name not in next_tok.consumed_by
            ):
                cur_ph = cur_tok.phonemes
                if cur_ph[-1].is_tanween():
                    cur_ph[-1] = tanween_to_diacritic(cur_ph[-1])
                elif Letter.NOON in cur_ph:
                    cur_ph.pop() # remove noon
                
                cur_tok.mark_consumed_by(self.name)
                next_tok.mark_consumed_by(self.name)
                i += 2
            else:
                i += 1
        
        return tokens


class IdghamMutajanisaynRule(Rule):
    name = "idgham_mutajanisayn"

    def process(self, tokens: List[Token], context) -> List[Token]:
        for token in tokens:
            if token.tag == self.name and self.name not in token.consumed_by:
                token.phonemes.pop()
                token.mark_consumed_by(self.name)
        
        return tokens

class IdghamMutaqaribaynRule(IdghamMutajanisaynRule):
    name = "idgham_mutaqaribayn"

class IdghamMutamathilaynRule(IdghamMutajanisaynRule):
    name = "idgham_mutamathilayn"

class IdghamShafawiRule(Rule):
    name = "idgham_shafawi"

    def process(self, tokens: List[Token], context) -> List[Token]:        
        i = 0
        nasalized_map = self.config.get('nasalized_map', {})
        meem_phoneme = nasalized_map.get('m')
        nasalized_meem = self._create_phoneme(meem_phoneme)

        while i < len(tokens) - 2:
            cur_tok = tokens[i]
            next_tok = tokens[i+1]
            if (
                cur_tok.tag == self.name
                and next_tok.tag == self.name
                and self.name not in cur_tok.consumed_by
                and self.name not in next_tok.consumed_by
            ):
                if cur_tok.phonemes[-1] == Letter.MEEM:
                    cur_tok.phonemes[-1] = nasalized_meem
                
                    # Remove meem from second token
                    next_tok.phonemes.pop(0)

                    # Remove shaddah from third token
                    if tokens[i+2].phonemes[0] == Diacritic.SHADDA:
                        tokens[i+2].phonemes.pop(0)
                
                    cur_tok.mark_consumed_by(self.name)
                    next_tok.mark_consumed_by(self.name)
                    i += 2
                else:
                    raise ValueError(f"Invalid Idgham Shafawi rule:\n{cur_tok.phonemes}\n{next_tok.phonemes}")
            else:
                i += 1
        
        return tokens
