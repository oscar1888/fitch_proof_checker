import pytest
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication

from fitch_proof_checker.view.proof_layout import (
    setup_proof_layout, add_premise, add_step_after, add_step_before,
    delete_step, new_subproof, end_subproof, new_arbitary_constant,
    delete_arbitrary_constant, edit_goal, get_all_lines, get_premises
)


class DummyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.global_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(self.global_layout)
        self.setCentralWidget(central_widget)
        self.edited = False
        self.proof_layout = None
        self.goal_field = None
        self.goal_status_dot = None


@pytest.fixture
def fpe_window(qtbot):
    window = DummyMainWindow()
    qtbot.addWidget(window)
    setup_proof_layout(window)
    return window


@pytest.fixture
def set_focus(mocker):
    def _focus(widget):
        app = QApplication.instance()
        mocker.patch.object(app, 'focusWidget', return_value=widget)

    return _focus


def test_no_focus_returns_early(fpe_window, set_focus):
    set_focus(fpe_window.goal_field)

    assert add_step_after(fpe_window) is None
    assert add_step_before(fpe_window) is None
    assert delete_step(fpe_window) is None
    assert new_subproof(fpe_window) is None
    assert end_subproof(fpe_window) is None
    assert new_arbitary_constant(fpe_window) is None
    assert delete_arbitrary_constant(fpe_window) is None


def test_edit_goal(fpe_window, mocker):
    spy = mocker.spy(fpe_window.goal_field, 'setFocus')
    edit_goal(fpe_window)
    spy.assert_called_once()


def test_add_premise(fpe_window):
    add_premise(fpe_window)
    prems = get_premises(fpe_window)
    assert len(prems) == 2
    assert prems[1].is_assump is True
    assert fpe_window.edited is True


def test_add_step_after_branches(fpe_window, set_focus):
    lines = get_all_lines(fpe_window)
    set_focus(lines[0].formula_field)
    add_step_after(fpe_window)
    assert len(get_all_lines(fpe_window)) == 2
    assert get_all_lines(fpe_window)[1].is_assump is False

    set_focus(get_all_lines(fpe_window)[1].formula_field)
    add_step_after(fpe_window)
    assert len(get_all_lines(fpe_window)) == 3


def test_add_step_before_branches(fpe_window, set_focus):
    set_focus(get_all_lines(fpe_window)[0].formula_field)
    add_step_before(fpe_window)

    lines = get_all_lines(fpe_window)
    assert lines[0].is_assump is True
    assert lines[1].is_assump is False
    assert lines[1].depth == 0

    set_focus(lines[1].formula_field)

    new_subproof(fpe_window)

    sub_prem = get_all_lines(fpe_window)[1]
    set_focus(sub_prem.formula_field)
    add_step_before(fpe_window)

    final_lines = get_all_lines(fpe_window)
    assert final_lines[1].depth == 0
    assert final_lines[1].is_assump is False
    assert final_lines[2].depth == 1
    assert final_lines[2].is_assump is True


def test_delete_step_branches(fpe_window, set_focus):
    lines = get_all_lines(fpe_window)
    set_focus(lines[0].formula_field)
    delete_step(fpe_window)
    assert len(get_all_lines(fpe_window)) == 1

    set_focus(get_all_lines(fpe_window)[0].formula_field)
    add_step_after(fpe_window)
    assert len(get_all_lines(fpe_window)) == 2

    set_focus(get_all_lines(fpe_window)[1].formula_field)
    delete_step(fpe_window)
    assert len(get_all_lines(fpe_window)) == 1

    set_focus(get_all_lines(fpe_window)[0].formula_field)
    add_step_after(fpe_window)

    set_focus(get_all_lines(fpe_window)[1].formula_field)
    new_subproof(fpe_window)

    set_focus(get_all_lines(fpe_window)[1].formula_field)
    add_step_after(fpe_window)

    assert len(get_all_lines(fpe_window)) == 3

    set_focus(get_all_lines(fpe_window)[1].formula_field)
    delete_step(fpe_window)

    assert len(get_all_lines(fpe_window)) == 1


