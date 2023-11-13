# flake8: noqa

import os
import pytest
from main import *
import pathlib, sys
import re

parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
sys.path.append(parent_dir)

os.environ["ENV"] = "test"

TEST_DIR = f"{os.getcwd()}/tests"

load_settings()

label_map_miz_controller = MizController()
label_map_miz_controller.exec_file(f"{TEST_DIR}/data/label_map.miz", f"{TEST_DIR}/data/mml.vct")
label_map_token_table = label_map_miz_controller.token_table
label_map_ast_root = label_map_miz_controller.ast_root


def test_cut_center_space_format_is_valid1():
    cut_center_space_value = 100
    assert (cut_center_space_format_is_valid(cut_center_space_value)) == False


def test_cut_center_space_format_is_valid2():
    cut_center_space_value = {":": True}
    assert (cut_center_space_format_is_valid(cut_center_space_value)) == False


def test_cut_center_space_format_is_valid3():
    cut_center_space_value = {": __label": 1}
    assert (cut_center_space_format_is_valid(cut_center_space_value)) == False


def test_cut_center_space_format_is_valid4():
    cut_center_space_value = {": __label": True}
    assert (cut_center_space_format_is_valid(cut_center_space_value)) == True


def test_generate_label_mapping():
    assert (
        generate_label_mapping(generate_token_blocks(label_map_ast_root, label_map_token_table))
    ) == {
        128: "A1",
        210: "A2",
        238: "A3",
        308: "A4",
        314: "A5",
        377: "A6",
        383: "A7",
        401: "A8",
        452: "A9",
        496: "A10",
        503: "A11",
        556: "A12",
        562: "A13",
        599: "A14",
        605: "A15",
        705: "A1",
        711: "A2",
        731: "A3",
        763: "A4",
    }


def test_set_formatted_text():
    os.environ["ENV"] = ""
    set_formatted_text(label_map_ast_root, label_map_token_table)
    assert [
        label_map_token_table.token(i).formatted_text
        for i in range(label_map_token_table.token_num)
        if (
            label_map_token_table.token(i).token_type == TokenType.IDENTIFIER
            and label_map_token_table.token(i).identifier_type == IdentifierType.LABEL
            and label_map_token_table.token(i).ref_token is None
            and not re.match(r"Def|Th", label_map_token_table.token(i).text)
        )
    ] == [
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
        "A7",
        "A8",
        "A9",
        "A10",
        "A11",
        "A12",
        "A13",
        "A14",
        "A15",
        "A1",
        "A2",
        "A3",
        "A4",
    ]
