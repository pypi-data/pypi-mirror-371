# Apache License

# Copyright 2025 Text Intellect Team

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
import cyrtranslit
from typing import List, Tuple


def to_latin_serbian(text: str) -> str:
    """
    Transliterates Serbian Cyrillic text to Latin script.
    Leaves Latin letters and numbers intact.
    """
    return cyrtranslit.to_latin(text, "sr")


def normalize_text_serbian(text: str) -> str:
    """
    Applies orthographic normalization for Serbian text.
    - Lowercases
    - Removes punctuation (keeps Serbian letters and numbers)
    - Removes newlines/tabs
    - Collapses multiple spaces into one
    - Strips leading/trailing spaces
    """
    text = text.lower().strip()
    # Remove any character that's not a letter, number, or whitespace
    text = re.sub(r"[^\w\sабвгдђежзијклљмнњопрстћуфхцчџш]", " ", text)
    # Replace newlines and tabs with a space
    text = re.sub(r"[\n\r\t]+", " ", text)
    # Collapse multiple spaces into a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_texts(predictions: List[str], references: List[str]) -> Tuple[List[str], List[str]]:
    """
    Cleans predictions and references for evaluation.
    - Replaces newlines/tabs with spaces
    - Strips leading/trailing spaces
    """
    clean_preds = [p.replace("\n", " ").replace("\t", " ").strip() for p in predictions]
    clean_refs = [r.replace("\n", " ").replace("\t", " ").strip() for r in references]
    return clean_preds, clean_refs
