import sys
import os
import json
import re
import utils.option as option

from py_miz_controller import (
    MizController,
    ASTToken,
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
        for setting_key, setting_value in settings.items():
            # 設定ファイルでは複合キーを文字列で表現しているため、タプルに変換する
            if has_composite_key(setting_value):
                setting_value = {tuple(k.split()): v for k, v in setting_value.items()}
            setattr(option, setting_key, setting_value)


def format(input_lines, token_table, ast_root):
    output(space_adjusted_lines(tokens_by_line(token_table)))


def output(output_lines):
    # with open(miz_path, "w") as f:
    with open("data/result.miz", "w") as f:
        f.writelines([f"{line}\n" for line in output_lines])


# 設定値が複合キーを持つかどうかを判定
def has_composite_key(setting_value):
    if not (isinstance(setting_value, dict)):
        return False
    for k, v in setting_value.items():
        if len(k.split()) > 1:
            return True
    return False


# TODO: 名前どうにかする
# TokenTypeが Identifier の場合、__[identifier_type] の形に変換する
# Symbol の場合はそのままのテキスト
def token_formatted_to_setting_value(token):
    if token.token_type == TokenType.IDENTIFIER:
        identifier_type = str(token.identifier_type)
        return f"__{identifier_type[identifier_type.index('.')+1:].lower()}"
    else:
        return token.text


def tokens_by_line(token_table):
    last_line_number = token_table.last_token.line_number
    tokens_by_line = [[] for _ in range(last_line_number)]

    for i in range(token_table.token_num):
        token = token_table.token(i)
        line_number = token.line_number
        tokens_by_line[line_number - 1].append(token)

    return tokens_by_line


# 実際にはmizcore側に実装
def is_separable_tokens(tokens):
    return True


def needs_omit_left_space(tokens):
    omit_left_space = [False for _ in range(len(tokens))]

    for current_pos in range(len(tokens)):
        if current_pos == 0:
            omit_left_space[current_pos] = True
            continue

        token_str = token_formatted_to_setting_value(tokens[current_pos])
        left_token_str = token_formatted_to_setting_value(tokens[current_pos - 1])

        if (left_token_str, token_str) in option.CUT_CENTER_SPACE:
            omit_left_space[current_pos] = option.CUT_CENTER_SPACE[(left_token_str, token_str)]
        else:
            if token_str in option.CUT_LEFT_SPACE:
                omit_left_space[current_pos] = True
            if left_token_str in option.CUT_RIGHT_SPACE:
                omit_left_space[current_pos] = True

    return omit_left_space


def can_omit_left_space(tokens):
    omit_left_space = [False for _ in range(len(tokens))]

    begin_pos = 0
    for current_pos in range(len(tokens)):
        if current_pos == 0:
            omit_left_space[current_pos] = True
            continue

        end_pos = current_pos + 1

        is_separable = is_separable_tokens(tokens[begin_pos:end_pos])
        omit_left_space[current_pos] = is_separable

        if not (is_separable):
            begin_pos = current_pos

    # return omit_left_space
    return [True for _ in range(len(tokens))]


def space_adjusted_line(tokens):
    output_line = ""
    omit_left_space = [
        i & j for i, j in zip(needs_omit_left_space(tokens), can_omit_left_space(tokens))
    ]
    for pos in range(len(tokens)):
        output_line += f"{'' if omit_left_space[pos] else ' '}{tokens[pos].text}"

    return output_line


def space_adjusted_lines(tokens_by_line):
    output_lines = []

    for tokens in tokens_by_line:
        output_lines.append(space_adjusted_line(tokens))
    return output_lines


if __name__ == "__main__":
    main(sys.argv)
