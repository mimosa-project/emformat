# flake8: noqa

import os
import pytest
from main import load_settings
from linter.linter import *
import pathlib, sys
import yaml
import utils.option as option
from py_miz_controller import MizController


parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
sys.path.append(parent_dir)

os.environ["ENV"] = "test"

TEST_DIR = f"{os.getcwd()}/tests"

lp_miz_controller = MizController()
lp_miz_controller.exec_file(
    f"{TEST_DIR}/data/long_proof.miz", f"{TEST_DIR}/data/mml.vct"
)
lp_ast_root = lp_miz_controller.ast_root


def test_check_long_proof1(caplog):
    setattr(option, "MAX_PROOF_LINE_NUMBER", 32)
    check_long_proof(lp_ast_root)
    assert "Proof too long" in caplog.text


def test_check_long_proof2(caplog):
    setattr(option, "MAX_PROOF_LINE_NUMBER", 33)
    check_long_proof(lp_ast_root)
    assert not "Proof too long" in caplog.text


rl_miz_controller = MizController()
rl_miz_controller.exec_file(
    f"{TEST_DIR}/data/redundant_label.miz", f"{TEST_DIR}/data/mml.vct"
)
rl_ast_root = rl_miz_controller.ast_root
rl_token_table = rl_miz_controller.token_table


def test_check_redundant_statement_label(caplog):
    token_lines = generate_token_lines(rl_token_table)
    check_redundant_statement_label(rl_ast_root, token_lines)
    assert caplog.text.count("is redundant citation label") == 3