def test_new_subproof_branches(fpe_window, set_focus):
    set_focus(get_all_lines(fpe_window)[0].formula_field)
    new_subproof(fpe_window)
    assert get_all_lines(fpe_window)[1].depth == 1

    set_focus(get_all_lines(fpe_window)[0].formula_field)
    add_step_after(fpe_window)
    empty_line = get_all_lines(fpe_window)[1]
    set_focus(empty_line.formula_field)
    new_subproof(fpe_window)
    assert get_all_lines(fpe_window)[1].is_assump is True

    lines = get_all_lines(fpe_window)
    lines[1].formula_field.setText("A")
    set_focus(lines[1].formula_field)
    new_subproof(fpe_window)
    assert len(get_all_lines(fpe_window)) == 4


def test_end_subproof_branches(fpe_window, set_focus):
    lines = get_all_lines(fpe_window)
    set_focus(lines[0].formula_field)

    end_subproof(fpe_window)

    new_subproof(fpe_window)
    lines = get_all_lines(fpe_window)

    set_focus(lines[1].formula_field)
    end_subproof(fpe_window)
    assert get_all_lines(fpe_window)[2].depth == 0

    set_focus(get_all_lines(fpe_window)[0].formula_field)
    new_subproof(fpe_window)
    lines = get_all_lines(fpe_window)
    lines[1].formula_field.setText("P")
    set_focus(lines[1].formula_field)
    add_step_after(fpe_window)

    lines = get_all_lines(fpe_window)
    set_focus(lines[2].formula_field)
    end_subproof(fpe_window)
    assert get_all_lines(fpe_window)[2].depth == 0


def test_arbitrary_constant_branches(fpe_window, set_focus, mocker):
    lines = get_all_lines(fpe_window)
    set_focus(lines[0].formula_field)

    new_arbitary_constant(fpe_window)

    new_subproof(fpe_window)
    sub_line = get_all_lines(fpe_window)[1]
    set_focus(sub_line.formula_field)

    mocker.patch('PyQt6.QtWidgets.QInputDialog.getText', return_value=('', False))
    new_arbitary_constant(fpe_window)
    assert not hasattr(sub_line, 'arb_const_label')

    mocker.patch('PyQt6.QtWidgets.QInputDialog.getText', return_value=('z', True))
    mock_warn = mocker.patch('PyQt6.QtWidgets.QMessageBox.warning')
    new_arbitary_constant(fpe_window)
    mock_warn.assert_called_once()

    mocker.patch('PyQt6.QtWidgets.QInputDialog.getText', return_value=('a', True))
    new_arbitary_constant(fpe_window)
    assert 'a' in sub_line.arb_consts_introduced

    new_arbitary_constant(fpe_window)
    assert mock_warn.call_count == 2

    mocker.patch('PyQt6.QtWidgets.QInputDialog.getText', return_value=('b', True))
    new_arbitary_constant(fpe_window)
    assert 'b' in sub_line.arb_consts_introduced
    assert sub_line.arb_const_label.text() == "a b"


def test_delete_arbitrary_constant_branches(fpe_window, set_focus, mocker):
    set_focus(get_all_lines(fpe_window)[0].formula_field)
    new_subproof(fpe_window)
    sub_line = get_all_lines(fpe_window)[1]
    set_focus(sub_line.formula_field)

    sub_line.arb_consts_introduced = ['a', 'b']
    sub_line.arb_const_label = mocker.Mock()

    mocker.patch('PyQt6.QtWidgets.QInputDialog.getItem', return_value=('a', False))
    delete_arbitrary_constant(fpe_window)
    assert len(sub_line.arb_consts_introduced) == 2

    mocker.patch('PyQt6.QtWidgets.QInputDialog.getItem', return_value=('b', True))
    delete_arbitrary_constant(fpe_window)
    assert 'b' not in sub_line.arb_consts_introduced
    sub_line.arb_const_label.setText.assert_called_with("a")

    mocker.patch('PyQt6.QtWidgets.QInputDialog.getItem', return_value=('a', True))

    label_mock = sub_line.arb_const_label

    delete_arbitrary_constant(fpe_window)

    assert len(sub_line.arb_consts_introduced) == 0

    label_mock.deleteLater.assert_called_once()

    assert not hasattr(sub_line, 'arb_const_label')


def test_proof_line_paint_event(fpe_window):
    lines = get_all_lines(fpe_window)

    lines[0].grab()

    from fitch_proof_checker.view.proof_layout.proof_line_view import ProofLine

    complex_line = ProofLine(fpe_window, is_assump=True, depth=2)

    complex_line.line_number_label.setText("2")

    fpe_window.proof_layout.insertWidget(1, complex_line)

    complex_line.grab()
