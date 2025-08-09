import re
import argparse
from collections import defaultdict


def parse_definitions(file_path):
    word_dict = defaultdict(set)  # Changed to set for automatic deduplication
    current_word = None
    current_pos = None
    definition_lines = []
    capture_definitions = False

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            # Skip empty lines and section headers
            if not line or line.startswith("From ") or line.endswith("definition found"):
                continue

            # Skip the word list at the end
            if line.startswith('[') and line.endswith(']'):
                continue

            # Word line pattern: "jour /ʒuʀ/ <n, masc>"
            if re.match(r'^\w+(\s*/\S*/)?(\s*<[^>]+>)?$', line):
                if current_word and definition_lines:
                    definition_str = ' '.join(definition_lines)
                    # Store as tuple to prevent duplicate (pos, definition) pairs
                    word_dict[current_word].add((current_pos, definition_str))

                # Reset for new word
                parts = line.split()
                current_word = parts[0]  # Keep original case
                current_pos = None
                definition_lines = []

                # Extract part of speech if exists
                for part in parts[1:]:
                    if part.startswith('<') and part.endswith('>'):
                        current_pos = part[1:-1]
                capture_definitions = True
                continue

            # Definition lines
            if capture_definitions:
                definition_lines.append(line)

    # Add last word
    if current_word and definition_lines:
        definition_str = ' '.join(definition_lines)
        word_dict[current_word].add((current_pos, definition_str))

    return word_dict


def generate_anki_tsv(word_dict, output_path):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        # Write TSV header for Anki import
        outfile.write("front\tback\n")

        for word, definitions in word_dict.items():
            # Format back side with all definitions
            back_lines = []
            for pos, definition in definitions:
                if pos:
                    back_lines.append(f"({pos}) {definition}")
                else:
                    back_lines.append(definition)

            back_content = '<br>'.join(back_lines)
            outfile.write(f"{word}\t{back_content}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Anki TSV deck from definitions file.')
    parser.add_argument('-i', '--input', default='definitions_output.txt',
                        help='Input definitions file (default: definitions_output.txt)')
    parser.add_argument('-o', '--output', default='french_vocabulary_deck.tsv',
                        help='Output TSV file (default: french_vocabulary_deck.tsv)')

    args = parser.parse_args()

    word_definitions = parse_definitions(args.input)
    generate_anki_tsv(word_definitions, args.output)

    print(f"Anki deck generated: {args.output}")
    print(f"Total unique words: {len(word_definitions)}")
    total_definitions = sum(len(defs) for defs in word_definitions.values())
    print(f"Total unique definitions: {total_definitions}")