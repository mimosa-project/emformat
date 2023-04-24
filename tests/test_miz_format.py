# flake8: noqa

import os
import pytest
from src.miz_format import *
import pathlib, sys
import re
import yaml

parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
sys.path.append(parent_dir)

TEST_DIR = f"{os.getcwd()}/tests"

miz_controller = MizController()
miz_controller.exec_file(f"{TEST_DIR}/data/jgraph_4.miz", f"{TEST_DIR}/data/mml.vct")

miz_controller2 = MizController()
miz_controller2.exec_file(f"{TEST_DIR}/data/tarski_0.miz", f"{TEST_DIR}/data/mml.vct")

load_settings()
token_table = miz_controller.token_table
token_table2 = miz_controller2.token_table

abcmiz_0_miz_controller = MizController()
abcmiz_0_miz_controller.exec_file(f"{TEST_DIR}/data/abcmiz_0.miz", f"{TEST_DIR}/data/mml.vct")
token_table3 = abcmiz_0_miz_controller.token_table

algstr_4_miz_controller = MizController()
algstr_4_miz_controller.exec_file(f"{TEST_DIR}/data/algstr_4.miz", f"{TEST_DIR}/data/mml.vct")
algstr_4_token_table = algstr_4_miz_controller.token_table

algspec1_miz_controller = MizController()
algspec1_miz_controller.exec_file(f"{TEST_DIR}/data/algspec1.miz", f"{TEST_DIR}/data/mml.vct")
algspec1_token_table = algspec1_miz_controller.token_table

environ_part_miz_controller = MizController()
environ_part_miz_controller.exec_file(
    f"{TEST_DIR}/data/environ_part.miz", f"{TEST_DIR}/data/mml.vct"
)
environ_part_token_table = environ_part_miz_controller.token_table


def test_cut_center_space_format_is_valid1():
    cut_center_space_value = 100
    assert (cut_center_space_format_is_valid(cut_center_space_value)) == False


def test_cut_center_space_format_is_valid2():
    cut_center_space_value = {":": True}
    assert (cut_center_space_format_is_valid(cut_center_space_value)) == False


def test_cut_center_space_format_is_valid3():
    cut_center_space_value = {": __label": True}
    assert (cut_center_space_format_is_valid(cut_center_space_value)) == True


def test_convert_to_token_representative_name1():
    token = token_table.token(329)
    assert (convert_to_token_representative_name(token)) == "__label"


def test_convert_to_token_representative_name2():
    token = token_table.token(330)
    assert (convert_to_token_representative_name(token)) == ":"


def test_tokens_by_line():
    assert ([token.text for token in tokens_by_line(token_table)[44]]) == [
        "reserve",
        "a",
        "for",
        "Real",
        ";",
    ]


def test_determine_space_omission1():
    assert (determine_space_omission(tokens_by_line(token_table)[596])) == [
        [":", "Def1", ":"],
    ]


def test_determine_space_omissio2():
    assert (determine_space_omission(tokens_by_line(token_table)[70])) == [
        ["r"],
        ["in"],
        ["REAL"],
        ["by"],
        ["XREAL_0", ":", "def"],
        ["1", ";"],
    ]


def test_space_adjusted_line1():
    assert (
        space_adjusted_line(tokens_by_line(token_table)[384])
    ) == "then g5 . p = (r1 / r2 - a) / b by A11, A18;"


def test_space_adjusted_line2():
    assert (
        space_adjusted_line(tokens_by_line(token_table)[64])
    ) == "{r where r is Real: r > a} c= the carrier of R^1"


def test_space_adjusted_line3():
    assert (
        space_adjusted_line(tokens_by_line(token_table)[1700])
    ) == "defpred Q [Point of TOP-REAL 2] means $1 `1 <= 0;"


def test_space_adjusted_line4():
    assert (space_adjusted_line(tokens_by_line(token_table)[596])) == ":Def1:"


def test_space_adjusted_line5():
    assert (space_adjusted_line(tokens_by_line(token_table)[174])) == "A7: K = f .: K and"


def test_space_adjusted_line6():
    assert (space_adjusted_line(tokens_by_line(token_table)[54])) == "theorem Th1:"


def test_space_adjusted_line7():
    assert (space_adjusted_line(tokens_by_line(token_table)[70])) == "r in REAL by XREAL_0:def 1;"


# def test_space_adjusted_line8():
#     assert (
#         space_adjusted_line(tokens_by_line(token_table2)[47])
#     ) == "scheme Replacement {A() -> set, P[object, object]}:"


