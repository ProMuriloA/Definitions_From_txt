import os
import argparse

def combine_txt_files(input_folder, output_file, include_headers=False):
    """
    Combines all .txt files from a folder into a single output file.
    
    Args:
        input_folder (str): Path to folder containing .txt files
        output_file (str): Path for output combined file
        include_headers (bool): Whether to include filename headers
    """
    # Validate input folder
    if not os.path.isdir(input_folder):
        raise NotADirectoryError(f"Input folder not found: {input_folder}")
    
    # Get absolute paths for comparison
    output_abs = os.path.abspath(output_file)
    txt_files = []
    
    # Collect and filter text files
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            file_path = os.path.join(input_folder, filename)
            file_abs = os.path.abspath(file_path)
            
            # Skip if this is the output file
            if file_abs == output_abs:
                continue
                
            txt_files.append(filename)
    
    # Sort files alphabetically
    txt_files.sort()
    
    if not txt_files:
        print("No .txt files found in the input folder")
        return

    # Process files
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for i, filename in enumerate(txt_files):
            file_path = os.path.join(input_folder, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
            except Exception as e:
                print(f"  Skipping {filename}: {str(e)}")
                continue
            
            # Add header if requested
            if include_headers:
                if i > 0:  # Add separator between files
                    outfile.write('\n\n')
                outfile.write(f'--- {filename} ---\n\n')
            
            outfile.write(content)
    
    print(f"Combined {len(txt_files)} file(s) into {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Combine TXT files into a single output file.')
    parser.add_argument('input_folder', help='Folder containing TXT files')
    parser.add_argument('output_file', help='Output combined TXT file')
    parser.add_argument('--headers', action='store_true', help='Include filename headers in output')
    
    args = parser.parse_args()
    
    try:
        combine_txt_files(
            input_folder=args.input_folder,
            output_file=args.output_file,
            include_headers=args.headers
        )
    except Exception as e:
        print(f"Error: {str(e)}")
