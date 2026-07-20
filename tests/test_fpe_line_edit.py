import sys
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QLineEdit
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QEvent
from fitch_proof_checker.view.fpe_line_edit import FPELineEdit


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def mock_main_window():
    mw = MagicMock()
    mw.edited = False
    return mw


@pytest.fixture
def mock_proof_line():
    return MagicMock()


@pytest.fixture
def fpe_edit(qapp, mock_proof_line, mock_main_window):
    widget = FPELineEdit(mock_proof_line, mock_main_window)
    return widget


def test_init(fpe_edit, mock_proof_line, mock_main_window):
    assert fpe_edit.proof_line is mock_proof_line
    assert fpe_edit.fpe_main_window is mock_main_window
    assert fpe_edit.font() is not None


def test_on_text_edited_no_replacement(fpe_edit, mocker):
    fpe_edit.setText("A B C")
    fpe_edit.setCursorPosition(5)

    mock_set_cursor = mocker.patch.object(fpe_edit, 'setCursorPosition')
    mock_set_text = mocker.patch.object(fpe_edit, 'setText')

    fpe_edit._on_text_edited("A B C")

    assert fpe_edit.fpe_main_window.edited is True
    mock_set_text.assert_not_called()
    mock_set_cursor.assert_not_called()


def test_on_text_edited_with_replacement(fpe_edit):
    fpe_edit.setText("A -> B")
    fpe_edit.setCursorPosition(6)

    fpe_edit._on_text_edited("A -> B")

    assert fpe_edit.text() == "A → B"

    assert fpe_edit.cursorPosition() == 5


def test_context_menu_event(fpe_edit, mocker):
    mock_menu = MagicMock()
    mock_logic_menu = MagicMock()
    mock_menu.addMenu.return_value = mock_logic_menu

    mocker.patch.object(fpe_edit, 'createStandardContextMenu', return_value=mock_menu)
    mocker.patch.object(fpe_edit, 'insert')

    event = MagicMock()
    fpe_edit.contextMenuEvent(event)

    mock_menu.addSeparator.assert_called_once()
    mock_menu.addMenu.assert_called_once_with("Insert Logic Symbol")
    mock_menu.exec.assert_called_once_with(event.globalPos())

    assert mock_logic_menu.addAction.call_count > 0

    action_args = mock_logic_menu.addAction.call_args_list[0]
    action_obj = action_args[0][0]

    action_obj.trigger()
    fpe_edit.insert.assert_called()


def test_key_press_event_handled(fpe_edit, mocker):
    mock_action = MagicMock()
    fake_conds = [(lambda e: True, mock_action)]

    mocker.patch('fitch_proof_checker.view.fpe_line_edit.utils.shortcuts_conds', fake_conds, create=True)

    event = MagicMock()
    with patch.object(QLineEdit, 'keyPressEvent') as mock_super_keypress:
        fpe_edit.keyPressEvent(event)

        mock_action.assert_called_once_with(fpe_edit.fpe_main_window)
        mock_super_keypress.assert_not_called()


def test_key_press_event_unhandled(fpe_edit, mocker):
    mock_action = MagicMock()
    fake_conds = [(lambda e: False, mock_action)]
    mocker.patch('fitch_proof_checker.view.fpe_line_edit.utils.shortcuts_conds', fake_conds, create=True)

    event = MagicMock()
    with patch.object(QLineEdit, 'keyPressEvent') as mock_super_keypress:
        fpe_edit.keyPressEvent(event)

        mock_action.assert_not_called()
        mock_super_keypress.assert_called_once_with(event)


def test_utils_move_wrong_widget(qapp, mocker):
    from fitch_proof_checker.view.fpe_line_edit.utils import move

    mock_app = MagicMock()
    mock_app.focusWidget.return_value = QLineEdit()
    mocker.patch('PyQt6.QtWidgets.QApplication.instance', return_value=mock_app)

    move_down = move(1)

    move_down(MagicMock())


def test_utils_move_out_of_bounds(qapp, fpe_edit, mocker):
    from fitch_proof_checker.view.fpe_line_edit.utils import move

    mock_app = MagicMock()
    fpe_edit.proof_line = MagicMock()
    fpe_edit.proof_line.line_number_label.text.return_value = "1"

    mock_app.focusWidget.return_value = fpe_edit
    mocker.patch('PyQt6.QtWidgets.QApplication.instance', return_value=mock_app)

    mocker.patch('fitch_proof_checker.view.fpe_line_edit.utils.get_all_lines', return_value=[MagicMock()])

    move_up = move(-1)
    move_up(MagicMock())


def test_utils_move_success(qapp, fpe_edit, mocker):
    from fitch_proof_checker.view.fpe_line_edit.utils import move

    mock_app = MagicMock()
    fpe_edit.proof_line = MagicMock()
    fpe_edit.proof_line.line_number_label.text.return_value = "1"

    mock_app.focusWidget.return_value = fpe_edit
    mocker.patch('PyQt6.QtWidgets.QApplication.instance', return_value=mock_app)

    mocker.patch('fitch_proof_checker.view.fpe_line_edit.utils.get_all_lines', return_value=["line1", "line2"])

    mock_mw = MagicMock()
    mock_layout_item = MagicMock()
    mock_target_widget = MagicMock()

    mock_mw.proof_layout.itemAt.return_value = mock_layout_item
    mock_layout_item.widget.return_value = mock_target_widget

    move_down = move(1)
    move_down(mock_mw)

    mock_mw.proof_layout.itemAt.assert_called_with(1)
    mock_target_widget.formula_field.setFocus.assert_called_once()


def test_shortcuts_conditions_lambdas(qapp):
    from fitch_proof_checker.view.fpe_line_edit.utils import shortcuts_conds

    cond_ctrl_a = shortcuts_conds[0][0]
    cond_ctrl_e = shortcuts_conds[1][0]
    cond_up = shortcuts_conds[2][0]
    cond_down = shortcuts_conds[3][0]

    event_a = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
    assert cond_ctrl_a(event_a)

    event_e = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_E, Qt.KeyboardModifier.ControlModifier)
    assert cond_ctrl_e(event_e)

    event_up = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Up, Qt.KeyboardModifier.NoModifier)
    assert cond_up(event_up)

    event_down = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
    assert cond_down(event_down)
