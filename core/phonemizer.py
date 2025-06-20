"""
core/phonemizer.py
==================
High-level orchestration using a hierarchical pipeline pattern:

    • tokenise a reference range
    • run preprocessing pipeline (initial mapping, boundaries, disambiguation)
    • run the ordered tajweed-rule pipeline
    • run postprocessing pipeline
    • format and return output

Pipeline stages are modular and can be easily extended or modified.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

import yaml

from .tokenizer import tokenize, Token
from .phoneme import Phoneme, Letter, Diacritic, map_word, create_phoneme, tanween_to_diacritic
from .helpers import compile_text
from .pipeline import PipelineContext, PipelineStage, CompositePipelineStage
from .result import PhonemizeResult
from .rules.ham_wasl import HamWaslRule
from .rules.idgham import GhunnahRule, IdghamGhunnahRule, IdghamWoGhunnahRule, IdghamShafawiRule, IdghamMutamathilaynRule, IdghamMutajanisaynRule, IdghamMutaqaribaynRule
from .rules.ikhfaa import IkhfaaRule, IkhfaaShafawiRule
from .rules.iqlab import IqlabRule
from .rules.qalqala import QalqalaRule

DATA_DIR = Path(__file__).resolve().parent.parent / "resources"


# ------------------------------------------------------------------ #
# Main Phonemizer Class                                              #
# ------------------------------------------------------------------ #

class Phonemizer:
    def __init__(
        self,
        db_path: str | Path = DATA_DIR / "Quran.json",
        map_path: str | Path = DATA_DIR / "base_phonemes.yaml",
        rule_cfg: str | Path = DATA_DIR / "rule_phonemes.yaml",
    ) -> None:
        self.db_path = str(db_path)
        self.rule_cfg_path = rule_cfg
        self.pipeline = self._build_pipeline()
  
    def _build_pipeline(self) -> CompositePipelineStage:
        """Build the processing pipeline"""
        configs = self._load_rule_configs(self.rule_cfg_path)
        
        return CompositePipelineStage([
            CompositePipelineStage([ # Preprocessing
                InitialPhonemeMapper(),
                WordBoundaryHandler(),
                ConditionalPhonemeDisambiguator(),
                WordEndAlefHandler(),
            ]),

            CompositePipelineStage([ # Tajweed Rules
                HamWaslRule(configs.get('ham_wasl', {})),
                QalqalaRule(configs.get('qalqala', {})),
                IqlabRule(configs.get('iqlab', {})),
                CompositePipelineStage([
                    GhunnahRule(configs.get('idgham', {})),
                    IdghamGhunnahRule(configs.get('idgham', {})),
                    IdghamWoGhunnahRule(configs.get('idgham', {})),
                    IdghamShafawiRule(configs.get('idgham', {})),
                    IdghamMutamathilaynRule(configs.get('idgham', {})),
                    IdghamMutajanisaynRule(configs.get('idgham', {})),
                    IdghamMutaqaribaynRule(configs.get('idgham', {})),
                ]),
                CompositePipelineStage([
                    IkhfaaRule(configs.get('ikhfaa', {})),
                    IkhfaaShafawiRule(configs.get('ikhfaa', {})),
                ]),
            ]),

            CompositePipelineStage([ # Postprocessing
                # either duplicate in the same or new phoneme e.g. ['tt'] vs ['t', 't']
                ShaddaHandler(seperate_phonemes=False),
                LongVowelHandler(),
                TanweenHandler(),
            ]),
        ])
    
    def phonemize(
        self,
        ref: str,
        *,
        stops: List[str] = [],
    ) -> PhonemizeResult:
        """
        Parameters
        ----------
        ref : str
            Qurʾānic reference (supported formats handled by tokenizer).
        stops : List[str], default []
            List of stop types to mark as boundaries. Can include:
            - "verse": Mark verse boundaries
            - "preferred_continue": ۖ 
            - "preferred_stop": ۗ 
            - "optional_stop": ۚ 
            - "compulsory_stop": ۘ 
            - "prohibited_stop": ۙ 
        Returns
        -------
        PhonemizeResult
            Object containing reference, text and phonemes.
        """
        context = PipelineContext(
            db_path=self.db_path,
            ref=ref,
            stops=stops,
        )
        
        tokens = tokenize(ref, stops=stops, db_path=self.db_path)
        tokens = self.pipeline.process(tokens, context)
        
        phoneme_arrays = self._format_phonemes(tokens)
        quran_text = compile_text(ref, db_path=self.db_path)

        return PhonemizeResult(
            ref=ref,
            text=quran_text,
            _nested=phoneme_arrays,
            _tokens=tokens,
        )
    
    def _load_rule_configs(self, cfg_path: str | Path) -> dict:
        """
        Load rule configurations from YAML file.
        """
        return yaml.safe_load(Path(cfg_path).read_text(encoding="utf-8"))
    
    def _format_phonemes(
        self,
        tokens: List[Token],
    ) -> List[List[str]]:
        """
        Build an array of arrays of phonemes, where each inner array represents a word's phonemes.
        """
        if not tokens:
            return []

        out: List[List[str]] = []
        current_word_phonemes: List[str] = []
        prev_location = tokens[0].location

        for tok in tokens:
            if tok.location != prev_location:
                out.append(current_word_phonemes)
                current_word_phonemes = []
            current_word_phonemes.extend(str(p) for p in tok.phonemes)
            prev_location = tok.location

        if current_word_phonemes:
            out.append(current_word_phonemes)

        return out

# ------------------------------------------------------------------ #
# Pipeline Stages Implementation                                     #
# ------------------------------------------------------------------ #

class Debugger(PipelineStage):
    """Debug the tokens"""
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for tok in tokens:
            print(tok.text, tok.phonemes)
        return tokens

class InitialPhonemeMapper(PipelineStage):
    """Apply initial phoneme mapping to tokens"""
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for tok in tokens:
            if tok.tag not in ["laam_shamsiyah", "slnt", "special"]:
                tok.phonemes = map_word(tok.text)
        return tokens


class WordBoundaryHandler(PipelineStage):
    """Handle word start and end boundary processing (Waqf and Ibtidaa)"""
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for tok_idx, tok in enumerate(tokens):
            if tok.tag == "special":
                continue

            if tok.is_start:
                self._handle_word_start(tok)
            
            if tok.is_end:
                self._handle_word_end(tokens, tok_idx)
        
        return tokens
    
    def _handle_word_start(self, tok: Token) -> None:
        """Handle word start boundary processing"""
        # 1. remove rule tags
        if tok.tag and (
            tok.tag.startswith("idgham") or
            tok.tag.startswith("ikhfaa") or
            tok.tag == "iqlab"
        ):
            tok.tag = None
        
        # 2. remove shadda on starting letter
        if (
            len(tok.phonemes) >= 2
            and tok.phonemes[0].is_letter()
            and tok.phonemes[1] == Diacritic["SHADDA"]
        ):
            tok.phonemes.pop(1)
    
    def _handle_word_end(self, tokens: List[Token], tok_idx: int) -> None:
        """Handle word end boundary processing"""
        # 1. remove rule tags
        tag = tokens[tok_idx].tag
        if tag and (
            tag.startswith("idgham") or
            tag.startswith("ikhfaa") or
            tag == "iqlab"
        ):
            tokens[tok_idx].tag = None
        
        if not tokens[tok_idx].phonemes:
            return
        
        # 2. diacritic handling
        last_ph = tokens[tok_idx].phonemes[-1]
        second_last_ph = tokens[tok_idx].phonemes[-2] if len(tokens[tok_idx].phonemes) >= 2 else None
        
        # 2a. hamza + fathatan  ->  hamza + fatha
        if (
            second_last_ph == Letter["HAMZA"]
            and last_ph == Diacritic["FATHATAN"]
        ):
            tokens[tok_idx].phonemes[-1] = tanween_to_diacritic(last_ph)

        # 2b. _ + fathatan + alef  ->  _ + fatha + alef
        elif (
            second_last_ph == Diacritic["FATHATAN"]
            and last_ph == Letter["ALEF"]
        ):
            tokens[tok_idx].phonemes[-2] = tanween_to_diacritic(second_last_ph)

        # 2c. remove diacritic(s) or other symbols on last letter
        else:
            while (
                tokens[tok_idx].phonemes
                and not tokens[tok_idx].phonemes[-1].is_letter()
                and tokens[tok_idx].phonemes[-1] not in [Diacritic["SHADDA"], Diacritic["SUKUN"]]
            ):
                tokens[tok_idx].phonemes.pop()
        
        if not tokens[tok_idx].phonemes:
            return

        # 3. add qalqala tag if ending in qalqala letter
        phs_before, phs_after = Token.get_word_phonemes_split(tokens, tok_idx, 0)
        last_letter_ph = None
        for ph in [*phs_before, tokens[tok_idx].phonemes[0], *phs_after][::-1]:
            if ph.is_letter():
                last_letter_ph = ph
                break
        
        if last_letter_ph in [
            Letter["QAF"],
            Letter["TTA"],
            Letter["BA"],
            Letter["JEEM"],
            Letter["DAL"]
        ]:
            qalqala_tok_idx = tok_idx
            while last_letter_ph not in tokens[qalqala_tok_idx].phonemes:
                qalqala_tok_idx -= 1
            if not tokens[qalqala_tok_idx].tag:
                tokens[qalqala_tok_idx].tag = "qalqala"


class ConditionalPhonemeDisambiguator(PipelineStage):
    """
    Disambiguate conditional phonemes (yaa/waw/etc.)
    Special cases with dagger (alef):
        (A) fatha + dagger                 = [a]       -> dagger = ":"
        (B) fatha + alef maksura + dagger  = [a:]      -> dagger = ""
        (C) consonant w/o fatha + dagger   = [c, a:]   -> dagger = "a:"
        (D) waw/yaa w/o fatha + dagger     = [w/j, a:] -> dagger = "a:"
    """
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for tok_idx, tok in enumerate(tokens):
            if not tok.phonemes:
                continue

            for k, cur_ph in enumerate(tok.phonemes):
                if cur_ph.name == "DAGGER_ALEF":
                    self._disambiguate_dagger_alef(tokens, tok_idx, k, cur_ph)
                elif cur_ph.is_conditional():
                    self._disambiguate_conditional(tokens, tok_idx, k, cur_ph)
        
        return tokens
    
    def _disambiguate_dagger_alef(self, tokens: List[Token], tok_idx: int, ph_idx: int,
                                  cur_ph: Phoneme) -> None:
        """Handle dagger alef disambiguation"""
        tok = tokens[tok_idx]
        [short_vowel, long_vowel] = cur_ph.get_conditional_options()
        phs_before, _ = Token.get_word_phonemes_split(tokens, tok_idx, ph_idx)
        
        if len(phs_before) == 0:
            return

        if phs_before[-1] == Diacritic["FATHA"]: # case (A)
            cur_ph.assign(short_vowel)
        elif phs_before[-1].name == "ALEF_MAKSURA": # case (B)
            tok.phonemes.pop(ph_idx)
        else: # case (C)
            cur_ph.assign(long_vowel)
    
    
    def _disambiguate_conditional(self, tokens: List[Token], tok_idx: int, ph_idx: int,
                                  cur_ph: Phoneme) -> None:
        """Handle conditional phoneme disambiguation (Yaa/Waw/Alef-Maksura/Taa-Marbuta)"""
        [consonant, vowel] = cur_ph.get_conditional_options()

        has_diacritic_after = False
        _, phs_after = Token.get_word_phonemes_split(tokens, tok_idx, ph_idx)
        if len(phs_after) > 0 and phs_after[0].is_diacritic():
            has_diacritic_after = True

        if ( # case (D)
            cur_ph.name in ["YA", "WAW"]
            and len(phs_after) > 0
            and phs_after[0].name == "DAGGER_ALEF"
        ):
            cur_ph.assign(consonant)
        elif has_diacritic_after:
            cur_ph.assign(consonant)
        else:
            cur_ph.assign(vowel)


class WordEndAlefHandler(PipelineStage):
    """Process alef phonemes at the end of words"""
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for tok_idx, tok in enumerate(tokens):
            if not tok.phonemes:
                continue
                
            phs_before, phs_after = Token.get_word_phonemes_split(tokens, tok_idx, len(tok.phonemes) - 1)
            if len(phs_after) > 0:
                continue
                
            word_phs = [*phs_before, tok.phonemes[-1]]
            
            if (  # fatha + alef + sukoon  ->  fatha
                len(word_phs) >= 3
                and word_phs[-3] == Diacritic["FATHA"]
                and word_phs[-2] == Letter["ALEF"]
                and word_phs[-1] == Diacritic["SUKUN"]
                and not tok.is_end  # only applies on continued recitation
            ):
                tok.phonemes.pop()
                tok.phonemes.pop()
            
            elif (  # _ + fathatan + alef  ->  _ + fathatan
                len(word_phs) >= 2
                and word_phs[-2] == Diacritic["FATHATAN"]
                and word_phs[-1] == Letter["ALEF"]
            ):
                tok.phonemes.pop()
            
            elif (  # lam + alef + fathatan  ->  lam + fathatan
                len(word_phs) >= 3
                and word_phs[-3] == Letter["LAM"]
                and word_phs[-2] == Letter["ALEF"]
                and word_phs[-1] == Diacritic["FATHATAN"]
            ) or (  # lam + shadda + alef + fathatan  ->  lam + fathatan
                len(word_phs) >= 4
                and word_phs[-4] == Letter["LAM"]
                and word_phs[-3] == Diacritic["SHADDA"]
                and word_phs[-2] == Letter["ALEF"]
                and word_phs[-1] == Diacritic["FATHATAN"]
            ):
                tok.phonemes.pop(-2)

            elif (  # lam + alef  ->  lam + fatha + alef
                len(word_phs) >= 2
                and word_phs[-2] == Letter["LAM"]
                and word_phs[-1] == Letter["ALEF"]
            ):
                fatha = Diacritic["FATHA"]
                tok.phonemes.insert(-1, create_phoneme("a", "diacritics"))
        
        return tokens


class LongVowelHandler(PipelineStage):
    """Merge ':' with previous phoneme to create long vowels"""
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for i, tok in enumerate(tokens):
            if not tok.phonemes:
                continue
                
            new_phs = []
            for ph_idx, ph in enumerate(tok.phonemes):
                if ph == Diacritic["SUKUN"]:
                    continue
                elif ph == ":":
                    prev_phs, _ = Token.get_word_phonemes_split(tokens, i, ph_idx)
                    if len(prev_phs) > 0:
                        prev_ph = prev_phs[-1]
                        # Create new phoneme with extended length
                        new_phoneme = create_phoneme(
                            prev_ph.phoneme + ":", "vowel"
                        )
                        
                        # Find where to place the new phoneme
                        if len(new_phs) > 0 and new_phs[-1] is prev_ph:
                            # Replace in current token
                            new_phs[-1] = new_phoneme
                        else:
                            # Find and replace in previous tokens
                            for prev_tok_idx in range(i-1, -1, -1):
                                prev_tok = tokens[prev_tok_idx]
                                if prev_tok.phonemes:
                                    for j, ph in enumerate(prev_tok.phonemes):
                                        if ph is prev_ph:
                                            prev_tok.phonemes[j] = new_phoneme
                                            break
                                    break
                else:
                    new_phs.append(ph)
            
            tok.phonemes = new_phs
        
        return tokens


class ShaddaHandler(PipelineStage):
    """Duplicate previous phoneme for shadda"""
    
    def __init__(self, seperate_phonemes: bool = False):
        self.seperate_phonemes = seperate_phonemes

    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for tok_idx, tok in enumerate(tokens):
            if not tok.phonemes:
                continue
                
            new_phs = []
            for ph_idx, ph in enumerate(tok.phonemes):
                if ph == Diacritic["SHADDA"]:
                    prev_phs, _ = Token.get_word_phonemes_split(tokens, tok_idx, ph_idx)
                    if len(prev_phs) > 0 and prev_phs[-1].is_letter():
                        if self.seperate_phonemes:
                            new_phs.append(prev_phs[-1])
                        else:
                            prev_phs[-1].phoneme += prev_phs[-1].phoneme
                            if len(new_phs) > 0:
                                new_phs[-1] = prev_phs[-1]
                            else:
                                tokens[tok_idx - 1].phonemes[-1] = prev_phs[-1]
                else:
                    new_phs.append(ph)
            
            tok.phonemes = new_phs
        
        return tokens


class TanweenHandler(PipelineStage):
    """Split tanween into two phonemes"""
    
    def process(self, tokens: List[Token], context: PipelineContext) -> List[Token]:
        for tok in tokens:
            if not tok.phonemes:
                continue
                
            new_phs = []
            for ph in tok.phonemes:
                if ph.is_tanween():
                    new_phs.append(ph.phoneme[0])
                    new_phs.append(ph.phoneme[1])
                elif ph != Diacritic["SUKUN"]:
                    new_phs.append(ph)
            
            tok.phonemes = new_phs
        
        return tokens