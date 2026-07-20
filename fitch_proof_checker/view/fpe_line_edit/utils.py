from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from fitch_proof_checker.view.fpe_line_edit import FPELineEdit
from fitch_proof_checker.view.proof_layout import add_step_after, end_subproof, get_all_lines


def move(movement):
    def _inner_move(fpe_main_window):
        if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
            return
        current_line = QApplication.instance().focusWidget().proof_line
        pos = int(current_line.line_number_label.text()) - 1
        lines = get_all_lines(fpe_main_window)
        if not (0 <= pos + movement < len(lines)): return
        line_to_focus = fpe_main_window.proof_layout.itemAt(pos + movement).widget()
        line_to_focus.formula_field.setFocus()
    return _inner_move


shortcuts_conds = [
    (lambda e: e.key() == Qt.Key.Key_A and (e.modifiers() & Qt.KeyboardModifier.ControlModifier), add_step_after),
    (lambda e: e.key() == Qt.Key.Key_E and (e.modifiers() & Qt.KeyboardModifier.ControlModifier), end_subproof),
    (lambda e: e.key() == Qt.Key.Key_Up, move(-1)),
    (lambda e: e.key() == Qt.Key.Key_Down, move(+1)),
]

symbol_map = {
    "<->": ('Co-Implies', "↔"),
    "->": ('Implies', "→"),
    "~": ('Not', "¬"),
    "\\forall ": ('For all', "∀"),
    "\\exists ": ('Exists', "∃"),
    "/\\": ('And', "∧"),
    "\\/": ('Or', "∨"),
    "_|_": ('False', "⊥"),
    "!=": ('Not Equal', "≠"),
    "\\mul ": ('Times', "×")
}
