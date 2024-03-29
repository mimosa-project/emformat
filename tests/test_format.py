# flake8: noqa

import os
import pytest
from main import load_settings, generate_token_blocks
from formatter.formatter import *
import pathlib, sys
import yaml
from py_miz_controller import MizController


parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
sys.path.append(parent_dir)

os.environ["ENV"] = "test"

TEST_DIR = f"{os.getcwd()}/tests"

load_settings()

miz_controller = MizController()
miz_controller.exec_file(f"{TEST_DIR}/data/jgraph_4.miz", f"{TEST_DIR}/data/mml.vct")

miz_controller2 = MizController()
miz_controller2.exec_file(f"{TEST_DIR}/data/tarski_0.miz", f"{TEST_DIR}/data/mml.vct")
miz_controller2.exec_file(f"{TEST_DIR}/data/tarski_0.miz", f"{TEST_DIR}/data/mml.vct")

blank_line_miz_controller = MizController()
blank_line_miz_controller.exec_file(f"{TEST_DIR}/data/blank_line.miz", f"{TEST_DIR}/data/mml.vct")
blank_line_token_table = blank_line_miz_controller.token_table

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

env_part_miz_controller = MizController()
env_part_miz_controller.exec_file(f"{TEST_DIR}/data/env_part.miz", f"{TEST_DIR}/data/mml.vct")
env_part_token_table = env_part_miz_controller.token_table

body_part_miz_controller = MizController()
body_part_miz_controller.exec_file(f"{TEST_DIR}/data/body_part.miz", f"{TEST_DIR}/data/mml.vct")
body_part_token_table = body_part_miz_controller.token_table

newline_miz_controller = MizController()
newline_miz_controller.exec_file(f"{TEST_DIR}/data/newline.miz", f"{TEST_DIR}/data/mml.vct")
newline_token_table = newline_miz_controller.token_table

real_1_miz_controller = MizController()
real_1_miz_controller.exec_file(f"{TEST_DIR}/data/real_1.miz", f"{TEST_DIR}/data/mml.vct")
real_1_token_table = real_1_miz_controller.token_table
real_1_ast_root = real_1_miz_controller.ast_root


def test_convert_to_token_representative_name1():
    token = token_table.token(329)
    assert (convert_to_token_representative_name(token)) == "__label"


def test_convert_to_token_representative_name2():
    token = token_table.token(330)
    assert (convert_to_token_representative_name(token)) == ":"


def test_separable_tokens_list():
    tokens = generate_token_lines(token_table)[45]
    assert (convert_token_lines_to_text_arrays(separable_tokens_list(miz_controller, tokens))) == [
        ["reserve"],
        ["p", ",", "q"],
        ["for"],
        ["Point"],
        ["of"],
        ["TOP-REAL", "2", ";"],
    ]


def test_generate_token_lines():
    assert ([token.text for token in generate_token_lines(token_table)[44]]) == [
        "reserve",
        "a",
        "for",
        "Real",
        ";",
    ]


def test_determine_space_omission1():
    assert (
        convert_token_lines_to_text_arrays(
            determine_space_omission(miz_controller, generate_token_lines(token_table)[596])
        )
    ) == [
        [":", "Def1", ":"],
    ]


def test_determine_space_omissio2():
    assert (
        convert_token_lines_to_text_arrays(
            determine_space_omission(miz_controller, generate_token_lines(token_table)[70])
        )
    ) == [
        ["r"],
        ["in"],
        ["REAL"],
        ["by"],
        ["XREAL_0", ":", "def"],
        ["1", ";"],
    ]


def test_generate_space_adjusted_line1():
    assert (
        convert_tokens_to_text(miz_controller, generate_token_lines(token_table)[384])
    ) == "then g5 . p = (r1 / r2 - a) / b by A11, A18;"


def test_generate_space_adjusted_line2():
    assert (
        convert_tokens_to_text(miz_controller, generate_token_lines(token_table)[64])
    ) == "{r where r is Real: r > a} c= the carrier of R^1"


