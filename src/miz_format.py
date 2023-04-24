import sys
import os
import json
import utils.option as option
import logging
import itertools


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


def convert_tokens_by_line_to_token_texts(tokens_by_line):
    texts = []
    for tokens in tokens_by_line:
        texts.append(token_texts(tokens))

    return texts


def determine_indentation_numbers(tokens_by_line) -> list[int]:
    # 環境部と本体部で分けて処理する
    environ_part_tokens_by_line, body_part_tokens_by_line = split_into_environ_and_body_part(
        tokens_by_line
    )

    (
        environ_part_indentation_numbers,
        environ_part_tokens_by_line,
    ) = determine_environ_part_line_breaks_and_indentation_numbers(environ_part_tokens_by_line)

    body_part_indentation_numbers = determine_body_part_indentation_numbers(
        body_part_tokens_by_line
    )

    output_tokens_by_line = environ_part_tokens_by_line + body_part_tokens_by_line
    indentation_numbers = environ_part_indentation_numbers + body_part_indentation_numbers

    return indentation_numbers, output_tokens_by_line


def determine_environ_part_line_breaks_and_indentation_numbers(environ_part_tokens_by_line):
    tokens = list(itertools.chain.from_iterable(environ_part_tokens_by_line))
    tokens_by_sentence = split_environ_part_tokens_into_sentences(tokens)
    output_indentation_numbers = []
    output_tokens_by_line = []

    for tokens in tokens_by_sentence:
        if len(tokens) == 0:
            output_indentation_numbers.append(0)
            output_tokens_by_line.append([])
            continue
        # 目標となるキーワードは必ず行頭に出現することを前提としている
        elif tokens[0].text == "environ" or tokens[0].token_type == TokenType.COMMENT:
            output_indentation_numbers.append(0)
            output_tokens_by_line.append([tokens[0]])
            continue

        (
            tokens_by_line,
            indentation_numbers,
        ) = determine_directive_line_breaks_and_indentation_numbers(tokens)
        output_tokens_by_line.extend(tokens_by_line)
        output_indentation_numbers.extend(indentation_numbers)

    output_tokens_by_line.append([])
    output_indentation_numbers.append(0)
    return output_tokens_by_line, output_indentation_numbers


# Input: 1行分のDirectiveのトークン列
# Output: 最大文字数を超えないよう分割した行単位のトークン列、各行のインデント数の配列
def determine_directive_line_breaks_and_indentation_numbers(
    directive_tokens,
) -> tuple[list[list], list]:
    tokens_by_line = []
    indentation_numbers = []
    current_line_length = option.ENVIRON_TOP_INDENTATION_SPACE_NUMBER
    current_line_tokens = []
    carryover_tokens = []
    # 区切り位置を決定
    for token in directive_tokens:
        current_line_length += len(token.text)

        if current_line_length > option.MAX_LINE_LENGTH:
            # 次の行が[,|;]から開始しないようにする
            if token.text in [",", ";"]:
                carryover_tokens.append(current_line_tokens.pop())
            carryover_tokens.append(token)

            # 現在の行を確定
            tokens_by_line.append(current_line_tokens)

            # 初期化
            current_line_length = option.ENVIRON_IN_LINE_INDENTATION_SPACE_NUMBER + sum(
                [len(token.text) for token in carryover_tokens]
            )
            current_line_tokens = carryover_tokens
            carryover_tokens = []
        else:
            current_line_tokens.append(token)

        # トークン間のスペース数を加算
        if token.text == "," or token.text in option.ENVIRON_TAGS:
            current_line_length += 1

    tokens_by_line.append(current_line_tokens)

    # インデント数の決定
    for i in range(len(tokens_by_line)):
        if i == 0:
            indentation_numbers.append(option.ENVIRON_TOP_INDENTATION_SPACE_NUMBER)
        else:
            indentation_numbers.append(option.ENVIRON_IN_LINE_INDENTATION_SPACE_NUMBER)

    return tokens_by_line, indentation_numbers


