from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QApplication, QHBoxLayout, QLabel, QLineEdit, \
    QInputDialog, QMessageBox
from fitch_proof_checker.view.fpe_line_edit import FPELineEdit
from fitch_proof_checker.view.proof_layout.proof_line_view import ProofLine
from fitch_proof_checker.view.utils import create_status_dot, qle_font, ARB_CONST_LABEL_STYLE


def setup_proof_layout(fpe_main_window):
    _create_proof_area(fpe_main_window)
    _create_goal_area(fpe_main_window)


def _create_proof_area(fpe_main_window):
    proof_title = QLabel("Proof:")
    proof_title.setStyleSheet("font-weight: bold; color: #333;")
    fpe_main_window.global_layout.addWidget(proof_title)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    container = QWidget()
    fpe_main_window.proof_layout = QVBoxLayout(container)
    fpe_main_window.proof_layout.setSpacing(0)
    fpe_main_window.proof_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    scroll.setWidget(container)
    fpe_main_window.global_layout.addWidget(scroll)

    add_premise(fpe_main_window)


def _create_goal_area(fpe_main_window):
    goal_layout = QHBoxLayout()
    goal_label = QLabel("Goal:")
    goal_label.setStyleSheet("font-weight: bold;")
    fpe_main_window.goal_field = QLineEdit()
    fpe_main_window.goal_field.setFont(qle_font)
    goal_layout.addWidget(goal_label)
    goal_layout.addWidget(fpe_main_window.goal_field)

    fpe_main_window.goal_status_dot = create_status_dot()
    goal_layout.addWidget(fpe_main_window.goal_status_dot)

    fpe_main_window.global_layout.addLayout(goal_layout)


def get_all_lines(fpe_main_window):
    return [fpe_main_window.proof_layout.itemAt(i).widget() for i in range(fpe_main_window.proof_layout.count())]


def get_premises(fpe_main_window):
    return [
        line
        for i in range(fpe_main_window.proof_layout.count())
        if (line := fpe_main_window.proof_layout.itemAt(i).widget()).is_assump and line.depth == 0
    ]


def _enumerate_proof_lines(fpe_main_window):
    for i, line in enumerate(get_all_lines(fpe_main_window)):
        line.line_number_label.setText(str(i + 1))


def _redraw_lines(fpe_main_window):
    for i in range(fpe_main_window.proof_layout.count()):
        fpe_main_window.proof_layout.itemAt(i).widget().update()


def update_layout(fpe_main_window):
    _enumerate_proof_lines(fpe_main_window)
    _redraw_lines(fpe_main_window)


def add_premise(fpe_main_window):
    premises = get_premises(fpe_main_window)
    last_premise = premises[-1] if premises else None
    idx = int(last_premise.line_number_label.text()) if last_premise else 0
    row = ProofLine(fpe_main_window, is_assump=True)
    fpe_main_window.proof_layout.insertWidget(idx, row)
    row.formula_field.setFocus()
    if premises: fpe_main_window.edited = True
    update_layout(fpe_main_window)


