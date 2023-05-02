import sys
import os
import json
import utils.option as option
import logging
import itertools


from py_miz_controller import MizController, TokenType, KeywordType, IdentifierType


def main(argv):
    _, miz_path, vct_path = argv
    miz_controller = MizController()
    miz_controller.exec_file(miz_path, vct_path)
    token_table = miz_controller.token_table

    load_settings()
    formatted_lines = format(token_table)
    output(formatted_lines)


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


def generate_token_lines(token_table):
    last_line_number = token_table.last_token.line_number
    token_lines = [[] for _ in range(last_line_number)]

    for i in range(token_table.token_num):
        token = token_table.token(i)
        line_number = token.line_number
        token_lines[line_number - 1].append(token)

    return token_lines


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


def generate_space_adjusted_line(tokens):
    output_line = ""
    no_space_tokens_list = determine_space_omission(tokens)

    for tokens in no_space_tokens_list:
        output_line += f" {''.join(tokens)}"

    return output_line.lstrip()


def generate_space_adjusted_lines(token_lines):
    output_lines = []

    for tokens in token_lines:
        output_lines.append(generate_space_adjusted_line(tokens))
    return output_lines


def convert_tokens_to_texts(tokens):
    if tokens == []:
        return []
    return [token.text for token in tokens]


def convert_token_lines_to_texts(token_lines):
    texts = []
    for tokens in token_lines:
        texts.append(convert_tokens_to_texts(tokens))

    return texts


def format(token_table):
    token_lines = generate_token_lines(token_table)
    env_part_token_lines, body_part_token_lines = split_into_env_and_body_part(token_lines)
    env_part_lines = format_env_part(env_part_token_lines)
    body_part_lines = format_body_part(body_part_token_lines)
    return env_part_lines + body_part_lines


def format_env_part(env_part_token_lines):
    # 元の改行位置は無視して一度文単位に変換する
    normalized_token_lines = normalize_blank_line(
        split_env_part_token_lines_into_sentences(env_part_token_lines)
    )
    indentation_widths = determine_env_part_indentation_widths(normalized_token_lines)
    space_adjusted_lines = generate_space_adjusted_lines(normalized_token_lines)

    output_lines = []
    for indentation_width, line in zip(indentation_widths, space_adjusted_lines):
        line = f"{' ' * indentation_width}{line}"
        if line.split() and line.split()[0] in option.ENV_DIRECTIVE_KEYWORDS:
            output_lines.extend(
                split_line_at_max_length(line, option.ENVIRON_LINE_INDENTATION_WIDTH)
            )
        else:
            output_lines.append(line)

    return output_lines


def format_body_part(body_part_token_lines):
    normalized_token_lines = normalize_blank_line(body_part_token_lines)
    indentation_widths = determine_body_part_indentation_widths(normalized_token_lines)
    space_adjusted_lines = generate_space_adjusted_lines(normalized_token_lines)

    output_lines = []
    for indentation_width, line in zip(indentation_widths, space_adjusted_lines):
        line = f"{' ' * indentation_width}{line}"
        output_lines.extend(split_line_at_max_length(line, indentation_width))

    return output_lines


# 1行のテキストを入力とし、指定された最大文字数を超える場合、最大文字数以内で分割されたテキスト配列を返す
def split_line_at_max_length(line, indentation_width):
    lines = []
    while len(line) >= option.MAX_LINE_LENGTH:
        split_blank_pos = line.rfind(" ", 0, option.MAX_LINE_LENGTH)
        lines.append(line[:split_blank_pos])
        # 2行目以降はインデントのスペース数を考慮する
        line = f"{' ' * indentation_width}{line[split_blank_pos + 1:]}"

    lines.append(line)
    return lines


