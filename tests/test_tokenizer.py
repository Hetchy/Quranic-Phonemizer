import sys
import types
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Stub out yaml dependency if not installed
if 'yaml' not in sys.modules:
    sys.modules['yaml'] = types.SimpleNamespace(safe_load=lambda *a, **k: {})

from core.tokenizer import Tokenizer


def test_tokenize_basic():
    t = Tokenizer()
    tokens = t.tokenize('1:1')
    assert tokens, 'No tokens returned'
    assert tokens[0].is_start
    assert tokens[-1].is_end