def test_split_into_environ_and_body_part():
    input_lines = tokens_by_line(token_table)
    assert (len(split_into_environ_and_body_part(input_lines)[0])) == 42


def test_token_texts():
    tokens = tokens_by_line(token_table)[44]
    assert (token_texts(tokens)) == ["reserve", "a", "for", "Real", ";"]


# Theoremブロック(Proof) を含む場合
def test_determine_body_part_indentation_numbers1():
    assert (
        determine_body_part_indentation_numbers(tokens_by_line(algspec1_token_table)[75:111])
    ) == [
        0,
        2,
        2,
        0,
        2,
        2,
        2,
        2,
        2,
        2,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        2,
        2,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        4,
        2,
        2,
        0,
    ]


# Theoremブロック(Simple-Justification)を含む場合
def test_determine_body_part_indentation_numbers2():
    assert (determine_body_part_indentation_numbers(tokens_by_line(token_table2)[30:35])) == [
        0,
        2,
        2,
        2,
        0,
    ]


# Schemeブロックを含む場合
def test_determine_body_part_indentation_numbers3():
    assert (
        determine_body_part_indentation_numbers(tokens_by_line(algstr_4_token_table)[135:161])
    ) == [
        0,
        2,
        2,
        2,
        0,
        2,
        2,
        0,
        2,
        2,
        2,
        2,
        2,
        4,
        4,
        4,
        2,
        2,
        2,
        4,
        4,
        4,
        2,
        2,
        2,
        0,
    ]


def test_determine_body_part_indentation_numbers4(caplog):
    input = tokens_by_line(token_table)[48:58]
    input.pop(4)
    try:
        determine_body_part_indentation_numbers(input)
    except SystemExit as e:
        assert e.code == 1
        assert "Expected 'end'" in caplog.text


def test_determine_body_part_indentation_numbers5(caplog):
    try:
        determine_body_part_indentation_numbers(tokens_by_line(token_table)[50:54])
    except SystemExit as e:
        assert e.code == 1
        assert "There are 'end' without a corresponding keyword" in caplog.text


def test_split_environ_part_tokens_into_sentences():
    tokens = list(itertools.chain.from_iterable(tokens_by_line(environ_part_token_table)))
    result = convert_tokens_by_line_to_token_texts(split_environ_part_tokens_into_sentences(tokens))
    expected = []
    with open(f"{TEST_DIR}/expected/environ_part.yml") as f:
        expected = yaml.safe_load(f)
    assert (result) == expected


def test_determine_directive_line_breaks_and_indentation_numbers():
    tokens = list(itertools.chain.from_iterable(tokens_by_line(environ_part_token_table)[5:7]))
    (
        directive_tokens_by_line,
        directive_indentation_numbers,
    ) = determine_directive_line_breaks_and_indentation_numbers(tokens)

    assert (directive_indentation_numbers) == [1, 6, 6]
    assert ([token_texts(tokens) for tokens in directive_tokens_by_line]) == [
        [
            "vocabularies",
            "NUMBERS",
            ",",
            "PRE_TOPC",
            ",",
            "FUNCT_4",
            ",",
            "SUPINF_2",
            ",",
            "COMPLEX1",
            ",",
            "XXREAL_0",
            ",",
        ],
        [
            "ORDINAL2",
            ",",
            "XBOOLE_0",
            ",",
            "FUNCT_1",
            ",",
            "TOPMETR",
            ",",
            "SUBSET_1",
            ",",
            "ORDINAL2",
            ",",
            "RCOMP_1",
            ",",
        ],
        [
            "RCOMP_2",
            ";",
        ],
    ]


def test_determine_environ_part_line_breaks_and_indentation_numbers1():
    result = []
    for tokens in determine_environ_part_line_breaks_and_indentation_numbers(
        tokens_by_line(environ_part_token_table)
    )[0]:
        result.append([token.text for token in tokens])

    expected = []
    with open(f"{TEST_DIR}/expected/environ_part.txt") as f:
        for line in f:
            print(line)
            expected.append(line.strip().split("|") if line != "\n" else [])

    assert (result) == expected


def test_determine_environ_part_line_breaks_and_indentation_numbers2():
    assert (
        determine_environ_part_line_breaks_and_indentation_numbers(tokens_by_line(environ_part_token_table))[1]
    ) == [0, 0, 0, 0, 0, 1, 6, 6, 1, 6, 6, 1, 6, 0]
