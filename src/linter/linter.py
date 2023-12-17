import logging
import utils.option as option
import itertools
from py_miz_controller import (
    ASTStatement,
    BlockType,
    ElementType,
    ASTToken,
    TokenType,
    IdentifierType,
)


def lint(miz_controller):
    ast_root = miz_controller.ast_root
    token_table = miz_controller.token_table
    token_lines = generate_token_lines(token_table)

    check_long_proof(ast_root)
    check_redundant_statement_label(ast_root, token_lines)


def check_long_proof(ast_root):
    if not (ast_root.child_component_num):
        return

    for i in range(ast_root.child_component_num):
        ast_component = ast_root.child_component(i)
        if ast_component.element_type != ElementType.BLOCK:
            continue

        if ast_component.block_type == BlockType.PROOF:
            if (
                ast_component.last_token.line_number
                - ast_component.first_token.line_number
                + 1
                <= option.MAX_PROOF_LINE_NUMBER
            ):
                continue

            logging.error(
                f"Proof too long [Ln {ast_component.first_token.line_number}, Col {ast_component.first_token.column_number}]"
            )
        else:
            check_long_proof(ast_component)


def generate_token_lines(token_table) -> list[list[ASTToken]]:
    token_lines: list[list] = [[] for _ in range(token_table.last_token.line_number)]

    for i in range(token_table.token_num):
        token = token_table.token(i)
        token_lines[token.line_number - 1].append(token)

    return token_lines


def extract_ast_statements(ast_block) -> list[ASTStatement]:
    ast_statements = []
    for i in range(ast_block.child_component_num):
        if ast_block.child_component(i).element_type == ElementType.STATEMENT:
            ast_statements.append(ast_block.child_component(i))

    return ast_statements


def extract_statement_tokens(
    token_lines, start_line_number, end_line_number
) -> list[ASTToken]:
    return list(
        itertools.chain.from_iterable(
            token_lines[start_line_number - 1 : end_line_number]
        )
    )


# 直前の式の引用のためにラベルを使用しているとき警告を出す
def check_redundant_statement_label(ast_block, token_lines):
    # 式を2行ずつ見ていく
    ast_statements = extract_ast_statements(ast_block)
    for statement, next_statement in zip(
        ast_statements[: len(ast_statements) - 1], ast_statements[1:]
    ):
        # 式にラベルが振られていることをチェック
        statement_tokens = extract_statement_tokens(
            token_lines,
            statement.range_first_token.line_number,
            statement.range_last_token.line_number,
        )
        referenced_label = None
        for token in statement_tokens:
            # `that`は2つ以上文を取れるため直後で`then`は使えない
            if token.text == "that":
                break

            if (
                token.token_type == TokenType.IDENTIFIER
                and token.identifier_type == IdentifierType.LABEL
                and not token.ref_token
            ):
                referenced_label = token
                break

        if not referenced_label:
            continue

        # 直後の式がラベルを引用しているかどうかチェック
        next_statement_tokens = extract_statement_tokens(
            token_lines,
            next_statement.range_first_token.line_number,
            next_statement.range_last_token.line_number,
        )
        reference_labels = []
        for i, token in enumerate(next_statement_tokens):
            if token.text == "by":
                reference_labels = [
                    token for token in next_statement_tokens[i + 1 :] if token.ref_token
                ]
                break

        for token in reference_labels:
            if token.ref_token == referenced_label:
                logging.error(
                    f"`{referenced_label.text}` is redundant citation label. Use `then` to omit the label [Ln {token.line_number}, Col {token.column_number}]"
                )
                break

    # 入れ子のブロックをさらに見に行く
    for i in range(ast_block.child_component_num):
        child_component = ast_block.child_component(i)
        if child_component.element_type == ElementType.BLOCK:
            check_redundant_statement_label(child_component, token_lines)
