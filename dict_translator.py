import subprocess
import sys
import os
from collections import OrderedDict

def get_unique_words(filename):
    """Extract unique lowercase words from a file while preserving order."""
    unique_words = OrderedDict()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                for word in line.split():
                    unique_words[word.lower()] = True
        return list(unique_words.keys())
    except FileNotFoundError:
        print(f"\nError: File '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError reading file: {e}")
        sys.exit(1)

def show_translation_options():
    """Display available translation options from file."""
    try:
        with open('translation_opt.txt', 'r', encoding='utf-8') as f:
            print("\nAvailable translation options:")
            print(f.read().strip())
    except FileNotFoundError:
        print("\nError: 'translation_opt.txt' not found.")
        print("Please create this file with available language options.")
        sys.exit(1)

def lookup_definitions(lang_code, words):
    """Look up definitions using dict command and return results."""
    definitions = []
    errors = []

    print(f"\nProcessing {len(words)} unique words...")
    for i, word in enumerate(words, 1):
        try:
            result = subprocess.run(
                ['dict', '-d', lang_code, word],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            definitions.append(f"\n--- {word.upper()} ---\n{result.stdout.strip()}\n")
        except subprocess.CalledProcessError as e:
            errors.append(f"\n--- {word.upper()} ---\nError: {e.stderr.strip()}\n")
        except Exception as e:
            errors.append(f"\n--- {word.upper()} ---\nSystem error: {str(e)}\n")

        # Show progress
        if i % 5 == 0 or i == len(words):
            print(f"Processed {i}/{len(words)} words", end='\r')

    return definitions, errors

def save_results(definitions, errors):
    """Save results to output files and return success status."""
    try:
        with open('definitions_output.txt', 'w', encoding='utf-8') as def_file:
            def_file.writelines(definitions)

        with open('errors_output.txt', 'w', encoding='utf-8') as err_file:
            err_file.writelines(errors)

        return True
    except Exception as e:
        print(f"\nError saving results: {e}")
        return False

def main():
    print("\n" + "="*50)
    print("DICTIONARY TRANSLATOR".center(50))
    print("="*50)

    # Show available translation options
    show_translation_options()

    # Get user input with validation
    lang_code = input("\nEnter language code: ").strip()
    if not lang_code:
        print("Error: Language code cannot be empty")
        sys.exit(1)

    # Process words
    input_file = 'enter_your_text_here.txt'
    words = get_unique_words(input_file)

    if not words:
        print(f"\nNo words found in '{input_file}'")
        sys.exit(0)

    definitions, errors = lookup_definitions(lang_code, words)

    # Save and display results
    if save_results(definitions, errors):
        print("\n\nResults saved to:")
        print(f"- definitions_output.txt ({(len(definitions))} words)")
        print(f"- errors_output.txt ({(len(errors))} words)")

        # Show sample output
        sample_size = min(3, len(definitions))
        print(f"\nSample definitions (first {sample_size}):")
        print(''.join(definitions[:sample_size]))
    else:
        print("Failed to save results")

if __name__ == "__main__":
    main()