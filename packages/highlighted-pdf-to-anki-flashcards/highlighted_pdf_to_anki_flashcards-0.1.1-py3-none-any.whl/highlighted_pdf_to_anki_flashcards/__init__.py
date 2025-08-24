"""
Highlighted PDF to Anki FlashCards

Extract highlighted words from PDFs, look up definitions, and generate
Anki-ready flashcard TXTs.
"""

__version__ = "0.1.1"

from .extractor import extract_highlighted_words
from .translator_and_generator import translate_and_write_file

__all__ = ["extract_highlighted_words", "translate_and_write_file"]