def split_environ_part_tokens_into_sentences(tokens) -> list[list]:
    output_tokens_by_sentence = []
    current_sentence_tokens = []

    for token in tokens:
        if token.text == "environ":
            output_tokens_by_sentence.extend([[], [token], []])
        elif token.token_type == TokenType.COMMENT:
            output_tokens_by_sentence.append([token])
        else:
            current_sentence_tokens.append(token)
            if token.text == ";":
                output_tokens_by_sentence.append(current_sentence_tokens)
                current_sentence_tokens = []

    if output_tokens_by_sentence[0] == []:
        output_tokens_by_sentence.pop(0)

    return output_tokens_by_sentence


def determine_body_part_indentation_numbers(body_part_tokens_by_line):
    indentation_numbers = []
    current_indentation_step = 0
    current_block_level = 0
    # Theorem, Scheme ブロック内でのみ利用
    current_block_type = ""
    proof_found = False

    # インデントの決定の目標となるキーワードは、必ず行頭に出現することを前提としている
    # adjust_line_break 内で実装
    for tokens in body_part_tokens_by_line:
        if tokens == []:
            indentation_numbers.append(0)
            continue

        first_token_text = tokens[0].text

        # ブロックの開始/終了の整合性をチェックする
        if first_token_text in option.TOP_OF_BLOCK_TAGS and current_block_level > 0:
            logging.error("Expected 'end'")
            sys.exit(1)
        elif first_token_text == "end" and current_block_level == 0:
            logging.error("There are 'end' without a corresponding keyword")
            sys.exit(1)

        # インデント数の決定と、インデント段階の変更
        if first_token_text in option.USE_INDENT_TAGS:
            if current_block_type == "theorem" and first_token_text == "proof":
                if not proof_found:
                    current_indentation_step -= 1
                    proof_found = True
                indentation_numbers.append(
                    current_indentation_step * option.SPACE_NUMBER_PER_INDENTATION
                )
                current_block_level += 1
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
                current_block_level += 1
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

        # Theoremブロックの開始/終了判定
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

        # Schemeブロックの開始/終了判定
        if first_token_text == "scheme":
            current_block_type = "scheme"
            proof_found = False
            current_block_level = 1
        elif current_block_type == "scheme":
            if first_token_text == "end" and current_block_level == 0:
                current_block_type = ""
                current_block_level = 0

    return indentation_numbers


# TODO: 改行を調整する処理
# 適切に改行が挿入された状態での token_by_lines を返す
def adjust_line_break(token_by_lines):
    pass


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


def normalize_blank_line(tokens_by_line):
    output_tokens_by_line = []

    # 空行の挿入
    for current_line, tokens in enumerate(tokens_by_line):
        if tokens == []:
            output_tokens_by_line.append(tokens)
            continue

        first_token_text = tokens[0].text
        before_comment_line_number = count_comment_lines_before(tokens_by_line, current_line)
        add_blank_line_number = (
            -1 * before_comment_line_number
            if before_comment_line_number
            else len(output_tokens_by_line)
        )
        if first_token_text in option.USE_BEFORE_BLANK_LINE:
            output_tokens_by_line.insert(add_blank_line_number, [])
        output_tokens_by_line.append(tokens)
        if first_token_text in option.USE_AFTER_BLANK_LINE:
            output_tokens_by_line.append([])

    first_no_empty_array_i = find_first_no_empty_array_i(output_tokens_by_line)

    return remove_consecutive_value(output_tokens_by_line[first_no_empty_array_i:], value=[])


def count_comment_lines_before(tokens_by_line, target_line):
    comment_line_number = 0
    for line in reversed(range(target_line)):
        if tokens_by_line[line] == []:
            return comment_line_number

        first_token_type = tokens_by_line[line][0].token_type
        if first_token_type != TokenType.COMMENT:
            return comment_line_number

        comment_line_number += 1

    return comment_line_number


def remove_consecutive_value(array, value):
    output = [array[0]]
    output.extend([j for i, j in zip(array, array[1:]) if j != value or i != j])
    return output


def find_first_no_empty_array_i(array):
    for i, elm in enumerate(array):
        if elm != []:
            return i


if __name__ == "__main__":
    main(sys.argv)
