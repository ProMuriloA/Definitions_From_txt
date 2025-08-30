import re
import os
import sys

def parse_definitions_file(content):
    sections = re.split(r'---\s+([A-Z\s]+)\s+---', content)[1:]
    flashcards = {}
    
    for i in range(0, len(sections), 2):
        word = sections[i].strip()
        definition_block = sections[i+1] if i+1 < len(sections) else ''
        
        # Skip if we've already processed this word
        if word in flashcards:
            continue
            
        # Split into individual definitions
        definitions = re.split(r'From\s+[^:]+:\s*', definition_block)
        definitions = [d.strip() for d in definitions if d.strip()]
        
        # Combine all definitions into one
        full_definition = " | ".join(definitions)
        
        # Clean up the definition text
        full_definition = re.sub(r'\s+', ' ', full_definition)
        full_definition = full_definition.replace('\t', ' ').replace('\n', ' ')
        
        flashcards[word] = full_definition
    
    return [(word, definition) for word, definition in flashcards.items()]

def main():
    # Check if file path was provided as argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = input("Please enter the path to your definitions file: ")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    
    # Remove file metadata headers
    content = re.sub(r'\[file name\]:.*?\n', '', content)
    content = re.sub(r'\[file content begin\].*?\n', '', content)
    content = re.sub(r'\[file content end\].*', '', content)
    
    flashcards = parse_definitions_file(content)
    
    # Write to TSV file
    output_path = os.path.join(os.path.dirname(file_path), 'flashcards.tsv')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('Front\tBack\n')
        for word, definition in flashcards:
            # Escape tabs and newlines in the definition
            definition = definition.replace('\t', ' ').replace('\n', ' ')
            f.write(f'{word}\t{definition}\n')
    
    print(f"Successfully created {len(flashcards)} flashcards in {output_path}")

if __name__ == '__main__':
    main()