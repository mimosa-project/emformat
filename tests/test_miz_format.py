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


def test_tokens_by_line():
    assert ([token.text for token in tokens_by_line(token_table)[44]]) == [
        "reserve",
        "a",
        "for",
        "Real",
        ";",
    ]


def test_space_adjusted_lines_1():
    assert (
        space_adjusted_lines(token_table)[384]
    ) == "then g5 . p = (r1 / r2 - a) / b by A11, A18;"


def test_space_adjusted_lines_2():
    assert (
        space_adjusted_lines(token_table)[64]
    ) == "{r where r is Real : r > a} c= the carrier of R^1"


def test_space_adjusted_lines_3():
    assert (
        space_adjusted_lines(token_table)[1700]
    ) == "defpred Q [Point of TOP-REAL 2] means $1 `1 <= 0;"


def test_space_adjusted_lines_4():
    assert (space_adjusted_lines(token_table)[596]) == ":Def1:"


def test_space_adjusted_lines_5():
    assert (space_adjusted_lines(token_table)[174]) == "A7: K = f .: K and"


def test_space_adjusted_lines_6():
    assert (space_adjusted_lines(token_table)[54]) == "theorem Th1:"


# def test_space_adjusted_lines_7():
#     assert (space_adjusted_lines(token_table)[70]) == "r in REAL by XREAL_0: def 1;"

def test_space_adjusted_lines_7():
    assert (space_adjusted_lines(token_table2)[47]) == "scheme Replacement {A() -> set, P[object, object] }:"