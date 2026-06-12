from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QApplication

from fitch_proof_checker.view.proof_layout.fpe_line_edit import FPELineEdit
from fitch_proof_checker.view.proof_layout.proof_line_view import ProofLine


def setup_proof_layout(fpe_main_window):
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    container = QWidget()
    fpe_main_window.proof_layout = QVBoxLayout(container)
    fpe_main_window.proof_layout.setSpacing(0)
    fpe_main_window.proof_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    scroll.setWidget(container)
    fpe_main_window.global_layout.addWidget(scroll)
    add_premise(fpe_main_window)


def _get_all_lines(fpe_main_window):
    return [fpe_main_window.proof_layout.itemAt(i).widget() for i in range(fpe_main_window.proof_layout.count())]


def _get_premises(fpe_main_window):
    return [
        fpe_main_window.proof_layout.itemAt(i).widget()
        for i in range(fpe_main_window.proof_layout.count())
        if (line := fpe_main_window.proof_layout.itemAt(i).widget()).is_assump and line.depth == 0
    ]


def _enumerate_proof_lines(fpe_main_window):
    for i, line in enumerate(_get_all_lines(fpe_main_window)):
        line.line_number_label.setText(str(i + 1))


def _redraw_lines(fpe_main_window):
    for i in range(fpe_main_window.proof_layout.count()):
        fpe_main_window.proof_layout.itemAt(i).widget().update()


def update_layout(fpe_main_window):
    _redraw_lines(fpe_main_window)
    _enumerate_proof_lines(fpe_main_window)


def add_premise(fpe_main_window):
    premises = _get_premises(fpe_main_window)
    last_premise = premises[-1] if premises else None
    idx = int(last_premise.line_number_label.text()) if last_premise else 0
    row = ProofLine(fpe_main_window, is_assump=True)
    fpe_main_window.proof_layout.insertWidget(idx, row)
    row.formula_field.setFocus()
    update_layout(fpe_main_window)


def add_step_after(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    if current_line.is_assump and current_line.depth == 0:
        last_premise = _get_premises(fpe_main_window)[-1]
        idx = int(last_premise.line_number_label.text())
    else:
        idx = int(current_line.line_number_label.text())
    row = ProofLine(fpe_main_window, depth=current_line.depth)
    fpe_main_window.proof_layout.insertWidget(idx, row)
    row.formula_field.setFocus()
    update_layout(fpe_main_window)


def add_step_before(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    if current_line.is_assump and current_line.depth == 0:
        last_premise = _get_premises(fpe_main_window)[-1]
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
    update_layout(fpe_main_window)


def delete_step(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    premises = _get_premises(fpe_main_window)
    if len(premises) == 1 and current_line.is_assump and current_line.depth == 0: return

    if current_line.is_assump and current_line.depth > 0:
        pos = int(current_line.line_number_label.text()) - 1
        final_idx_to_del = pos
        for line in [fpe_main_window.proof_layout.itemAt(i).widget() for i in
                     range(pos, fpe_main_window.proof_layout.count())]:
            if line.depth < current_line.depth or line.depth == current_line.depth and line.is_assump: break
            final_idx_to_del += 1
        for i in range(pos, final_idx_to_del + 1):
            line = fpe_main_window.proof_layout.itemAt(i).widget()
            fpe_main_window.proof_layout.removeWidget(line)
            line.deleteLater()
        # focus a quello dopo e se non c'è quello prima
        fpe_main_window.proof_layout.itemAt(
            pos if pos < fpe_main_window.proof_layout.count() else pos - 1
        ).widget().formula_field.setFocus()
    else:
        lines = _get_all_lines(fpe_main_window)
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
        glob_prems = _get_premises(fpe_main_window)
        idx = int(glob_prems[-1].line_number_label.text())
        depth = 1
    elif not current_line.is_assump and not current_line.formula_field.text():
        idx = int(current_line.line_number_label.text()) - 1
        depth = current_line.depth + 1
        fpe_main_window.proof_layout.removeWidget(current_line)
        current_line.deleteLater()
    else:
        idx = int(current_line.line_number_label.text())
        depth = current_line.depth + 1

    row = ProofLine(fpe_main_window, is_assump=True, depth=depth)
    fpe_main_window.proof_layout.insertWidget(idx, row)
    row.formula_field.setFocus()
    update_layout(fpe_main_window)


def end_subproof(fpe_main_window):
    if not isinstance(QApplication.instance().focusWidget(), FPELineEdit):
        return
    current_line = QApplication.instance().focusWidget().proof_line
    if current_line.depth == 0: return

    lines = _get_all_lines(fpe_main_window)
    pos = int(current_line.line_number_label.text()) - 1
    next_line = fpe_main_window.proof_layout.itemAt(pos + 1).widget() if pos + 1 < len(lines) else None
    last_idx = pos
    for i in range(pos + 1, fpe_main_window.proof_layout.count()):
        e = fpe_main_window.proof_layout.itemAt(i).widget()
        if e.depth < current_line.depth or e.depth == current_line.depth and e.is_assump: break
        last_idx = i

    if (
        current_line.is_assump
        or (pos == len(lines) - 1
            or next_line.depth < current_line.depth
            or next_line.depth == current_line.depth and next_line.is_assump) and current_line.formula_field.text()
    ):
        row = ProofLine(fpe_main_window, depth=current_line.depth - 1)
        fpe_main_window.proof_layout.insertWidget(last_idx + 1, row)
        row.formula_field.setFocus()
    else:
        last_subproof_line = fpe_main_window.proof_layout.itemAt(last_idx).widget()
        if last_subproof_line.depth > current_line.depth: return
        last_subproof_line.depth -= 1
        last_subproof_line.formula_field.setFocus()
    update_layout(fpe_main_window)


def edit_goal(fpe_main_window):
    # TODO: implement this function
    pass


def verify_line(fpe_main_window):
    # TODO: implement this function
    pass


def verify_proof(fpe_main_window):
    # TODO: implement this function
    pass
