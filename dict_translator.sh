#!/bin/bash
echo 'Choose Your Language'
echo 'Type the language you want to translate from'
echo 'Options:'
cat translation_opt.txt
echo 'Choose an option below:'
read -r option_chosen
python3 dict_translator.py "$option_chosen" 1>definitions_output.txt 2>errors_output.txt
echo 'Your archive is saved in definitions_output.txt in the same folder'
echo 'Here is the result:'
cat definitions_output.txt
