import argparse
from .extractor import extract_highlighted_words
from .translator_and_generator import translate_and_write_file
from os import path
import textwrap


def main():
    parser = argparse.ArgumentParser(
        prog="pdf2anki",
        description="Extract highlighted words from a PDF and convert them into an Anki-ready flashcard TXT file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              pdf2anki --pdf_file notes.pdf
              pdf2anki --pdf_file article.pdf --dest_lang es
              pdf2anki --pdf_file book.pdf --output my_flashcards.txt --dest_lang fr

            Language codes:
              Use standard Google Translate language codes (e.g., 'es' for Spanish, 'fr' for French, 'de' for German).
              If no language is specified, only definitions and synonyms are included.

            Output:
              If --output is not provided, the resulting TXT will be saved in the same folder as the input PDF,
              named '<pdf_filename>__FlashCards.txt'.""")
    )
    
    parser.add_argument( "--pdf_file", required=True,
        help="Path to the PDF file containing highlighted words."
    )
    parser.add_argument( "--dest_lang", required=False,
        help="Target language for translations (Google Translate language code, e.g., 'es' for Spanish, 'fr' for French). "
             "If omitted, only definitions and synonyms will be included."
    )
    parser.add_argument( "--output", required=False,
        help="Path to save the output TXT file. "
             "If not provided, the file will be created in the same folder as the PDF, "
             "named '<pdf_filename>__FlashCards.txt'."
    )
    args = parser.parse_args()
    
    pdf_file_path = args.pdf_file
    
    if args.output is None:
        root, extension = path.splitext( path.basename(pdf_file_path) )
        target_file_name = path.join( path.dirname(pdf_file_path) , root+'__FlashCards.txt' )
    else:
        target_file_name = args.output
    
    print("\n~ Extracting highlights...")
    highlighted_words = extract_highlighted_words(pdf_file_path)
    print(highlighted_words)
    
    if args.dest_lang is None:
        dest_lang = "en"
    else:
        dest_lang = args.dest_lang 

    print("~ Looking up definitions & Exporting FlashCards...")
    translate_and_write_file(highlighted_words, dest_lang=dest_lang, target_file_name=target_file_name )

    print("~ Done! TXT saved: ",target_file_name)
    

if __name__ == "__main__":
    main()