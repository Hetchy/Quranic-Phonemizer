from __future__ import annotations
from typing import List

from .rule import Rule
from ..tokenizer import Token
from ..phoneme import Letter

class IqlabRule(Rule):
    name = "iqlab"

    def process(self, tokens: List[Token], context) -> List[Token]:
        iqlab_ph = self.config.get('phoneme')
        iqlab_ph = self._create_phoneme(iqlab_ph)

        i = 0
        while i < len(tokens):
            cur_tok = tokens[i]
            next_tok = tokens[i+1] if i + 1 < len(tokens) else None

            if ( # Iqlab across words (two tokens)
                next_tok
                and cur_tok.tag == self.name
                and next_tok.tag == self.name
                and self.name not in cur_tok.consumed_by
                and self.name not in next_tok.consumed_by
            ):
                if cur_tok.phonemes[-1] == Letter.NOON:
                    cur_tok.phonemes[-1] = iqlab_ph # replace noon with iqlab phoneme
                else: # last phoneme is a diacritic
                    cur_tok.phonemes += [iqlab_ph] # original letter and diacritic remain
                
                cur_tok.mark_consumed_by(self.name)
                next_tok.mark_consumed_by(self.name) # baa phoneme unchanged
                i += 2

            # Iqlab within word (single token)
            elif cur_tok.tag == self.name and self.name not in cur_tok.consumed_by:
                cur_tok.phonemes[0] = iqlab_ph # replace noon with iqlab phoneme
                cur_tok.mark_consumed_by(self.name)
                i += 1
            
            else: # not iqlab, continue
                i += 1
        
        return tokens