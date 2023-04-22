import sys
import os
import json
import utils.option as option

from py_miz_controller import (
    MizController,
    TokenType,
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
            # CUT_CENTER_SPACE の場合、型チェックを行う
            if setting_key == "CUT_CENTER_SPACE":
                if not cut_center_space_format_is_valid(setting_value):
                    print("設定ファイルのCUT_CENTER_SPACEの値が不適切です。")
                    sys.exit(1)

                # 複合キーの型変換
                setting_value = {tuple(k.split()): v for k, v in setting_value.items()}

            setattr(option, setting_key, setting_value)


def format(input_lines, token_table, ast_root):
    output(space_adjusted_lines(tokens_by_line(token_table)))


def output(output_lines):
    # with open(miz_path, "w") as f:
    with open("data/result.miz", "w") as f:
        f.writelines([f"{line}\n" for line in output_lines])


def cut_center_space_format_is_valid(cut_center_space_value):
    if not (isinstance(cut_center_space_value, dict)):
        return False

    for key in cut_center_space_value:
        if len(key.split()) != 2:
            return False

    return True


# token.identifier_type = IdentifierType.LABEL の場合、"__label" を返す
def convert_to_token_representative_name(token):
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


def determine_space_omission(tokens):
    no_space_tokens_list = []
    no_space_tokens = []

    for current_pos in range(len(tokens)):
        token_text = tokens[current_pos].text

        if current_pos == 0:
            no_space_tokens.append(token_text)
            if len(tokens) == 1:
                no_space_tokens_list.append(no_space_tokens)
            continue

        representative_name = convert_to_token_representative_name(tokens[current_pos])
        left_representative_name = convert_to_token_representative_name(tokens[current_pos - 1])

        if option.CUT_CENTER_SPACE.get((left_representative_name, representative_name)):
            no_space_tokens.append(token_text)
        elif (
            representative_name in option.CUT_LEFT_SPACE
            or left_representative_name in option.CUT_RIGHT_SPACE
        ):
            no_space_tokens.append(token_text)
        else:
            no_space_tokens_list.extend(separable_tokens_list(no_space_tokens))
            no_space_tokens = [token_text]

        if current_pos == len(tokens) - 1:
            no_space_tokens_list.extend(separable_tokens_list(no_space_tokens))

    return no_space_tokens_list


def separable_tokens_list(tokens):
    separable_tokens_list = []
    begin_pos = 0
    end_pos = len(tokens)

    while True:
        if is_separable_tokens(tokens[begin_pos:end_pos]):
            separable_tokens_list.append(tokens[begin_pos:end_pos])
            if end_pos == len(tokens):
                break

            begin_pos = end_pos
            end_pos = len(tokens)
        else:
            end_pos -= 1

    return separable_tokens_list


def space_adjusted_line(tokens):
    output_line = ""
    no_space_tokens_list = determine_space_omission(tokens)

    for tokens in no_space_tokens_list:
        output_line += f" {''.join(tokens)}"

    return output_line.lstrip()


def space_adjusted_lines(tokens_by_line):
    output_lines = []

    for tokens in tokens_by_line:
        output_lines.append(space_adjusted_line(tokens))
    return output_lines


def token_texts(tokens):
    if tokens == []:
        return []
    return [token.text for token in tokens]


def determine_indentation_numbers(tokens_by_line) -> list[int]:
    # 環境部と本体部で分けて処理する
    environ_part_tokens_by_line, body_part_tokens_by_line = split_into_environ_and_body_part(
        tokens_by_line
    )
    return determine_environ_part_indentation_numbers(
        environ_part_tokens_by_line
    ) + determine_body_part_indentation_numbers(body_part_tokens_by_line)


def determine_environ_part_indentation_numbers(environ_part_tokens_by_line):
    indentation_numbers = []

    for tokens in environ_part_tokens_by_line:
        if tokens == []:
            indentation_numbers.append(0)
            continue

        first_token = tokens[0]
        first_token_text = first_token.text

        if first_token_text in option.ENVIRON_TAGS:
            indentation_numbers.append(option.ENVIRON_TOP_INDENTATION_SPACE_NUMBER)
        elif first_token.token_type == TokenType.IDENTIFIER:
            indentation_numbers.append(option.ENVIRON_IN_LINE_INDENTATION_SPACE_NUMBER)
        else:
            indentation_numbers.append(0)

    return indentation_numbers


def determine_body_part_indentation_numbers(body_part_tokens_by_line):
    indentation_numbers = []
    current_indentation_step = 0
    current_block_level = 0
    # Theorem, Scheme ブロック内でのみ利用
    current_block_type = ""
    proof_found = False

    for tokens in body_part_tokens_by_line:
        if tokens == []:
            indentation_numbers.append(0)
            continue

        first_token_text = tokens[0].text

        # インデント数の決定と、インデント段階の変更
        if first_token_text in option.USE_INDENT_TAGS:
            if current_block_type == "theorem" and first_token_text == "proof":
                if not proof_found:
                    current_indentation_step -= 1
                    proof_found = True
                current_block_level += 1
                indentation_numbers.append(
                    current_indentation_step * option.SPACE_NUMBER_PER_INDENTATION
                )
                current_indentation_step += 1
            elif current_block_type == "scheme" and first_token_text == "proof":
                if not proof_found:
                    current_indentation_step -= 1
                    proof_found = True
                else:
                    current_block_level += 1
                indentation_numbers.append(
                    current_indentation_step * option.SPACE_NUMBER_PER_INDENTATION
                )
                current_indentation_step += 1
            else:
                indentation_numbers.append(
                    current_indentation_step * option.SPACE_NUMBER_PER_INDENTATION
                )
                current_indentation_step += 1
        elif first_token_text == "provided":
            current_indentation_step -= 1
            indentation_numbers.append(
                current_indentation_step * option.SPACE_NUMBER_PER_INDENTATION
            )
            current_indentation_step += 1
        elif first_token_text == "end":
            current_block_level -= 1
            current_indentation_step -= 1
            indentation_numbers.append(
                current_indentation_step * option.SPACE_NUMBER_PER_INDENTATION
            )
        else:
            indentation_numbers.append(
                current_indentation_step * option.SPACE_NUMBER_PER_INDENTATION
            )

        # "theorem" タグは "end" と対にならないため、ブロック内にいるどうか判定が必要
        # Theorem ブロック終了条件
        #   - Proof の場合                : Proof ブロックが終了する
        #   - Simple-Justification の場合 : ";" が出現する
        if first_token_text == "theorem":
            current_block_type = "theorem"
            proof_found = False
            current_block_level = 1
        elif current_block_type == "theorem":
            if (first_token_text == "end" and current_block_level == 1) or (
                not proof_found and ";" in token_texts(tokens)
            ):
                current_block_type = ""
                current_block_level = 0

        # Schemeブロック内で最初に出現する "proof" は "end" と対にならないため、ブロック内にいるどうか判定が必要
        if first_token_text == "scheme":
            current_block_type = "scheme"
            proof_found = False
            current_block_level = 1
        elif current_block_type == "scheme":
            if first_token_text == "end" and current_block_level == 0:
                current_block_type = ""
                current_block_level = 0

    return indentation_numbers


def split_into_environ_and_body_part(tokens_by_line):
    for current_line_number, tokens in enumerate(tokens_by_line):
        if tokens == []:
            continue

        init_token = tokens[0]
        if (
            init_token.token_type == TokenType.KEYWORD
            and init_token.keyword_type == KeywordType.BEGIN_
        ):
            return tokens_by_line[:current_line_number], tokens_by_line[current_line_number:]


if __name__ == "__main__":
    main(sys.argv)
