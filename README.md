# Definitions_From_txt

### All software inside this repository is under the GNU GPL V.3 License.

### This is a software for finding a lot of word definitions all at once
This is a linux terminal tool for automating word definition searchs. It uses gcide and it is adapted to search between many languages. In order to use it you must enter the text inside the enter_your_text_here.txt and run the ./dict_translator.sh. The whole process is shown below:

This Software works this way:

1. Copy and paste your text inside the enter_your_text_here.txt and save the file. Then you can close it.
2. Open the terminal in the folder and run: **chmod +x ./dict_translator** in the terminal
2. Open the terminal and execute the bash archive dict_translator. Run **./dict_translator.sh** in the terminal.
3. Now the software has been opened. Then choose a database based on the corresponding languages.
4. Now your definitions are available on the terminal and on the file **definitions_output.txt**.
5. Any errors while trying to find the definitions are in **errors_output.txt**.
6. Generate an Anki deck by running:

	python3 generate_anki_deck.py definitions_output.txt
7. [optional] You can transform a .apkg or .colpkg file into tsv with the anki_to_tsv.py file; Usage: python anki_to_tsv.py <input.apkg> [output.tsv]
8. [optional] You can select only the words that are not in two files so you can make a different file with the tsv_compare.py file; Usage: python3 tsv_compare.py <base_file.tsv> <input_file.tsv> <output_file.tsv>
9. [optional] You can use public domain texts/books in txt and merge them witht the ./Livros/combine.py file. In this example I used the Public Domain works of Charles Dickens available in the Project Gutenberg website. 