def add_step_after(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    if current_line.is_assump and current_line.depth == 0:
        last_premise = get_premises(fpe_main_window)[-1]
        idx = int(last_premise.line_number_label.text())
    else:
        idx = int(current_line.line_number_label.text())
    row = ProofLine(fpe_main_window, depth=current_line.depth)
    fpe_main_window.proof_layout.insertWidget(idx, row)
    row.formula_field.setFocus()
    fpe_main_window.edited = True
    update_layout(fpe_main_window)


def add_step_before(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    if current_line.is_assump and current_line.depth == 0:
        last_premise = get_premises(fpe_main_window)[-1]
        idx = int(last_premise.line_number_label.text())
    else:
        idx = int(current_line.line_number_label.text()) - 1
    row = ProofLine(fpe_main_window,
                    depth=current_line.depth - 1
                    if current_line.is_assump and current_line.depth > 0
                    else current_line.depth
                    )
    fpe_main_window.proof_layout.insertWidget(idx, row)
    row.formula_field.setFocus()
    fpe_main_window.edited = True
    update_layout(fpe_main_window)


def find_final_subproof_idx(fpe_main_window, current_line):
    pos = int(current_line.line_number_label.text()) - 1
    final_idx = pos
    for line in [fpe_main_window.proof_layout.itemAt(i).widget() for i in
                 range(pos + 1, fpe_main_window.proof_layout.count())]:
        if line.depth < current_line.depth or line.depth == current_line.depth and line.is_assump: break
        final_idx += 1
    return final_idx


def delete_step(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    premises = get_premises(fpe_main_window)
    if len(premises) == 1 and current_line.is_assump and current_line.depth == 0: return

    if current_line.is_assump and current_line.depth > 0:
        pos = int(current_line.line_number_label.text()) - 1
        final_idx_to_del = find_final_subproof_idx(fpe_main_window, current_line)
        for i in range(final_idx_to_del, pos-1, -1):
            line = fpe_main_window.proof_layout.itemAt(i).widget()
            fpe_main_window.proof_layout.removeWidget(line)
            line.deleteLater()
        fpe_main_window.proof_layout.itemAt(
            pos if pos < fpe_main_window.proof_layout.count() else pos - 1
        ).widget().formula_field.setFocus()
    else:
        lines = get_all_lines(fpe_main_window)
        curr_line_num = int(current_line.line_number_label.text())
        fpe_main_window.proof_layout.removeWidget(current_line)
        current_line.deleteLater()
        fpe_main_window.proof_layout.itemAt(
            curr_line_num - (1 if curr_line_num < len(lines) else 2)
        ).widget().formula_field.setFocus()
    update_layout(fpe_main_window)


def new_subproof(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line

    if current_line.is_assump and current_line.depth == 0:
        glob_prems = get_premises(fpe_main_window)
        idx = int(glob_prems[-1].line_number_label.text())
    elif not current_line.is_assump and not current_line.formula_field.text():
        idx = int(current_line.line_number_label.text()) - 1
        fpe_main_window.proof_layout.removeWidget(current_line)
        current_line.deleteLater()
    else:
        idx = int(current_line.line_number_label.text())

    row = ProofLine(fpe_main_window, is_assump=True, depth=current_line.depth + 1)
    fpe_main_window.proof_layout.insertWidget(idx, row)
    row.formula_field.setFocus()
    fpe_main_window.edited = True
    update_layout(fpe_main_window)


def end_subproof(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    if current_line.depth == 0: return
    last_idx = find_final_subproof_idx(fpe_main_window, current_line)

    if current_line.is_assump or current_line.formula_field.text():
        row = ProofLine(fpe_main_window, depth=current_line.depth - 1)
        fpe_main_window.proof_layout.insertWidget(last_idx + 1, row)
        row.formula_field.setFocus()
    else:
        last_subproof_line = fpe_main_window.proof_layout.itemAt(last_idx).widget()
        if last_subproof_line.depth > current_line.depth: return
        row = ProofLine(fpe_main_window, depth=last_subproof_line.depth-1)
        row.formula_field.setText(last_subproof_line.formula_field.text())
        row.justification_field.setText(last_subproof_line.justification_field.text())
        fpe_main_window.proof_layout.removeWidget(last_subproof_line)
        last_subproof_line.deleteLater()
        fpe_main_window.proof_layout.insertWidget(int(last_subproof_line.line_number_label.text())-1, row)
        row.formula_field.setFocus()
    update_layout(fpe_main_window)


def new_arbitary_constant(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    proof_line = QApplication.instance().focusWidget().proof_line
    if not proof_line.is_assump or proof_line.depth == 0: return

    const_name, ok = QInputDialog.getText(
        fpe_main_window,
        "New arbitrary constant",
        "Write the constant name (e.g. \"a\"):"
    )

    if ok and const_name.strip():
        const_name = const_name.strip()

        if const_name in proof_line.arb_consts_introduced:
            QMessageBox.warning(
                fpe_main_window,
                "Duplicated constant",
                f"The constant '{const_name}' was already introduced in this line."
            )
            return

        proof_line.arb_consts_introduced.append(const_name)

        if not hasattr(proof_line, 'arb_const_label'):
            proof_line.arb_const_label = QLabel()
            proof_line.arb_const_label.setStyleSheet(ARB_CONST_LABEL_STYLE)
            proof_line.layout().insertWidget(2, proof_line.arb_const_label)

        proof_line.arb_const_label.setText(" ".join(proof_line.arb_consts_introduced))


def delete_arbitrary_constant(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    proof_line = QApplication.instance().focusWidget().proof_line
    if not proof_line.is_assump or proof_line.depth == 0 or not proof_line.arb_consts_introduced: return

    item, ok = QInputDialog.getItem(
        fpe_main_window,
        "Delete arbitrary constant",
        "Select the constant to remove:",
        proof_line.arb_consts_introduced,
        0,
        False
    )

    if ok and item:
        proof_line.arb_consts_introduced.remove(item)

        if not proof_line.arb_consts_introduced:
            proof_line.arb_const_label.deleteLater()
            del proof_line.arb_const_label
        else:
            proof_line.arb_const_label.setText(" ".join(proof_line.arb_consts_introduced))


def edit_goal(fpe_main_window):
    fpe_main_window.goal_field.setFocus()
