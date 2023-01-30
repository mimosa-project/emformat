import sys
import os
import yaml
import re
import utils.const as const

from py_miz_controller import (
    MizController,
    TokenType,
    ElementType,
    StatementType,
    BlockType,
    SymbolType,
    SpecialSymbolType,
    IdentifierType,
    CommentType,
    KeywordType,
)


def main(argv):
    _, miz_path, vct_path = argv
    miz_controller = MizController()
    miz_controller.exec_file(miz_path, vct_path)
    token_table = miz_controller.token_table
    ast_root = miz_controller.ast_root

    input_lines = []
    with open(miz_path, "r", encoding="utf-8") as f:
        input_lines = f.read().split("\n")

    load_settings()
    format(input_lines, token_table, ast_root)


def load_settings():
    with open("{}/settings.yml".format(os.path.dirname(__file__)), "r") as yml:
        settings = yaml.safe_load(yml)
        for k, v in settings.items():
            setattr(const, k, v)


def format(input_lines, token_table, ast_root):
    pass


def output(output_lines):
    # with open(miz_path, "w") as f:
    with open("data/result.miz", "w") as f:
        f.writelines(output_lines)


if __name__ == "__main__":
    main(sys.argv)