def test_generate_space_adjusted_line3():
    assert (
        convert_tokens_to_text(miz_controller, generate_token_lines(token_table)[1700])
    ) == "defpred Q [Point of TOP-REAL 2] means $1 `1 <= 0;"


def test_generate_space_adjusted_line4():
    assert (
        convert_tokens_to_text(miz_controller, generate_token_lines(token_table)[596])
    ) == ":Def1:"


def test_generate_space_adjusted_line5():
    assert (
        convert_tokens_to_text(miz_controller, generate_token_lines(token_table)[174])
    ) == "A7: K = f .: K and"


def test_generate_space_adjusted_line6():
    assert (
        convert_tokens_to_text(miz_controller, generate_token_lines(token_table)[54])
    ) == "theorem Th1:"


def test_generate_space_adjusted_line7():
    assert (
        convert_tokens_to_text(miz_controller, generate_token_lines(token_table)[70])
    ) == "r in REAL by XREAL_0:def 1;"


# def test_generate_space_adjusted_line8():
#     assert (
#         convert_tokens_to_text(miz_controller2, generate_token_lines(token_table2)[47])
#     ) == "scheme Replacement {A() -> set, P[object, object]}:"


def test_split_into_env_and_body_part():
    input_lines = generate_token_lines(token_table)
    assert (len(split_into_env_and_body_part(input_lines)[0])) == 42


def test_token_texts():
    tokens = generate_token_lines(token_table)[44]
    assert (convert_tokens_to_text_array(tokens)) == ["reserve", "a", "for", "Real", ";"]


