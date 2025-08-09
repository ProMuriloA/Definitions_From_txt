import sys
import csv


def filter_tsv_by_front(base_file, input_file, output_file):
    # Increase field size limit to handle large fields
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int //= 2
            if max_int < 1024:
                print("Error: Couldn't set field size limit to a workable value")
                sys.exit(1)

    # Function to find front column index
    def find_front_index(header):
        for i, col in enumerate(header):
            if col.lower() == "front":
                return i
        return None

    # Process base file to get front values
    reference_values = set()
    try:
        with open(base_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)  # Read header
            front_index = find_front_index(header)

            if front_index is None:
                print(f"Error: 'Front' column not found in {base_file}")
                sys.exit(1)

            for row in reader:
                if len(row) > front_index:
                    reference_values.add(row[front_index])

        print(f"Loaded {len(reference_values)} front values from {base_file}")
    except Exception as e:
        print(f"Error processing base file: {str(e)}")
        sys.exit(1)

    # Process input file
    removed_count = 0
    total_count = 0
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
                open(output_file, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')

            # Process input header
            input_header = next(reader)
            front_index_input = find_front_index(input_header)

            if front_index_input is None:
                print(f"Error: 'Front' column not found in {input_file}")
                sys.exit(1)

            writer.writerow(input_header)

            # Process rows
            for row in reader:
                total_count += 1
                if len(row) <= front_index_input:
                    # Skip rows that don't have a front value
                    continue

                front_value = row[front_index_input]
                if front_value in reference_values:
                    removed_count += 1
                    continue

                writer.writerow(row)

        print(f"Processed {total_count} rows from {input_file}")
        print(f"Removed {removed_count} rows with matching Front values")
        print(f"Saved {total_count - removed_count} rows to {output_file}")

    except Exception as e:
        print(f"Error processing input file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python filter_tsv.py <base_file.tsv> <input_file.tsv> <output_file.tsv>")
        print("Purpose: Remove rows from input_file where 'Front' column matches any in base_file")
        sys.exit(1)

    _, base_file, input_file, output_file = sys.argv
    filter_tsv_by_front(base_file, input_file, output_file)