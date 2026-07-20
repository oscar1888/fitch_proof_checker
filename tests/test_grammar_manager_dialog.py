import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QPushButton, QWidget

from fitch_proof_checker.view.grammar_manager_dialog import GrammarManagerDialog


class DummyParent(QWidget):
    pass


@pytest.fixture
def setup_dialog(qtbot, mocker):
    parent = DummyParent()
    dialog = GrammarManagerDialog(parent)

    dialog._keep_parent_alive = parent

    qtbot.addWidget(dialog)

    presenter_mock = mocker.Mock()
    dialog.add_presenter(presenter_mock)

    return dialog, presenter_mock


def test_initialization_and_presenter(setup_dialog):
    dialog, presenter = setup_dialog

    presenter.populate_list.assert_any_call('connective')
    presenter.populate_list.assert_any_call('quantifier')
    assert presenter.populate_list.call_count == 2


def test_tab_buttons_signals(setup_dialog, qtbot, mocker):
    dialog, _ = setup_dialog
    mock_add = mocker.patch.object(dialog, '_add_item')
    mock_remove = mocker.patch.object(dialog, '_remove_item')

    buttons = dialog.findChildren(QPushButton)

    btn_add_conn = next(b for b in buttons if b.text() == "Add Connective...")
    btn_rm_conn = next(b for b in buttons if b.text() == "Remove Connective")
    btn_add_quant = next(b for b in buttons if b.text() == "Add Quantifier...")
    btn_rm_quant = next(b for b in buttons if b.text() == "Remove Quantifier")

    qtbot.mouseClick(btn_add_conn, Qt.MouseButton.LeftButton)
    mock_add.assert_called_with('connective')

    qtbot.mouseClick(btn_rm_conn, Qt.MouseButton.LeftButton)
    mock_remove.assert_called_with('connective')

    qtbot.mouseClick(btn_add_quant, Qt.MouseButton.LeftButton)
    mock_add.assert_called_with('quantifier')

    qtbot.mouseClick(btn_rm_quant, Qt.MouseButton.LeftButton)
    mock_remove.assert_called_with('quantifier')


def test_bottom_buttons_signals(setup_dialog, qtbot, mocker):
    dialog, _ = setup_dialog

    mock_load_def = mocker.patch.object(dialog, '_load_default_grammar')
    mock_load_prof = mocker.patch.object(dialog, '_load_profile')
    mock_save_prof = mocker.patch.object(dialog, '_save_profile')

    dialog.btn_load_default.clicked.disconnect()
    dialog.btn_load_default.clicked.connect(dialog._load_default_grammar)

    dialog.btn_load_profile.clicked.disconnect()
    dialog.btn_load_profile.clicked.connect(dialog._load_profile)

    dialog.btn_save_profile.clicked.disconnect()
    dialog.btn_save_profile.clicked.connect(dialog._save_profile)

    qtbot.mouseClick(dialog.btn_load_default, Qt.MouseButton.LeftButton)
    mock_load_def.assert_called_once()

    qtbot.mouseClick(dialog.btn_load_profile, Qt.MouseButton.LeftButton)
    mock_load_prof.assert_called_once()

    qtbot.mouseClick(dialog.btn_save_profile, Qt.MouseButton.LeftButton)
    mock_save_prof.assert_called_once()


def test_remove_item_no_selection(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mock_warn = mocker.patch('PyQt6.QtWidgets.QMessageBox.warning')

    dialog._remove_item('connective')

    mock_warn.assert_called_once()
    assert "Select a connective" in mock_warn.call_args[0][2]
    presenter.remove_item.assert_not_called()


def test_remove_item_protected(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mock_warn = mocker.patch('PyQt6.QtWidgets.QMessageBox.warning')

    dialog.list_connectives.addItem("And")
    dialog.list_connectives.setCurrentRow(0)

    presenter.get_item_name.return_value = "And"
    presenter.is_protected_item.return_value = True

    dialog._remove_item('connective')

    mock_warn.assert_called_once()
    assert "Cannot remove" in mock_warn.call_args[0][2]
    presenter.remove_item.assert_not_called()


def test_remove_item_user_cancels(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    dialog.list_connectives.addItem("CustomConn")
    dialog.list_connectives.setCurrentRow(0)

    presenter.is_protected_item.return_value = False
    mocker.patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.No)

    dialog._remove_item('connective')
    presenter.remove_item.assert_not_called()


def test_remove_item_quantifier_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    dialog.list_quantifiers.addItem("CustomQuant")
    dialog.list_quantifiers.setCurrentRow(0)

    presenter.is_protected_item.return_value = False
    mocker.patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes)

    dialog._remove_item('quantifier')
    presenter.remove_item.assert_called_once_with('quantifier', 0)


def test_add_item_cancelled(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("", ""))

    dialog._add_item('connective')
    presenter.add_item.assert_not_called()


def test_add_item_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("plugin.py", ""))
    presenter.add_item.return_value = (True, "Plugin added successfully")
    mock_info = mocker.patch('PyQt6.QtWidgets.QMessageBox.information')

    dialog._add_item('quantifier')

    presenter.add_item.assert_called_once_with('quantifier', "plugin.py")
    mock_info.assert_called_once()


def test_add_item_failure(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("plugin.py", ""))
    presenter.add_item.return_value = (False, "Syntax error")
    mock_crit = mocker.patch('PyQt6.QtWidgets.QMessageBox.critical')

    dialog._add_item('connective')
    mock_crit.assert_called_once()


def test_load_default_cancelled(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.No)

    dialog._load_default_grammar()
    presenter.load_default_grammar.assert_not_called()


def test_load_default_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes)
    mock_info = mocker.patch('PyQt6.QtWidgets.QMessageBox.information')

    dialog.combo_defaults.setCurrentIndex(1)

    dialog._load_default_grammar()

    presenter.load_default_grammar.assert_called_once_with("First-Order Logic (FOL)")
    mock_info.assert_called_once()


def test_load_profile_cancelled(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("", ""))
    dialog._load_profile()
    presenter.load_profile.assert_not_called()


def test_load_profile_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("my_grammar.json", ""))
    presenter.load_profile.return_value = (True, "Profile loaded!")
    mock_info = mocker.patch('PyQt6.QtWidgets.QMessageBox.information')

    dialog._load_profile()

    presenter.load_profile.assert_called_with("my_grammar.json")
    mock_info.assert_called_once()


def test_load_profile_failure(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("bad.json", ""))
    presenter.load_profile.return_value = (False, "Corrupted JSON")
    mock_crit = mocker.patch('PyQt6.QtWidgets.QMessageBox.critical')

    dialog._load_profile()
    mock_crit.assert_called_once()


def test_save_profile_cancelled(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("", ""))
    dialog._save_profile()
    presenter.save_profile.assert_not_called()


def test_save_profile_adds_extension_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("new_grammar", ""))
    presenter.save_profile.return_value = (True, "Saved!")
    mock_info = mocker.patch('PyQt6.QtWidgets.QMessageBox.information')

    dialog._save_profile()

    presenter.save_profile.assert_called_with("new_grammar.json")
    mock_info.assert_called_once()


def test_save_profile_with_extension_failure(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("new_grammar.json", ""))
    presenter.save_profile.return_value = (False, "Read-only system")
    mock_crit = mocker.patch('PyQt6.QtWidgets.QMessageBox.critical')

    dialog._save_profile()

    presenter.save_profile.assert_called_with("new_grammar.json")
    mock_crit.assert_called_once()