# Theoremブロック(Proof) を含む場合
def test_determine_body_part_indentation_widths1():
    assert (
        determine_body_part_indentation_widths(generate_token_lines(algspec1_token_table)[75:111])
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
def test_determine_body_part_indentation_widths2():
    assert (determine_body_part_indentation_widths(generate_token_lines(token_table2)[30:41])) == [
        0,
        2,
        2,
        2,
        0,
        0,
        0,
        2,
        2,
        2,
        2,
    ]


# Schemeブロックを含む場合
def test_determine_body_part_indentation_widths3():
    assert (
        determine_body_part_indentation_widths(generate_token_lines(algstr_4_token_table)[135:161])
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


def test_determine_body_part_indentation_widths4(caplog):
    input = generate_token_lines(token_table)[48:58]
    input.pop(4)
    try:
        determine_body_part_indentation_widths(input)
    except SystemExit as e:
        assert e.code == 1
        assert "Expected 'end'" in caplog.text


def test_determine_body_part_indentation_widths5(caplog):
    try:
        determine_body_part_indentation_widths(generate_token_lines(token_table)[50:54])
    except SystemExit as e:
        assert e.code == 1
        assert "There are 'end' without a corresponding keyword" in caplog.text


def test_split_env_part_tokens_into_sentences():
    result = convert_token_lines_to_text_arrays(
        split_env_part_token_lines_into_sentences(generate_token_lines(env_part_token_table))
    )
    expected = []
    with open(f"{TEST_DIR}/expected/env_part.yml") as f:
        expected = yaml.safe_load(f)
    assert (result) == expected


def test_remove_consecutive_value():
    array = ["aaa", "aaa", "bbb", "ccc", "ccc"]
    assert (remove_consecutive_value(array, "aaa")) == ["aaa", "bbb", "ccc", "ccc"]


def test_count_comment_lines_before1():
    assert (count_comment_lines_before(generate_token_lines(token_table2), 13)) == 13


def test_count_comment_lines_before2():
    assert (count_comment_lines_before(generate_token_lines(token_table2), 14)) == 0


def test_count_comment_lines_before3():
    assert (count_comment_lines_before(generate_token_lines(token_table2), 22)) == 1


def test_find_first_no_empty_array_i():
    array = [[], [], [], [1]]
    assert (find_first_no_empty_array_i(array)) == 3


def test_normalize_blank_line():
    with open(f"{TEST_DIR}/expected/blank_line.miz") as f:
        expected = f.read().split("\n")
    result = convert_token_lines_to_texts(
        blank_line_miz_controller,
        normalize_blank_line(generate_token_lines(blank_line_token_table)),
    )
    assert result == expected


def test_split_line_at_max_length():
    line = "  for Y being set st Y c= field R & Y <> {} ex a being object st a in Y & for b being object st b in Y & a <> b holds not [a,b] in R; let A be non empty Subset of T;"
    indentation_width = 4
    assert (split_line_at_max_length(line, indentation_width)) == [
        "  for Y being set st Y c= field R & Y <> {} ex a being object st a in Y & for b",
        "    being object st b in Y & a <> b holds not [a,b] in R; let A be non empty",
        "    Subset of T;",
    ]


def test_format_env_part():
    assert (
        format_env_part(env_part_miz_controller, generate_token_lines(env_part_token_table))
    ) == [
        ":: Fan Homeomorphisms in the Plane",
        "::  by Yatsuka Nakamura",
        "",
        "environ",
        "",
        " vocabularies NUMBERS, PRE_TOPC, FUNCT_4, SUPINF_2, COMPLEX1, XXREAL_0,",
        "      ORDINAL2, XBOOLE_0, FUNCT_1, TOPMETR, SUBSET_1, ORDINAL2, RCOMP_1,",
        "      RCOMP_2;",
        " notations TARSKI, XBOOLE_0, SUBSET_1, ORDINAL1, NUMBERS, XCMPLX_0, XREAL_0,",
        "      STRUCT_0, PARTFUN1, TOPMETR, RLVECT_1, EUCLID, FUNCT_4, PRE_TOPC,",
        "      RLTOPSP1;",
        " constructors FUNCT_4, REAL_1, SQUARE_1, BINOP_2, COMPLEX1, TOPS_2, COMPTS_1,",
        "      TBSP_1, TOPMETR, PSCOMP_1, FUNCSDOM, PCOMPS_1;",
    ]


def test_format_body_part():
    assert (
        format_body_part(body_part_miz_controller, generate_token_lines(body_part_token_table))
    ) == [
        "begin :: Semilattice of type widening Semilattice of type widening Semilattice of type widening",
        "",
        "definition",
        "  for x, y being Element of Class R, v, w being Element of M st x = Class (R,",
        "  v) & y = Class (R, w) holds it . (x, y) = Class (R, v * w) if M is non empty",
        "  otherwise it = {};",
        "  correctness",
        "  proof",
        "    A1: M is not empty implies ex b being BinOp of Class R st for x, y being",
        "    Element of Class R, v, w being Element of M st x = Class (R, v) & y = Class",
        "    (R, w) holds b . (x, y) = Class (R, v * w)",
        "  end;",
        "end;",
        "",
        "registration",
        "  coherence",
        "  proof",
        "    let Y be set;",
        "  end;",
        "end;",
    ]


def test_adjust_newline_position():
    assert (
        convert_token_lines_to_text_arrays(
            adjust_newline_position(generate_token_lines(newline_token_table))
        )
    ) == [
        ["environ", ":: comment"],
        ["constructors", "NUMBERS", ";"],
        ["registrations", "XBOOLE_0", ";"],
        ["begin"],
        ["definition"],
        ["aaa", ";"],
        ["bbb", ":", "Def4", ":", "ccc", ";"],
        ["end", ";"],
        ["theorem"],
        ["ddd"],
        ["proof"],
        ["A1", ":"],
        ["now"],
        ["eee", ";"],
        ["end", ";"],
        ["end", ";"],
        ["theorem", "Th1", ":"],
        ["fff", ";"],
        ["scheme", "ddd", "{", "P", "[", "set", "]", "}", ":"],
        ["end", ";"],
        ["definition"],
        ["let", "n"],
        ["be", "Nat", ";"],
        ["end", ";"],
    ]


def test_generate_token_blocks():
    result = generate_token_blocks(real_1_ast_root, real_1_token_table)
    assert ([token_blocks[0].line_number for token_blocks in result]) == [31, 37, 46, 56, 64, 82]

    assert (convert_tokens_to_text_array(result[0])) == [
        "registration",
        "cluster",
        "->",
        "real",
        "for",
        "Element",
        "of",
        "REAL",
        ";",
        "coherence",
        ";",
        "end",
    ]
