"""
core/helpers.py
================
Utility helpers shared across the package.
"""
from __future__ import annotations

# These utilities are mainly for notebooks / debugging; guarded import.
try:
    from IPython.display import display, HTML  # type: ignore
except ModuleNotFoundError:     # graceful fallback in non-notebook runs
    def display(x):  # type: ignore
        print(x)
    HTML = str  # type: ignore

import re
from pathlib import Path
from typing import Dict, List, Tuple, Iterable
from .loader import load_db, keys_for_reference


# ------------------------------------------------------------------ #
# private helpers                                                    #
# ------------------------------------------------------------------ #

_TAG_RE   = re.compile(r"</?rule[^>]*?>", re.IGNORECASE | re.DOTALL)

def _strip_rule_tags(text: str) -> str:
    """Remove <rule …> wrappers, keep interior letters unchanged."""
    return _TAG_RE.sub("", text)

def _ayah_end(num: int) -> str:
    """Return Qurʾānic verse-end marker with embedded number."""
    ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
    num = "".join(ARABIC_DIGITS[int(d)] for d in str(num))
    RLM = "\u200F"                       # right-to-left mark
    return f"{RLM}﴿{num}﴾{RLM}"

# internal verse-grouper
def _words_by_verse(
    keys: Iterable[str], db: Dict[str, Dict[str, str]]
) -> Dict[str, List[str]]:
    """
    Return {'s:v': [word1, word2, …]} **with `<rule>` tags stripped**.
    *keys* is an iterable of DB keys ('s:v:w').
    """
    verses: Dict[str, List[Tuple[int, str]]] = {}

    for key in keys:
        s, v, w = key.split(":")
        raw = db[key]["text"]
        if isinstance(raw, list):
            raw = "".join(raw)
        verses.setdefault(f"{s}:{v}", []).append((int(w), _strip_rule_tags(raw)))

    return {k: [t for _, t in sorted(v)] for k, v in verses.items()}


# ------------------------------------------------------------------ #
# public API                                                         #
# ------------------------------------------------------------------ #

def compile_text(
    ref: str,
    *,
    db_path: str | Path = "resources/Quran.json",
) -> str:
    """
    Build Qurʾānic text for *ref* without tajweed tags, inserting
    «﴾n﴿» after every complete verse inside the range.
    """
    db   = load_db(db_path)
    keys = keys_for_reference(ref, db)
    if not keys:
        return ""

    out: list[str] = []

    for i, k in enumerate(keys):
        cur_s, cur_v, cur_w = (int(x) for x in k.split(":"))
        raw = db[k]["text"]
        if isinstance(raw, list):
            raw = "".join(raw)

        out.append(_strip_rule_tags(raw).strip())

        # -- verse boundary check --------------------------------------
        next_key = keys[i + 1] if i + 1 < len(keys) else None
        if (
            next_key is None                                         # end of selection
            or next_key.split(":")[:2] != [str(cur_s), str(cur_v)]   # verse changes
        ):
            out.append(_ayah_end(cur_v))                             # <-- OWN CHUNK

    return " ".join(out)

def display_verses_with_codepoints(
    codepoints: List[str],
    *,
    ref: str | None = None,
    db_path: str | Path = "resources/Quran.json",
    highlight_colour: str = "red",
) -> None:
    """
    Show every verse whose **letters contain *all* the Unicode code‐points**
    in *codepoints*.  Useful when hunting rare glyphs like daggers alef.

    Parameters
    ----------
    codepoints : list[str]
        e.g. ``['0623', '0670']`` (hex, upper/lowercase both fine).
    ref : str | None
        Restrict the search to this reference range (same format accepted
        by :func:`core.loader.keys_for_reference`).  ``None`` = whole muṣḥaf.
    db_path : str | Path
        Path to the Qurʾān word-by-word JSON.
    highlight_colour : str
        CSS colour used to highlight characters that match the codepoints.
    """
    db = load_db(db_path)
    keys = keys_for_reference(ref, db) if ref else db.keys()

    verse_words = _words_by_verse(keys, db)
    targets     = {int(c, 16) for c in codepoints}

    matches = [
        (verse, words)
        for verse, words in verse_words.items()
        if targets.issubset({ord(ch) for w in words for ch in w})
    ]

    header = f"<h3>{len(matches)} verse(s) contain {' & '.join('U+'+c.upper() for c in codepoints)}</h3>"
    if ref:
        header += f"<p>Search restricted to <code>{ref}</code></p>"
    display(HTML(header))

    for verse, words in matches:
        rendered = []
        for w in words:
            highlighted_word = ""
            for ch in w:
                if ord(ch) in targets:
                    highlighted_word += f"<span style='color:{highlight_colour};font-weight:bold'>{ch}</span>"
                else:
                    highlighted_word += ch
            rendered.append(highlighted_word)
        display(HTML(f"<p><strong>{verse}</strong> — {' '.join(rendered)}</p>"))