def split_env_part_token_lines_into_sentences(env_part_token_lines) -> list[list]:
    # 1次元のトークン列に変換する。この時改行を維持するため空文字列で表現する。
    tokens = list(
        itertools.chain.from_iterable(
            [tokens if len(tokens) != 0 else [""] for tokens in env_part_token_lines]
        )
    )

    token_sentences = []
    current_sentence_tokens = []
    for token in tokens:
        if token == "":
            token_sentences.append([])
        elif token.text == "environ" or token.token_type == TokenType.COMMENT:
            token_sentences.append([token])
        else:
            current_sentence_tokens.append(token)

            if token.text == ";":
                token_sentences.append(current_sentence_tokens)
                current_sentence_tokens = []

    return token_sentences


def determine_env_part_indentation_widths(env_part_token_lines):
    indentation_widths = []

    for tokens in env_part_token_lines:
        # 目標となるキーワードは必ず行頭に出現することを前提としている
        if (
            len(tokens) == 0
            or tokens[0].text == "environ"
            or tokens[0].token_type == TokenType.COMMENT
        ):
            indentation_widths.append(0)
        else:
            indentation_widths.append(option.ENVIRON_DIRECTIVE_INDENTATION_WIDTH)

    return indentation_widths


def determine_body_part_indentation_widths(body_part_token_lines):
    indentation_widths = []
    current_indentation_level = 0
    current_block_level = 0
    # Theorem, Scheme ブロック内でのみ利用
    current_block_type = ""
    is_top_level_proof = False

    # インデントの決定の目標となるキーワードは、必ず行頭に出現することを前提としている
    # adjust_newline_position で実装
    for tokens in body_part_token_lines:
        if tokens == []:
            indentation_widths.append(0)
            continue

        first_token_text = tokens[0].text

        # ブロックの開始/終了の整合性をチェックする
        if first_token_text in option.TOP_BLOCK_KEYWORDS and current_block_level > 0:
            logging.error(
                f"Expected 'end' on line {tokens[0].line_number}, column {tokens[0].column_number}"
            )
            sys.exit(1)
        elif first_token_text == "end" and current_block_level == 0:
            logging.error(
                "There are 'end' without a corresponding keyword on line "
                f"{tokens[0].line_number}, column {tokens[0].column_number}"
            )
            sys.exit(1)

        # ブロックレベルの調整
        if first_token_text in option.BLOCK_KEYWORDS:
            if not (
                current_block_type == "scheme"
                and first_token_text == "proof"
                and is_top_level_proof
            ):
                # schemeブロックの最初のproof以外はblock levelを+1
                current_block_level += 1
        elif first_token_text == "end":
            current_block_level -= 1

        # インデント数の決定と、インデント段階の変更
        # Pre-indentation width
        if (
            current_block_type in ["theorem", "scheme"]
            and first_token_text == "proof"
            and is_top_level_proof
        ) or first_token_text in ["provided", "end"]:
            # theorem/schemeのブロック内で最初のproof，またはprovided/endであればインデントを-1
            current_indentation_level -= 1

        indentation_widths.append(current_indentation_level * option.STANDARD_INDENTATION_WIDTH)

        # Post-indentation width
        if first_token_text in option.BLOCK_KEYWORDS or first_token_text == "provided":
            # 字下げキーワードまたはprovided以降はインデントを+1
            current_indentation_level += 1

        if first_token_text == "proof":
            is_top_level_proof = False

        # Theoremブロックの開始/終了判定
        if first_token_text == "theorem":
            current_block_type = "theorem"
            is_top_level_proof = True
            current_block_level = 1
        elif current_block_type == "theorem":
            if (first_token_text == "end" and current_block_level == 1) or (
                is_top_level_proof and ";" in convert_tokens_to_texts(tokens)
            ):
                current_block_type = ""
                current_block_level = 0

        # Schemeブロックの開始/終了判定
        if first_token_text == "scheme":
            current_block_type = "scheme"
            is_top_level_proof = True
            current_block_level = 1
        elif current_block_type == "scheme":
            if first_token_text == "end" and current_block_level == 0:
                current_block_type = ""
                current_block_level = 0

    return indentation_widths


