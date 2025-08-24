# highlighted-pdf-to-anki-flashcards

Extract highlighted words from PDFs and turn them into Anki flashcards (TXT).

## Features
- Extracts highlighted text from PDF files.
- Fetches definitions (and optional translations).
- Exports results to a TXT file ready for import into Anki.

## Installation
```bash
pip install highlighted-pdf-to-anki-flashcards
```

```bash
pdf2anki --pdf_file my_notes.pdf
```

```bash
pdf2anki --pdf_file my_notes.pdf --dest_lang es
```

```bash
pdf2anki --pdf_file my_notes.pdf --output vocab.csv
```