def display_verses_with_rule(
    rule: str,
    *,
    ref: str | None = None,
    db_path: str | Path = "resources/Quran.json",
    highlight_colour: str = "red",
    return_html: bool = False,
) -> None | str:
    """
    Show every verse that contains at least one segment wrapped in
    ``<rule class=<rule>>…</rule>``.

    Parameters
    ----------
    rule : str
        Tajweed rule name, exactly as it appears in the ``class=`` attribute.
    ref : str | None
        Reference range to limit the search (``None`` = whole Qurʾān).
    db_path : str | Path
        Path to the DB JSON.
    highlight_colour : str
        CSS colour for highlighted rule segments.
    """
    db = load_db(db_path)
    keys = keys_for_reference(ref, db) if ref else db.keys()

    verse_words_raw = _words_by_verse(keys, db)  # words **without** tags

    # We need tagged words, so fetch again (raw text) for the same keys
    verse_words_tagged: Dict[str, List[str]] = {}
    for k in keys:
        s, v, w = k.split(":")
        verse_words_tagged.setdefault(f"{s}:{v}", []).append(db[k]["text"])

    TAG_RE = re.compile(r"<rule class=([^>]+)>(.*?)</rule>", re.IGNORECASE | re.DOTALL)

    matches = []
    total_rule_occurrences = 0
    for verse, word_list in verse_words_tagged.items():
        # Keep input order
        word_list_sorted = [t for _, t in sorted(zip(
            (int(k.split(':')[2]) for k in db if k.startswith(verse+':')), word_list))]

        found = False
        rendered_words = []
        verse_rule_count = 0

        for w in word_list_sorted:
            # normalise list/str
            w_str = "".join(w) if isinstance(w, list) else w

            def repl(m: re.Match[str]) -> str:
                nonlocal found, verse_rule_count
                cls, inner = m.group(1), m.group(2)
                if cls == rule:
                    found = True
                    verse_rule_count += 1
                    return f"<span style='color:{highlight_colour};font-weight:bold'>{inner}</span>"
                return inner

            rendered_words.append(TAG_RE.sub(repl, w_str))

        if found:
            matches.append((verse, " ".join(rendered_words), verse_rule_count))
            total_rule_occurrences += verse_rule_count

    header = f"<h3>{len(matches)} verse(s) contain rule <code>{rule}</code></h3>"
    header += f"<h4>Total occurrences: {total_rule_occurrences}</h4>"
    if ref:
        header += f"<p>Search restricted to <code>{ref}</code></p>"
    html_output = [header]

    for verse, html_txt, verse_rule_count in matches:
        html_output.append(f"<p><strong>{verse}</strong> — {html_txt} <span style='color:gray'>(Occurrences in verse: {verse_rule_count})</span></p>")

    if return_html:
        return "\n".join(html_output)
    else:
        display(HTML(header))
        for verse, html_txt, verse_rule_count in matches:
            display(HTML(f"<p><strong>{verse}</strong> — {html_txt} <span style='color:gray'>(Occurrences in verse: {verse_rule_count})</span></p>"))  # nosec B703

def save_verses_with_all_rules(
    rules_yaml_path: str = "resources/rule_phonemes.yaml",
    output_dir: str = "data/tajweed_occurences",
    db_path: str | Path = "resources/Quran.json",
    highlight_colour: str = "red",
):
    """
    For each rule in the YAML file, run display_verses_with_rule and save the output to <output_dir>/<rule_name>.md
    Compatible with rule_phonemes.yaml where each rule is a dict with a 'name' field.
    """
    import os
    import yaml
    # Read all rule names from the YAML file (using 'name' field)
    with open(rules_yaml_path, encoding="utf-8") as f:
        rules_yaml = yaml.safe_load(f)
    rules = [r["name"] for r in rules_yaml.get("rules", []) if isinstance(r, dict) and "name" in r]

    os.makedirs(output_dir, exist_ok=True)
    for rule in rules:
        html = display_verses_with_rule(
            rule,
            db_path=db_path,
            highlight_colour=highlight_colour,
            return_html=True
        )
        out_path = os.path.join(output_dir, f"{rule}.md")
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(html if html else "")

