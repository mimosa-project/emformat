"""
TODO:
    文中の空白の入れ方を統一する処理を追加
    80文字オーバーの文を区切る場所判定＋分割位置リストを返す関数を作る
    環境宣言部分の字下げと改行
"""

import sys
import re

MAX_LINE_LENGTH = 80    # 1行の最大文字数
INDENT_SIZE = 2 # 字下げのスペースの個数
ENV_INDENT_LEVEL = 3    # 環境宣言部分のインデントの段階
VOCABRARY_DIRECTIVE_ITEM = "vocabularies"
REQUIREMENT_DIRECTIVE_ITEM = "requirements"
LIBRARY_DIRECTIVE_ITEMS = ["notations", "constructors", "registrations", 
"definitions", "expansions", "equalities", "theorems", "schemes"]
CORRECTNESS_CONDITION_ITEMS = ["correctness", "existence", "uniqueness",
"coherence", "compatibility", "consistency", "reducibility"]
# １行に単体で置く単語群
SINGLE_TAG_ITEMS = ["definition", "registration", "notation", "theorem",
"scheme", "case", "suppose", "hereby", "now", "proof", "environ", "begin",
"provided"]
# "end"と対になる単語群
WITH_END_ITEMS = ["definition", "registration", "notation", 'scheme', "case",
"suppose", "hereby", "now", "proof"]
# ブロックの開始タグ群
START_BLOSK_TAG_LIST = ["reserve", "definition", "registration", "notation", 
"theorem", "scheme"]


def split_with_env_wrapping(input_line):
    """
    環境宣言部分の各行に対し,80文字以内で分割できる適切な場所を探す
    Args:
        input_line(str): 1行分の文字列
    Returns:
        list: 分割する位置の要素番号
    TODO:
        len(line)を、リストの最後の要素に追加する
        字下げ分のスペース数を考慮
    """
    pass


def search_environ(input_lines):
    """'environ'が登場する行の値を見つけて返す"""
    for index, line in enumerate(input_lines):
        if 'environ' in line:
            return index


def search_begin(input_lines):
    """初めて'begin'が登場する行の値を見つけて返す"""
    for index, line in enumerate(input_lines):
        if 'begin' in line:
            return index


def process_environment_declaration(input_lines):
    """
    環境宣言部の処理をまとめた関数
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 整形された環境宣言部の文字列
    TODO:
        80文字エラー処理書いたらテストして組み込む
    """
    output_lines = []
    for line in input_lines:
        # 'environ'の行の後に空行を１行追加
        if 'environ' in line:
            output_lines.extend([line, ''])
        # 80文字以内ならスペースを入れてそのまま追加
        elif len(line) <= MAX_LINE_LENGTH:
            splited_line = ' ' + line
            output_lines.append(splited_line)
        else:
            splited_lines = []
            is_first_line = False   # 1行目であるか判定する変数
            # TODO: ここで80文字処理
            split_index_list = split_with_env_wrapping(line)
            start_index = 0
            end_index = 0
            for index in split_index_list:
                end_index = index
                splited_line = line[start_index: end_index]
                start_index = end_index
                # 1行目は直前にスペースを1つ入れる
                # 2行目以降は字下げを行う
                if is_first_line == True:
                    new_splited_line = ' ' + splited_line
                    is_first_line = False
                else:
                    new_splited_line = ' '*(INDENT_SIZE*ENV_INDENT_LEVEL) \
                        + splited_line
                splited_lines.append(new_splited_line)
            output_lines.extend(splited_lines)
    return output_lines


