import subprocess
import sys

word_array = []
each_word = []

def get_unique_elements(input_list):
    return list(set(input_list))


def open_text(text_title):
    with open(text_title, 'r') as text_to_open:
        for line_inside in text_to_open:
            word_array.append(line_inside)


def array_subdvision(word_array):
    log_from_translation = []
    for phrase in word_array:
        each_word.append(phrase.split())

    new_each_word = []
    for i in each_word:
        for j in i:
            new_each_word.append(str(j).lower())
            new_each_word = get_unique_elements(new_each_word)
    print(new_each_word)

    for new_j in new_each_word:
        translator_word = str(new_j).lower()
        command_for_proc = ['dict', '-d', sys.argv[1], translator_word]
        try:
            proc = subprocess.call(command_for_proc)
        except subprocess.CalledProcessError:
            print('')
        else:
            log_from_translation.append(proc)


open_text("enter_your_text_here.txt")
array_subdvision(word_array)
