from .rule import Rule
from ..tokenizer import Token
from typing import List
from ..phoneme import Diacritic, create_phoneme

class QalqalaRule(Rule):
    name = "qalqala"

    def process(self, tokens: List[Token], context) -> List[Token]:
        for tok_idx, tok in enumerate(tokens):
            if tok.tag == self.name and self.name not in tok.consumed_by:
                self._apply_qalqala(tokens, tok_idx)
                tok.mark_consumed_by(self.name)
        
        return tokens

    def _apply_qalqala(self, tokens: List[Token], tok_idx: int) -> None:
        tok = tokens[tok_idx]
        for ph_cfg in self.config.get("phonemes"):
            qalqala_letter_ph = ph_cfg.get("target")
            qalqala_letter_ph = create_phoneme(qalqala_letter_ph, "special")
            
            if qalqala_letter_ph in tok.phonemes:
                
                _, phs_after = Token.get_word_phonemes_split(tokens, tok_idx, tok.phonemes.index(qalqala_letter_ph))
                is_last_letter = [ph for ph in phs_after if ph.is_letter()] == []
                diacritic = phs_after[0] if phs_after else None

                qalqala_ph = None
                if is_last_letter:
                    if diacritic in [None, Diacritic.SUKUN]:
                        qalqala_ph = ph_cfg.get("strong")
                    elif diacritic == Diacritic.SHADDA:
                        if len(phs_after) == 1: # ensure no other diacritic after shadda
                            qalqala_ph = ph_cfg.get("strongest")
                    # Do not apply Qalqala for any other cases, as it is not a stopping word
                else:
                    qalqala_ph = ph_cfg.get("weak")
                
                if qalqala_ph:
                    tok.phonemes.append(create_phoneme(qalqala_ph, "special"))
                    return
                