def generate_indent_level_list(input_lines):
    """
    各行のインデントレベルを調べる
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 各行のインデントレベルを記録
    """
    indent_level_list = []
    indent_level = 0
    is_in_theorem = False   # Theoremブロック内にいるか
    is_proof_in_theorem = False # Theoremブロック内にいる且つJustificationがProofであるか
    is_in_scheme = False    # Schemeブロック内にいるか
    semicolon_has_appeared_in_scheme = False  # schemeブロック内にいる且つ;が既出であるか
    skip_next_proof = False # 次のproofをendとの組にしない

    for index, line in enumerate(input_lines):
        if 'end;' in line:
            indent_level -= 1

        if is_in_scheme == True:
            if indent_level == 0:
                is_in_scheme = False
            # 'proof'が';'より先に出てくる場合,字下げはしない
            if (semicolon_has_appeared_in_scheme == False) and ('proof' in line):
                skip_next_proof = True
            elif ';' in line:
                semicolon_has_appeared_in_scheme = True

        if is_in_theorem == True:
            # theorem->初回proofの場合,Proofであることを判定
            if is_proof_in_theorem == False:
                if 'proof' in line:
                    is_proof_in_theorem = True

        indent_level_list.append(indent_level)

        # Theoremブロック終了判定
        if ('end;' in line) and (is_in_theorem == True):
                if indent_level == 1:
                    is_in_theorem = False
                    indent_level = 0

        # TheoremでProofなしの場合,';'がTheoremブロックの終了判定記号となる
        if (is_in_theorem == True) and \
             (is_proof_in_theorem == False):
            if re.search(';', line):
                is_in_theorem = False
                indent_level -= 1
                continue

        if 'theorem' in line:
            indent_level += 1
            is_in_theorem = True
            is_proof_in_theorem = False
            continue

        for item in WITH_END_ITEMS:
            if item in line:
                # schemeの場合
                if item == 'scheme':
                    indent_level += 1
                    is_in_scheme = True
                    semicolon_has_appeared_in_scheme = False
                    skip_next_proof = False
                # scheme->proofの場合,字下げカウントを飛ばす
                elif (is_in_scheme == True) and (item == 'proof') \
                    and (skip_next_proof == True):
                    skip_next_proof = False
                # 'cases'を省く
                elif item == 'case':
                    if not ('cases' in line):
                        indent_level += 1
                else:
                    indent_level += 1

    return indent_level_list


def indent_line(input_lines):
    """
    各行の文頭に字下げ分のスペースを挿入する
    ラベルは文頭に置き,続く文はインデントレベルに揃える
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 字下げ分のスペースが挿入された文字列
    """
    output_lines = []
    indent_level_list = generate_indent_level_list(input_lines)
    # 先頭ラベルのインデント調整
    # 各行に字下げ分のスペースを挿入
    for indent_level, line in zip(indent_level_list, input_lines):
        space_num = indent_level*INDENT_SIZE
        if re.search(r'^\s*[\w\d]+:', line):
            label_end_index = re.search(r'^\s*[\w\d]+:', line).end()
            label_str = line[:label_end_index]
            after_label_str = line[label_end_index:]
            new_after_label_str = after_label_str.lstrip()
            if len(label_str) < space_num:
                new_line = label_str + ' '*(space_num-len(label_str)) + \
                    new_after_label_str
            else:
                new_line = label_str + new_after_label_str
            output_lines.append(new_line)
        else:
            new_line = ' '*space_num + line
            output_lines.append(new_line)
    return output_lines


def insert_blankline(input_lines):
    """
    Text-Itemのブロック間に空行を挿入する
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: input_fileに出現するブロック間に空行が挿入された状態
    """
    output_lines = []
    prev_is_reserve = False 
    for line in input_lines:
        for item in START_BLOSK_TAG_LIST:
            if item in line:
                # item含む行の直前に挿入
                # reserveが続く場合は挿入なし
                if item == "reserve":
                    if prev_is_reserve == True:
                        output_lines.append(line)
                    else:
                        output_lines.extend(['', line])
                    prev_is_reserve = True
                else:
                    prev_is_reserve = False
                    output_lines.extend(['', line])
                break
        else:
            output_lines.append(line)
    return output_lines


def trim_before_punctuation(input_lines):
    """
    カンマ,セミコロンの直前の空白を取り除く
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 句読点直前の空白が取り除かれた文字列
    """
    output_lines = []
    for line in input_lines:
        new_line = re.sub(r'\s+(?=[,;])', '', line)
        output_lines.append(new_line)
    return output_lines


def trim_immediately_inside_brackets(input_lines):
    """
    括弧の始めの直後、終わりの直前の空白を取り除く
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 括弧内部の空白が取り除かれた文字列
    """
    output_lines = []
    for line in input_lines:
        new_line = re.sub(r'(?<=[\[\{\(])\s+|\s+(?=[\]\}\)])','',line)
        output_lines.append(new_line)
    return output_lines


def trim_interword(input_lines):
    """
    単語間の空白を1つづつにする
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 全単語間の空白が1つに整形された文字列
    """
    output_lines = []
    for line in input_lines:
        splited_line_list = line.split()
        new_line = ''
        for index, item in enumerate(splited_line_list):
            if index != 0:
                new_line += ' '+item
            else:
                new_line += item
        output_lines.append(new_line)
    return output_lines