def phonemize_and_save(
    ref: str,
    *,
    db_path: str | Path = "resources/Quran.json",
    output_dir: str | Path = "data/phonemized",
    stops: List[str] = [],
) -> None:
    """
    Phonemize a given reference and save the formatted output to a file.
    
    The output format is:
    - Each line contains a word followed by its phoneme array
    - All phoneme arrays are aligned to start at the same column
    - Extra newline at verse endpoints (no verse numbers/markers)
    - File is saved as data/phonemized/<ref>.txt
    
    Parameters
    ----------
    ref : str
        Quranic reference (e.g., "69:24", "2:1-5")
    db_path : str | Path
        Path to the Quran database
    output_dir : str | Path
        Directory to save the phonemized output
    """
    from .phonemizer import Phonemizer
    import os
    import unicodedata
    
    def visual_width(text):
        """Calculate visual width by removing combining characters (diacritics)"""
        # Remove combining characters (Arabic diacritics)
        normalized = ''.join(c for c in text if not unicodedata.combining(c))
        return len(normalized)
    
    def align_at_column(word, phoneme_str, target_col=20):
        """Align phoneme string to start at target column"""
        word_width = visual_width(word)
        if word_width >= target_col:
            # If word is too long, truncate and add space
            # We need to be careful with Arabic text truncation
            spaces_needed = 1
        else:
            spaces_needed = target_col - word_width
        return word + (" " * spaces_needed) + phoneme_str
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Phonemize the reference
    phonemizer = Phonemizer(db_path=db_path)
    res = phonemizer.phonemize(ref, stops=stops)
    quran_text = res.text
    phoneme_arrays = res.phonemes_nested()
    
    if not quran_text or not phoneme_arrays:
        print(f"No content found for reference: {ref}")
        return
    
    # Build the output lines
    output_lines = []

    db = load_db(db_path)
    keys = keys_for_reference(ref, db)
    
    current_verse = None
    phoneme_index = 0
    
    for key in keys:
        s, v, _ = key.split(":")
        verse_key = f"{s}:{v}"
        
        # Add blank line when verse changes
        if current_verse is not None and current_verse != verse_key:
            output_lines.append(f"\n{s}:{v}")
        current_verse = verse_key
        
        # Get the clean word text
        raw_text = db[key]["text"]
        if isinstance(raw_text, list):
            raw_text = "".join(raw_text)
        clean_word = _strip_rule_tags(raw_text).strip()
        
        # Skip empty words or verse numbers
        if not clean_word or re.match(r'^[\u0660-\u0669]+$', clean_word):
            continue
            
        if phoneme_index < len(phoneme_arrays):
            phoneme_array = phoneme_arrays[phoneme_index]
            phoneme_str = "[" + ", ".join(f"'{p}'" for p in phoneme_array) + "]"
            aligned_line = align_at_column(clean_word, phoneme_str)
            output_lines.append(aligned_line)
            phoneme_index += 1
    
    # Save to file
    # Clean the reference for use as filename (replace problematic characters)
    safe_ref = re.sub(r'[<>:"/\\|?*]', '_', ref)
    output_file = Path(output_dir) / f"{safe_ref}.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Phonemized output saved to: {output_file}")

def compare_files(
    file1_path: str | Path,
    file2_path: str | Path,
    *,
    context_lines: int = 3,
    ignore_whitespace: bool = False,
    return_result: bool = False,
) -> bool | str:
    """
    Compare two text files and output differences if they're not identical.
    
    Parameters
    ----------
    file1_path : str | Path
        Path to the first file
    file2_path : str | Path  
        Path to the second file
    context_lines : int
        Number of context lines to show around differences (default: 3)
    ignore_whitespace : bool
        Whether to ignore whitespace differences (default: False)
    return_result : bool
        If True, return the diff as a string. If False, print it (default: False)
        
    Returns
    -------
    bool | str
        If return_result=False: Returns True if files are identical, False if different
        If return_result=True: Returns the diff string (empty if files are identical)
    """
    import difflib
    from pathlib import Path
    
    file1_path = Path(file1_path)
    file2_path = Path(file2_path)
    
    # Check if files exist
    if not file1_path.exists():
        error_msg = f"File not found: {file1_path}"
        if return_result:
            return error_msg
        print(error_msg)
        return False
        
    if not file2_path.exists():
        error_msg = f"File not found: {file2_path}"
        if return_result:
            return error_msg
        print(error_msg)
        return False
    
    try:
        # Read files
        with open(file1_path, 'r', encoding='utf-8') as f1:
            lines1 = f1.readlines()
        with open(file2_path, 'r', encoding='utf-8') as f2:
            lines2 = f2.readlines()
            
        # Optionally ignore whitespace
        if ignore_whitespace:
            lines1 = [line.strip() + '\n' for line in lines1]
            lines2 = [line.strip() + '\n' for line in lines2]
        
        # Compare files
        if lines1 == lines2:
            result_msg = f"Files are identical: {file1_path.name} and {file2_path.name}"
            if return_result:
                return ""  # Empty string indicates no differences
            print(result_msg)
            return True
        
        # Generate unified diff
        diff = difflib.unified_diff(
            lines1,
            lines2,
            fromfile=str(file1_path),
            tofile=str(file2_path),
            n=context_lines
        )
        
        diff_output = ''.join(diff)
        
        if return_result:
            return diff_output
        
        print(f"Files differ: {file1_path.name} vs {file2_path.name}")
        print("=" * 60)
        print(diff_output)
        return False
        
    except Exception as e:
        error_msg = f"Error comparing files: {e}"
        if return_result:
            return error_msg
        print(error_msg)
        return False
