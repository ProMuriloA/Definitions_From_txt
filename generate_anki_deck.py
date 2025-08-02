import re
from collections import defaultdict

def parse_definitions(file_path):
    word_dict = defaultdict(list)
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
                    word_dict[current_word].append((current_pos, ' '.join(definition_lines)))
                
                # Reset for new word
                parts = line.split()
                current_word = parts[0].lower()
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
        word_dict[current_word].append((current_pos, ' '.join(definition_lines)))
    
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
    input_file = "definitions_output.txt"
    output_file = "french_vocabulary_deck.tsv"
    
    word_definitions = parse_definitions(input_file)
    generate_anki_tsv(word_definitions, output_file)
    
    print(f"Anki deck generated: {output_file}")
    print(f"Total words: {len(word_definitions)}")
