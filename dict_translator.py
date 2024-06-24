import subprocess
import sys
word_array = []
each_word = []


def open_text(text_title):
    with open(text_title, 'r') as text_to_open:
        for line_inside in text_to_open:
            word_array.append(line_inside)


def array_subdvision(word_array):
    log_from_translation = []
    for phrase in word_array:
        each_word.append(phrase.split())
    for i in each_word:
        for j in i:
            translator_word = str(j).lower()
            command_for_proc = ['dict', '-d', sys.argv[1], translator_word]
            try:
                proc = subprocess.call(command_for_proc)
            except subprocess.CalledProcessError:
                print('')
            else:
                log_from_translation.append(proc)


open_text("enter_your_text_here.txt")
array_subdvision(word_array)
