import pytest
from src.whisper_eval_serbian.utils import normalize_text_serbian, clean_texts, to_latin_serbian

# -----------------------------
# Tests for normalize_text_serbian
# -----------------------------
@pytest.mark.parametrize("input_text, expected", [
    # Lowercasing
    ("Dobar DAN", "dobar dan"),

    # Remove punctuation (replace with space)
    ("Zdravo, svete!", "zdravo svete"),
    ("Ovo-je.test?", "ovo je test"),

    # Serbian letters preserved
    ("ČĆŠĐŽ Ljubav", "čćšđž ljubav"),

    # Numbers kept
    ("Imam 123 jabuke", "imam 123 jabuke"),

    # Multiple spaces collapsed
    ("Ovo    je   test", "ovo je test"),

    # Newlines/tabs removed
    ("Ovo\nje\ttest", "ovo je test"),

    # Leading/trailing spaces stripped
    ("   višak prostora   ", "višak prostora"),

    # Combination case
    ("   Čao,\nsvete!   ", "čao svete"),

    # Only punctuation
    ("   ,.!?\n\t  ", ""),

    # Already normalized
    ("ovo je test", "ovo je test"),

    # Empty string
    ("", ""),
])
def test_normalize_text_serbian(input_text, expected):
    assert normalize_text_serbian(input_text) == expected

# -----------------------------
# Tests for clean_texts
# -----------------------------
def test_clean_texts_basic():
    predictions = ["Hello\nWorld", "  Test\tText "]
    references = ["Ref\nOne", "  Ref Two "]
    clean_preds, clean_refs = clean_texts(predictions, references)
    assert clean_preds == ["Hello World", "Test Text"]
    assert clean_refs == ["Ref One", "Ref Two"]

def test_clean_texts_empty_lists():
    clean_preds, clean_refs = clean_texts([], [])
    assert clean_preds == []
    assert clean_refs == []

def test_clean_texts_only_newlines():
    preds = ["\n\n", "\t"]
    refs = ["\n", "\t"]
    clean_preds, clean_refs = clean_texts(preds, refs)
    assert clean_preds == ["", ""]
    assert clean_refs == ["", ""]

# -----------------------------
# Tests for to_latin_serbian
# -----------------------------
@pytest.mark.parametrize("input_text, expected", [
    ("Ћао свет", "Ćao svet"),
    ("Шта радиш?", "Šta radiš?"),
    ("Ђорђе и Жељко", "Đorđe i Željko"),
    ("Normal Latin text", "Normal Latin text"),
    ("123 бројке", "123 brojke"),
])
def test_to_latin_serbian(input_text, expected):
    assert to_latin_serbian(input_text) == expected