# 特定のキーワードの前後で改行を挿入する
def adjust_newline_position(token_lines):
    output_token_lines = []
    for tokens in token_lines:
        if len(tokens) == 0:
            output_token_lines.append([])
            continue

        current_line_tokens = []
        for current_pos in range(len(tokens)):
            # 現在のトークンの直前で改行する場合、1つ前の行を確定する
            if (
                tokens[current_pos].text == ".="
                or tokens[current_pos].text in ["environ", "begin"]
                or tokens[current_pos].text in option.BLOCK_KEYWORDS
                or tokens[current_pos].text in option.ENV_DIRECTIVE_KEYWORDS
            ):
                # ".=", "environ", "begin" or ブロック開始キーワード or Directive開始キーワード
                if len(current_line_tokens) != 0:
                    output_token_lines.append(current_line_tokens)
                    current_line_tokens = []
            elif (
                tokens[current_pos].text == ":"
                and tokens[current_pos - 2].text not in [":", "theorem"]
                and tokens[current_pos - 1].token_type == TokenType.IDENTIFIER
                and tokens[current_pos - 1].identifier_type == IdentifierType.LABEL
            ):
                # LABEL: (":LABEL:", "theorem LABEL:" のパターンは除外)
                prev_token = current_line_tokens.pop()
                if len(current_line_tokens) != 0:
                    output_token_lines.append(current_line_tokens)
                current_line_tokens = [prev_token]

            current_line_tokens.append(tokens[current_pos])

            # 現在のトークンの直後で改行する場合、現在の行を確定する
            if (
                tokens[current_pos].text == ";"
                or tokens[current_pos].text in ["environ", "begin"]
                or (
                    tokens[current_pos].text == ":"
                    and current_line_tokens[0].text in ["theorem", "scheme"]
                )
                or (
                    tokens[current_pos].text in option.BLOCK_KEYWORDS
                    and not (
                        tokens[current_pos].text == "scheme"
                        or (
                            tokens[current_pos].text == "theorem"
                            and tokens[current_pos + 1].token_type == TokenType.IDENTIFIER
                            and tokens[current_pos + 1].identifier_type == IdentifierType.LABEL
                        )
                    )
                )
            ):
                # ";", "environ", "begin"
                # "theorem LABEL:", "scheme Scheme-Identifier { Scheme-Parameters }:" の直後
                # "theorem LABEL:", "scheme" を除く、ブロック開始キーワード直後
                output_token_lines.append(current_line_tokens)
                current_line_tokens = []

    return output_token_lines


def split_into_env_and_body_part(token_lines):
    for current_line_number, tokens in enumerate(token_lines):
        if tokens == []:
            continue

        init_token = tokens[0]
        if (
            init_token.token_type == TokenType.KEYWORD
            and init_token.keyword_type == KeywordType.BEGIN_
        ):
            return token_lines[:current_line_number], token_lines[current_line_number:]


def normalize_blank_line(token_lines):
    output_token_lines = []

    # 空行の挿入
    for current_line, tokens in enumerate(token_lines):
        if tokens == []:
            output_token_lines.append(tokens)
            continue

        first_token_text = tokens[0].text
        before_comment_line_number = count_comment_lines_before(token_lines, current_line)
        add_blank_line_number = (
            -1 * before_comment_line_number
            if before_comment_line_number
            else len(output_token_lines)
        )
        if first_token_text in option.KEYWORDS_INSERT_BLANK_LINE_BEFORE:
            output_token_lines.insert(add_blank_line_number, [])
        output_token_lines.append(tokens)
        if first_token_text in option.KEYWORDS_INSERT_BLANK_LINE_AFTER:
            output_token_lines.append([])

    first_no_empty_array_i = find_first_no_empty_array_i(output_token_lines)

    return remove_consecutive_value(output_token_lines[first_no_empty_array_i:], value=[])


def count_comment_lines_before(token_lines, target_line):
    comment_line_number = 0
    for line in reversed(range(target_line)):
        if token_lines[line] == []:
            return comment_line_number

        first_token_type = token_lines[line][0].token_type
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
