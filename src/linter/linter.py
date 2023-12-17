import logging
import utils.option as option
from py_miz_controller import (
    BlockType,
    ElementType,
)


def lint(miz_controller):
    ast_root = miz_controller.ast_root

    check_long_proof(ast_root)
    check_too_many_nested_blocks(ast_root)


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


def check_too_many_nested_blocks(ast_root):
    for i in range(ast_root.child_component_num):
        ast_component = ast_root.child_component(i)
        if ast_component.element_type != ElementType.BLOCK:
            continue

        initial_nesting_number = 1
        nesting_levels = count_nesting_levels(ast_component, [initial_nesting_number])

        if (max(nesting_levels)) > option.MAX_NESTING_DEPTH:
            logging.error(
                f"Too many nested blocks [Ln {ast_component.range_first_token.line_number}, Col {ast_component.range_first_token.column_number}]"
            )


def count_nesting_levels(ast_component, nesting_levels):
    for i in range(ast_component.child_component_num):
        if ast_component.child_component(i).element_type == ElementType.BLOCK:
            nesting_levels[-1] += 1
            count_nesting_levels(ast_component.child_component(i), nesting_levels)
            nesting_levels.append(nesting_levels[-1] - 1)

    return nesting_levels
