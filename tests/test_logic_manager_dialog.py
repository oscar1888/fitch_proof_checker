import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QMessageBox
from fitch_proof_checker.view.logic_manager_dialog import LogicManagerDialog


class DummyParent(QWidget):
    pass


@pytest.fixture
def setup_dialog(qtbot, mocker):
    parent = DummyParent()
    dialog = LogicManagerDialog(parent)
    dialog._keep_parent_alive = parent

    mocker.patch('PyQt6.QtWidgets.QMessageBox.information')
    mocker.patch('PyQt6.QtWidgets.QMessageBox.warning')
    mocker.patch('PyQt6.QtWidgets.QMessageBox.critical')
    mocker.patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes)

    qtbot.addWidget(dialog)
    presenter_mock = mocker.Mock()
    dialog.add_presenter(presenter_mock)

    return dialog, presenter_mock


def test_bottom_buttons_signals(setup_dialog, qtbot, mocker):
    dialog, _ = setup_dialog

    mock_load_def = mocker.patch.object(dialog, '_load_default_logic')
    mock_add = mocker.patch.object(dialog, '_add_rule')
    mock_remove = mocker.patch.object(dialog, '_remove_rule')
    mock_load = mocker.patch.object(dialog, '_load_logic')
    mock_save = mocker.patch.object(dialog, '_save_logic')

    buttons_config = [
        (dialog.btn_load_default, mock_load_def),
        (dialog.btn_add, mock_add),
        (dialog.btn_remove, mock_remove),
        (dialog.btn_load, mock_load),
        (dialog.btn_save_as, mock_save)
    ]

    for btn, mock in buttons_config:
        btn.clicked.disconnect()
        btn.clicked.connect(mock)

        qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
        mock.assert_called_once()


def test_remove_rule_no_selection(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mock_warn = mocker.patch('PyQt6.QtWidgets.QMessageBox.warning')

    dialog._remove_rule()

    mock_warn.assert_called_once()
    presenter.remove_rule.assert_not_called()


def test_remove_rule_success(setup_dialog):
    dialog, presenter = setup_dialog
    dialog.rule_list.addItem("AndElim")
    dialog.rule_list.setCurrentRow(0)

    dialog._remove_rule()
    presenter.remove_rule.assert_called_once_with(0)


def test_load_default_logic(setup_dialog):
    dialog, presenter = setup_dialog
    dialog.combo_defaults.setCurrentIndex(0)

    dialog._load_default_logic()
    presenter.load_default_logic.assert_called_once_with("Propositional Logic (PL)")


def test_add_rule_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("rule.py", ""))
    presenter.add_rule.return_value = (True, "Success")

    dialog._add_rule()
    presenter.add_rule.assert_called_once_with("rule.py")


def test_add_rule_failure(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("bad.py", ""))
    presenter.add_rule.return_value = (False, "Error")
    mock_crit = mocker.patch('PyQt6.QtWidgets.QMessageBox.critical')

    dialog._add_rule()
    mock_crit.assert_called_once()


def test_load_logic_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("logic.json", ""))
    presenter.load_profile.return_value = (True, "Loaded")

    dialog._load_logic()
    presenter.load_profile.assert_called_once_with("logic.json")


def test_save_logic_success(setup_dialog, mocker):
    dialog, presenter = setup_dialog
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("save", ""))
    presenter.save_profile.return_value = (True, "Saved")

    dialog._save_logic()
    presenter.save_profile.assert_called_once_with("save.json")
