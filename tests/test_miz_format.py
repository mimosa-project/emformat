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

load_settings()
token_table = miz_controller.token_table
token_table2 = miz_controller2.token_table


def test_has_composite_key1():
    setting_value = 100
    assert (has_composite_key(setting_value)) == False


def test_has_composite_key2():
    setting_value = {":": True}
    assert (has_composite_key(setting_value)) == False


def test_has_composite_key3():
    setting_value = {": __label": True}
    assert (has_composite_key(setting_value)) == True


def test_token_formatted_to_setting_value1():
    token = token_table.token(329)
    assert (token_formatted_to_setting_value(token)) == "__label"


def test_token_formatted_to_setting_value2():
    token = token_table.token(330)
    assert (token_formatted_to_setting_value(token)) == ":"


def test_tokens_by_line():
    assert ([token.text for token in tokens_by_line(token_table)[44]]) == [
        "reserve",
        "a",
        "for",
        "Real",
        ";",
    ]


def test_require_to_omit_left_space():
    assert (require_to_omit_left_space(tokens_by_line(token_table)[44])) == [
        True,
        False,
        False,
        False,
        True,
    ]


# def test_can_omit_left_space():
#     assert (can_omit_left_space(tokens_by_line(token_table)[44])) == [
#         True,
#         False,
#         False,
#         False,
#         True,
#     ]


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
