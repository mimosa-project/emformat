from collections import Counter
import re


def has_same_number_of_chars(file_name1, file_name2):
    input_lines1 = ""
    input_lines2 = ""

    with open(file_name1, "r", encoding="utf-8") as f:
        input_lines1 = f.read()
    with open(file_name2, "r", encoding="utf-8") as f:
        input_lines2 = f.read()

    counter1 = Counter(input_lines1)
    counter2 = Counter(input_lines2)

    diff = diff_chars_count(counter1, counter2)

    return diff == {}


def diff_chars_count(dict1, dict2):
    chars = {
        char
        for char in set(list(dict1.keys()) + list(dict2.keys()))
        if re.match(r"\S", char)
    }
    diff = {}
    for char in chars:
        count = dict1[char] - dict2[char]
        if count != 0:
            diff[char] = count
    return diff