def trim_extra_blank(input_lines):
    """
    行中の余分な空白を削除する処理をまとめた関数
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 行中の余分な空白が削除された文字列
    """
    punctuation_lines = trim_before_punctuation(input_lines)
    inside_brackets_line = \
        trim_immediately_inside_brackets(punctuation_lines)
    interword_lines = trim_interword(inside_brackets_line)
    
    output_lines = interword_lines
    return output_lines


def process_text_proper(input_lines):
    """
    証明記述部分の処理をまとめた関数
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 整形された文字列
    """
    output_lines = []
    trimmed_extra_blank_lines = trim_extra_blank(input_lines)
    indented_lines = indent_line(trimmed_extra_blank_lines)
    inserted_blankline_lines = insert_blankline(indented_lines)
    output_lines = inserted_blankline_lines
    return output_lines


def process_lines(input_lines):
    """
    前処理後のファイルを整形する処理をまとめた関数
    まず冒頭のコメント部,環境宣言部('environ'以下),証明記述部('begin'以下)を
    分割し,それぞれ処理してから統合
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 整形された文字列
    TODO:
        環境宣言部の処理を書く
    """
    output_lines = []
    environment_declaration_lines = []
    text_proper_lines = []

    environ_index = search_environ(input_lines)
    begin_index = search_begin(input_lines)
    outline_comment_lines = [line for line in input_lines[: environ_index]]
    environment_declaration_lines = \
        [line for line in input_lines[environ_index: begin_index]]
    text_proper_lines = [line for line in input_lines[begin_index:]]

    #new_environment_declaration_lines = \
    #    process_environment_declaration(environment_declaration_lines)
    new_environment_declaration_lines = environment_declaration_lines
    new_text_proper_lines = process_text_proper(text_proper_lines)
    
    if len(outline_comment_lines)==0:
        output_lines.extend(new_environment_declaration_lines)
        output_lines.append('')
        output_lines.extend(new_text_proper_lines)
    else:
        output_lines.extend(outline_comment_lines)
        output_lines.append('')
        output_lines.extend(new_environment_declaration_lines)
        output_lines.append('')
        output_lines.extend(new_text_proper_lines)

    return output_lines
   

def findall_index(pattern, line):
    """
    行の中に存在する全ての特定の文字列の位置を調べる
    Args:
        pattern(str): 存在を調べたい文字列
        line(str): 探索される行の文字列
    Returns:
        list: 全ての一致した部分の頭文字の位置
    """
    output_list = []
    for index in range(len(line)-len(pattern)+1):
        if line[index: index+len(pattern)] == pattern:
            output_list.append(index)
    return output_list


def split_with_semicolon(input_lines):
    """
    文末までで1行になるように行を連結して作り直す
    連結するときは単語間に1つのスペースを入れる
    コメント文を含む場合は連結しない
    ラベルが先頭に出現する場合は連結しない
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 整形された文字列
    """
    splited_lines = []
    output_lines = []
    for line in input_lines:
        split_index_list = [] # ';'の位置のリスト
        if ';' in line:
            split_index_list = findall_index(';', line)
            start_index = 0
            end_index = 0
            for split_index in split_index_list:
                end_index = split_index + 1
                splited_lines.append(line[start_index: end_index])
                start_index = end_index
            splited_lines.append(line[start_index:])
        else:
            splited_lines.append(line)
        
    splited_lines = [l for l in splited_lines if l != '']
    
    is_intext = False  # 文が途中であるかどうか
    is_in_comment = False # ひとつ前の文がコメント文を含むかどうか
    for line in splited_lines:
        # コメント文を含む場合はそのまま追加
        if '::' in line:
            is_in_comment = True
            output_lines.append(line)
        # 先頭にラベルを含む場合は次の要素に追加
        # TODO: トークナイザー出来たらそっちで分割処理。ここ消す
        elif re.search(r'^\s*[\w\d]*:', line):
            output_lines.append(line)
            if ';' in line:
                is_intext = False

        # 文の途中でない場合は次の要素に追加
        # 文中に ';' が含まれる（文が終了する）かどうか確認
        elif is_intext == False:
            output_lines.append(line)
            if ';' not in line:
                is_intext = True
        # 文の途中である場合は、ひとつ前の要素の文字列と連結する
        # 前の文がコメント文を含む場合は次の要素に追加
        # 文中に ';' が含まれる（文が終了する）かどうか確認
        else:
            if is_in_comment==False:
                output_lines[len(output_lines)-1] += ' ' + line
            else:
                output_lines.append(line)
                is_in_comment = False
            if ';' in line:
                is_intext = False
    return output_lines


