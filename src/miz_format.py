import sys
import os
import json
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
    with open("{}/settings.json".format(os.path.dirname(__file__)), "r") as f:
        settings = json.load(f)
        for k, v in settings.items():
            setattr(const, k, v)


def format(input_lines, token_table, ast_root):
    output(space_adjusted_lines(token_table))


def output(output_lines):
    # with open(miz_path, "w") as f:
    with open("data/result.miz", "w") as f:
        f.writelines([f"{line}\n" for line in output_lines])


def space_adjusted_lines(token_table):
    output_lines = []

    for tokens in tokens_by_line(token_table):
        output_line = ""
        has_before_space = True
        for token in tokens:
            token_type = token.token_type

            if token_type != TokenType.SYMBOL:
                output_line += f" {token.text}" if has_before_space else token.text
                has_before_space = True
            else:
                match token.special_symbol_type:
                    case SpecialSymbolType.COMMA | SpecialSymbolType.SEMICOLON:
                        output_line += token.text
                        has_before_space = True
                    case SpecialSymbolType.LEFT_PARENTHESIS | SpecialSymbolType.LEFT_BRACKET | SpecialSymbolType.LEFT_BRACE:
                        output_line += f" {token.text}"
                        has_before_space = False
                    case SpecialSymbolType.RIGHT_PARENTHESIS | SpecialSymbolType.RIGHT_BRACKET | SpecialSymbolType.RIGHT_BRACE:
                        output_line += token.text
                        has_before_space = True
                    case _:
                        output_line += (
                            f" {token.text}" if has_before_space else token.text
                        )
                        has_before_space = True

        output_lines.append(output_line.strip())

    return output_lines


def tokens_by_line(token_table):
    last_line_number = token_table.last_token.line_number
    tokens_by_line = [[] for _ in range(last_line_number)]

    for i in range(token_table.token_num):
        token = token_table.token(i)
        line_number = token.line_number
        tokens_by_line[line_number - 1].append(token)

    return tokens_by_line


if __name__ == "__main__":
    main(sys.argv)
