import logging
import utils.option as option
from py_miz_controller import (
    BlockType,
    ElementType,
)


def lint(miz_controller):
  ast_root = miz_controller.ast_root

  check_long_proof(ast_root)


def check_long_proof(ast_root):
  if not(ast_root.child_component_num): return

  for i in range(ast_root.child_component_num):
    ast_component = ast_root.child_component(i)
    if ast_component.element_type != ElementType.BLOCK: continue

    if ast_component.block_type == BlockType.PROOF:
      if ast_component.last_token.line_number - ast_component.first_token.line_number + 1 <= option.MAX_PROOF_LINE_NUMBER: continue

      logging.error(f'Proof too long [Ln {ast_component.first_token.line_number}, Col {ast_component.first_token.column_number}]')
    else:
      check_long_proof(ast_component)