# ".=" の直前で行を分割して返す
def split_with_equalsign(input_lines):
    """
    '.='で行を分割して,文を作り直す
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: '.='で行が分割された文字列
    """
    output_lines = []
    for line in input_lines:
        split_index_list = []   # '.='の'.'の位置のリスト
        if '.=' in line:
            split_index_list = findall_index('.=', line)
            start_index = 0
            end_index = 0
            for split_index in split_index_list:
                end_index = split_index   # '.='の直前が区切り
                output_lines.append(line[start_index: end_index])
                start_index = end_index
            output_lines.append(line[start_index:])
        else:
            output_lines.append(line)
    return output_lines


def split_with_items(input_lines):
    """
    'definition', 'proof'などの単語を単体で1行として,文を作り直す
    'theorem'ブロックはタグごと
    'scheme'ブロックは識別子ごと
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 単語の前後で行が分割された文字列
    TODO:
        ループで拾えないproofがあるので'''以下を追加.
        できれば修正したい.
    """
    output_lines = []
    for line in input_lines:
        is_in_comment = False   # コメント文を含むかどうか
        if '::' in line:
            is_in_comment = True
        for item in SINGLE_TAG_ITEMS:
            if re.search(item+r"[^s]", line):
                # タグ名指定のあるtheoremブロックの場合
                if re.search('theorem'+r'\s*[\d\w]+:', line):
                    tag_obj = re.search('[\d\w]+:', line)
                    tag_str = tag_obj.group()
                    line = re.sub(r'\s*theorem\s+[\d\w]+:\s*',
                        '\n'+'theorem '+tag_str+'\n', line)
                # schemeブロックの場合
                elif item == 'scheme':
                    line = re.sub(':', ':\n', line)
                    line = re.sub('provided', '\nprovided\n', line)
                else:
                    line = re.sub('\s*'+item+'\s*', '\n'+item+'\n', line)
        # '''
        if 'proof' in line and not ('\nproof\n' in line):
            line = re.sub('\s*proof\s*', '\nproof\n', line)
        # '''

        tmp_lines = line.split('\n')
        new_lines = [l for l in tmp_lines if l != '']
        # 文の後にコメント文を含む場合は、ひとつ前の行と連結
        if is_in_comment==True and len(new_lines) > 1:
            new_lines[len(new_lines)-2] += ' ' + new_lines.pop()
        output_lines.extend(new_lines)

    return output_lines


def preprocess_line(input_lines):
    """
    入力ファイルに対して行う前処理をまとめた関数
    文頭と文末の余分な空白,改行のみの行は削除する
    Args:
        input_lines(list): 1行が1要素として格納された文字列
    Returns:
        list: 前処理済の文字列
    """
    output_lines = []
    new_input_lines = [line.strip() for line in input_lines]
    new_input_lines = [line for line in new_input_lines if line != '']

    splited_with_semicolon_lines = split_with_semicolon(new_input_lines)
    splited_with_equalsign_lines = split_with_equalsign(
        splited_with_semicolon_lines)
    splited_with_items_lines = split_with_items(splited_with_equalsign_lines)

    stripped_lines = [l.strip() for l in splited_with_items_lines]
    output_lines.extend(stripped_lines)
    return output_lines


def main():
    file_path = sys.argv[1]
    input_lines = []        # 入力ファイルの内容
    output_lines = []       # 出力ファイルの内容
    preprocessed_lines = [] # 入力ファイルに前処理を行った内容
    processed_lines = []    # 前処理後のファイルに処理を行った内容

    with open(file_path, "r") as f1:
        input_lines = f1.readlines()
    
    preprocessed_lines = preprocess_line(input_lines)
    #preprocessed_lines = [line+'\n' for line in preprocessed_lines]
    processed_lines = process_lines(preprocessed_lines)
    processed_lines = [line+'\n' for line in processed_lines]
    output_lines = processed_lines
    
    with open(file_path, "w") as f2:
        for line in output_lines:
            f2.write(line)


if __name__ == '__main__':
    main()