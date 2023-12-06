import sys
import os
import json
import utils.option as option
import logging
from typing import Any
import re
from formatter.formatter import format
from linter.linter import lint


from py_miz_controller import (
    MizController,
    TokenType,
    IdentifierType,
    ASTToken,
    ASTBlock,
    ASTStatement,
    StatementType,
    BlockType,
)

def main(argv):
    os.environ["ENV"] = ""
    _, mode, miz_path, vct_path, user_settings = argv
    user_settings = json.loads(user_settings)
    miz_controller = MizController()
    miz_controller.exec_file(miz_path, vct_path)
    token_table = miz_controller.token_table
    ast_root = miz_controller.ast_root

    override_settings(user_settings)
    load_settings()
    set_formatted_text(ast_root, token_table)

    match mode:
      case "-f" | "--format":
        formatted_lines = format(miz_controller, token_table)
        output(miz_path, formatted_lines)
      case "-l" | "--lint":
        lint(miz_controller)
      case _:
        pass


# ユーザーが指定した項目値を設定
def override_settings(user_settings: dict):
    for setting_key, setting_value in user_settings.items():
        # バリデーションチェック
        if setting_key == "CUT_CENTER_SPACE":
            if cut_center_space_format_is_valid(setting_value):
                # 複合キーの型変換
                setting_value = {tuple(k.split()): v for k, v in setting_value.items()}
            else:
                continue
        elif setting_key in [
            "MAX_LINE_LENGTH",
            "STANDARD_INDENTATION_WIDTH",
            "ENVIRON_DIRECTIVE_INDENTATION_WIDTH",
            "ENVIRON_LINE_INDENTATION_WIDTH",
            "MAX_PROOF_LINE_NUMBER",
        ]:
            if re.fullmatch(r"\d+", setting_value):
                setting_value = int(setting_value)
            else:
                continue
        elif setting_key in ["CUT_LEFT_SPACE", "CUT_RIGHT_SPACE"]:
            if type(setting_value) != list:
                continue
        else:
            continue

        setattr(option, setting_key, setting_value)


# デフォルトの項目値を設定
def load_settings():
    with open("{}/default_settings.json".format(os.path.dirname(__file__)), "r") as f:
        settings = json.load(f)
        for setting_key, setting_value in settings.items():
            # CUT_CENTER_SPACE の場合、型チェックを行う
            if setting_key == "CUT_CENTER_SPACE":
                if not cut_center_space_format_is_valid(setting_value):
                    logging.error("CUT_CENTER_SPACE value in setting file is invalid.")
                    sys.exit(1)

                # 複合キーの型変換
                setting_value = {tuple(k.split()): v for k, v in setting_value.items()}

            if not hasattr(option, setting_key):
                setattr(option, setting_key, setting_value)


def set_formatted_text(ast_root, token_table):
    label_mapping = generate_label_mapping(generate_token_blocks(ast_root, token_table))
    for i in range(token_table.token_num):
        token = token_table.token(i)
        token_id = token.ref_token.id if token.ref_token else token.id
        if (
            token.token_type == TokenType.IDENTIFIER
            and token.identifier_type == IdentifierType.LABEL
            and token_id in label_mapping.keys()
        ):
            token.set_formatted_text(label_mapping[token_id])
        else:
            token.set_formatted_text(token.text)


def output(miz_path, output_lines):
    with open(miz_path, "w") as f:
        f.writelines([f"{line}\n" for line in output_lines])


def cut_center_space_format_is_valid(cut_center_space_value: Any) -> bool:
    if not (isinstance(cut_center_space_value, dict)):
        return False

    for key, value in cut_center_space_value.items():
        if len(key.split()) != 2:
            return False
        if type(value) != bool:
            return False

    return True

# チェック対象のラベルに対して、{トークンID: ラベル名} のリストを返す
def generate_label_mapping(token_blocks) -> dict[int, str]:
    label_mapping = {}
    for token_block in token_blocks:
        # label_var_counts = {ラベル変数名: カウント, ...}
        # "A1"の"A"をラベル変数名とする
        label_var_counts: dict[str, int] = {}
        for i in range(len(token_block)):
            token = token_block[i]
            if (
                token.token_type == TokenType.IDENTIFIER
                and token.identifier_type == IdentifierType.LABEL
                and token_block[i - 1].text != ":"  # :Def: を除外
                and token.ref_token is None
            ):
                label_var = (
                    re.match(r"^(.*?)\d+$", token.text).group(1)
                    if re.search(r"\d+$", token.text)
                    else token.text
                )
                # 初めて登場するラベル変数名の場合、カウントを初期化
                if label_var not in label_var_counts.keys():
                    label_var_counts[label_var] = 1

                label_mapping[token.id] = f"{label_var}{label_var_counts[label_var]}"
                label_var_counts[label_var] += 1

    return label_mapping


def generate_token_blocks(ast_root, token_table) -> list[list[ASTToken]]:
    block_ranges = generate_block_ranges(ast_root)

    if len(block_ranges) == 0:
        return []

    first_token_id, last_token_id = block_ranges.pop(0)

    token_blocks = []
    token_block = []
    is_in_block = False

    for i in range(token_table.token_num):
        token = token_table.token(i)

        if token.id == first_token_id:
            is_in_block = True

        if is_in_block:
            token_block.append(token)

        if token.id == last_token_id:
            is_in_block = False
            token_blocks.append(token_block)
            token_block = []

            if len(block_ranges) == 0:
                return token_blocks
            first_token_id, last_token_id = block_ranges.pop(0)


def generate_block_ranges(ast_root) -> list[list[int]]:
    block_ranges: list[list[int]] = []
    for i in range(ast_root.child_component_num):
        ast_component = ast_root.child_component(i)

        if type(ast_component) == ASTBlock:
            if (
                i != 0
                and type(ast_root.child_component(i).block_type == BlockType.PROOF)
                and type(ast_root.child_component(i - 1)) == ASTStatement
                and ast_root.child_component(i - 1).statement_type == StatementType.SCHEME
            ):
                # Schemeブロック内でproofブロックが出現する場合、
                # Schemeブロック先頭からproofブロック末尾までをまとめて一つのブロックとみなす
                block_ranges[-1][1] = ast_component.last_token.id
            else:
                block_ranges.append([ast_component.first_token.id, ast_component.last_token.id])
        elif ast_component.statement_type == StatementType.SCHEME:
            block_ranges.append(
                [ast_component.range_first_token.id, ast_component.range_last_token.id]
            )

    return block_ranges


if __name__ == "__main__":
    main(sys.argv)
