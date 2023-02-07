import os
import pytest
from src.miz_format import *
import pathlib, sys

parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
sys.path.append(parent_dir)

TEST_DIR = f"{os.getcwd()}/tests"

miz_controller = MizController()
miz_controller.exec_file("data/jgraph_4.miz", "data/mml.vct")
load_settings()


@pytest.fixture
def token_table():
    return miz_controller.token_table


def test_tokens_by_line(token_table):
    assert ([token.text for token in tokens_by_line(token_table)[44]]) == [
        "reserve",
        "a",
        "for",
        "Real",
        ";",
    ]


def test_space_adjusted_lines_1(token_table):
    assert (
        space_adjusted_lines(token_table)[111]
    ) == "A2 : B = {p where p is Point of X : g /. p < a};"


def test_space_adjusted_lines_2(token_table):
    assert (
        space_adjusted_lines(token_table)[384]
    ) == "then g5 . p = (r1 / r2 - a) / b by A11, A18;"
