import os
import pytest
from src.miz_format import *
import pathlib, sys

parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
sys.path.append(parent_dir)

TEST_DIR = f"{os.getcwd()}/tests"

miz_controller = MizController()
miz_controller.exec_file("data/jgraph_4.miz", "data/mml.vct")

miz_controller2 = MizController()
miz_controller2.exec_file("data/tarski_0.miz", "data/mml.vct")

blank_line_miz_controller = MizController()
blank_line_miz_controller.exec_file(f"{TEST_DIR}/data/blank_line.miz", "data/mml.vct")
blank_line_token_table = blank_line_miz_controller.token_table

load_settings()
token_table = miz_controller.token_table
token_table2 = miz_controller2.token_table


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


def test_omit_continuous_values():
    array = ["aaa", "aaa", "bbb", "ccc", "ccc"]
    assert (omit_continuous_values(array, "aaa")) == ["aaa", "bbb", "ccc", "ccc"]


def test_count_before_comment_line_number1():
    assert (count_before_comment_line_number(tokens_by_line(token_table2), 13)) == 13


def test_count_before_comment_line_number2():
    assert (count_before_comment_line_number(tokens_by_line(token_table2), 14)) == 0


def test_count_before_comment_line_number3():
    assert (count_before_comment_line_number(tokens_by_line(token_table2), 22)) == 1

def test_find_first_no_empty_array_i():
    array = [[], [], [], [1]]
    assert(find_first_no_empty_array_i(array)) == 3


def test_adjust_blank_line():
    with open(f"{TEST_DIR}/expected/blank_line.miz") as f:
        expected = f.read().split("\n")
    result = space_adjusted_lines(adjust_blank_line(tokens_by_line(blank_line_token_table)))
    assert result == expected
