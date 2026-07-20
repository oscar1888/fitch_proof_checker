import sys
import json
import pytest
from PyQt6.QtWidgets import QMainWindow, QLabel, QMessageBox
from fitch_proof_checker.view.menu_bar.file_menu import (
    setup, open_new_window, open_proof_file, save, save_as, can_quit, quit_program
)


class DummyMainWindow(QMainWindow):
    def __init__(self, mocker):
        super().__init__()
        self.log_console = QLabel()
        self.current_file_path = None
        self.edited = False

        self.presenter = mocker.Mock()
        self.presenter.serialize_proof.return_value = {"proof": "data"}


@pytest.fixture
def fpe_window(qtbot, mocker):
    window = DummyMainWindow(mocker)
    qtbot.addWidget(window)
    return window


def test_setup_menu(fpe_window):
    setup(fpe_window)
    actions = fpe_window.menuBar().actions()[0].menu().actions()

    assert len(actions) == 5
    action_texts = [action.text() for action in actions]
    assert "New Window" in action_texts
    assert "Save As..." in action_texts


def test_open_new_window(mocker):
    mock_popen = mocker.patch('subprocess.Popen')
    open_new_window(None)

    mock_popen.assert_called_once_with([sys.executable] + sys.argv)


def test_open_proof_file_canceled(fpe_window, mocker):
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=("", ""))
    open_proof_file(fpe_window)

    assert fpe_window.current_file_path is None


def test_open_proof_file_success(fpe_window, mocker, tmp_path):
    test_file = tmp_path / "test.proof"
    valid_data = {"proof": "valid"}
    test_file.write_text(json.dumps(valid_data))

    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=(str(test_file), ""))

    open_proof_file(fpe_window)

    fpe_window.presenter.deserialize_proof.assert_called_once_with(valid_data)
    assert fpe_window.current_file_path == str(test_file)
    assert "successfully" in fpe_window.log_console.text()


def test_open_proof_file_exception(fpe_window, mocker, tmp_path):
    test_file = tmp_path / "test.proof"
    test_file.write_text("NOT A JSON")

    mocker.patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=(str(test_file), ""))

    open_proof_file(fpe_window)

    assert "Error loading file:" in fpe_window.log_console.text()
    fpe_window.presenter.deserialize_proof.assert_not_called()


def test_save_no_current_path_calls_save_as(fpe_window, mocker):
    fpe_window.current_file_path = None
    mock_save_as = mocker.patch('fitch_proof_checker.view.menu_bar.file_menu.save_as')

    save(fpe_window)

    mock_save_as.assert_called_once_with(fpe_window)


def test_save_success(fpe_window, tmp_path):
    test_file = tmp_path / "existing.proof"
    fpe_window.current_file_path = str(test_file)

    save(fpe_window)

    saved_data = json.loads(test_file.read_text())
    assert saved_data == {"proof": "data"}
    assert "File saved:" in fpe_window.log_console.text()


def test_save_exception(fpe_window, mocker, tmp_path):
    fpe_window.current_file_path = str(tmp_path / "dummy.proof")
    fpe_window.presenter.serialize_proof.side_effect = Exception("Serialization failed")

    save(fpe_window)

    assert "Error saving file: Serialization failed" in fpe_window.log_console.text()


def test_save_as_canceled(fpe_window, mocker):
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("", ""))

    save_as(fpe_window)

    assert fpe_window.current_file_path is None


def test_save_as_adds_extension(fpe_window, mocker, tmp_path):
    target_path = tmp_path / "new_file"
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=(str(target_path), ""))

    save_as(fpe_window)

    expected_path = str(target_path) + ".proof"
    assert fpe_window.current_file_path == expected_path
    assert "File saved as:" in fpe_window.log_console.text()


def test_save_as_existing_extension(fpe_window, mocker, tmp_path):
    target_path = tmp_path / "new_file.proof"
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=(str(target_path), ""))

    save_as(fpe_window)

    assert fpe_window.current_file_path == str(target_path)


def test_save_as_exception(fpe_window, mocker, tmp_path):
    target_path = tmp_path / "error_file.proof"
    mocker.patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=(str(target_path), ""))
    fpe_window.presenter.serialize_proof.side_effect = Exception("Write error")

    save_as(fpe_window)

    assert "Error saving file: Write error" in fpe_window.log_console.text()


def test_can_quit_no_file_no_edits(fpe_window):
    fpe_window.current_file_path = None
    fpe_window.edited = False
    assert can_quit(fpe_window) is True


def test_can_quit_unsaved_edited_user_says_yes(fpe_window, mocker):
    fpe_window.current_file_path = None
    fpe_window.edited = True
    mocker.patch('PyQt6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Yes)

    assert can_quit(fpe_window) is True


def test_can_quit_unsaved_edited_user_says_no(fpe_window, mocker):
    fpe_window.current_file_path = None
    fpe_window.edited = True
    mocker.patch('PyQt6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.No)

    assert can_quit(fpe_window) is False


def test_can_quit_saved_file_unchanged(fpe_window, tmp_path):
    test_file = tmp_path / "unchanged.proof"
    test_file.write_text(json.dumps({"proof": "data"}))
    fpe_window.current_file_path = str(test_file)

    assert can_quit(fpe_window) is True


def test_can_quit_saved_file_changed(fpe_window, tmp_path, mocker):
    test_file = tmp_path / "changed.proof"
    test_file.write_text(json.dumps({"proof": "OLD_DATA"}))
    fpe_window.current_file_path = str(test_file)

    mocker.patch('PyQt6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Yes)

    assert can_quit(fpe_window) is True


def test_can_quit_saved_file_read_error(fpe_window, mocker):
    fpe_window.current_file_path = "/percorso/che/non/esiste/affatto.proof"
    mocker.patch('PyQt6.QtWidgets.QMessageBox.warning', return_value=QMessageBox.StandardButton.Yes)

    assert can_quit(fpe_window) is True


def test_quit_program(fpe_window, mocker):
    spy = mocker.spy(fpe_window, 'close')
    quit_program(fpe_window)
    spy.assert_called_once()
