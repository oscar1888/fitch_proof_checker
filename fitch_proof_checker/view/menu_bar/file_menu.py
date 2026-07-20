import json
import subprocess
import sys
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from fitch_proof_checker.view.utils import add_action


def setup(fpe_main_window):
    file_menu = fpe_main_window.menuBar().addMenu("File")
    action_data = [
        ("New Window", open_new_window, "Ctrl+n"),
        ("Open", open_proof_file, "Ctrl+o"),
        ("Save", save, "Ctrl+s"),
        ("Save As...", save_as, ""),
        ("Quit", quit_program, "Ctrl+q"),
    ]
    for name, fun, shortcut in action_data:
        add_action(fpe_main_window, file_menu, name, fun, shortcut)


def open_new_window(_):
    subprocess.Popen([sys.executable] + sys.argv)


def open_proof_file(fpe_main_window):
    file_path, _ = QFileDialog.getOpenFileName(fpe_main_window, "Open Proof File", "",
                                               "Proof Files (*.proof);;All Files (*)")
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                proof_data = json.load(f)

            fpe_main_window.presenter.deserialize_proof(proof_data)

            fpe_main_window.current_file_path = file_path
            fpe_main_window.log_console.setText(f"File loaded successfully: {file_path}")
        except Exception as e:
            fpe_main_window.log_console.setText(f"Error loading file: {str(e)}")


def save(fpe_main_window):
    if fpe_main_window.current_file_path:
        try:
            proof_data = fpe_main_window.presenter.serialize_proof()

            with open(fpe_main_window.current_file_path, "w", encoding="utf-8") as f:
                json.dump(proof_data, f, indent=4)

            fpe_main_window.log_console.setText(f"File saved: {fpe_main_window.current_file_path}")
        except Exception as e:
            fpe_main_window.log_console.setText(f"Error saving file: {str(e)}")
    else:
        save_as(fpe_main_window)


def save_as(fpe_main_window):
    file_path, _ = QFileDialog.getSaveFileName(fpe_main_window, "Save Proof As", "",
                                               "Proof Files (*.proof);;All Files (*)")
    if file_path:
        if not file_path.endswith('.proof'):
            file_path += '.proof'

        try:
            proof_data = fpe_main_window.presenter.serialize_proof()

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(proof_data, f, indent=4)

            fpe_main_window.current_file_path = file_path
            fpe_main_window.log_console.setText(f"File saved as: {file_path}")
        except Exception as e:
            fpe_main_window.log_console.setText(f"Error saving file: {str(e)}")


def can_quit(fpe_main_window):
    is_saved = bool(fpe_main_window.current_file_path)

    has_unsaved_changes = False

    if not is_saved and fpe_main_window.edited:
        has_unsaved_changes = True
    elif is_saved:
        try:
            with open(fpe_main_window.current_file_path, "r", encoding="utf-8") as f:
                saved_data = json.load(f)

            actual_data = fpe_main_window.presenter.serialize_proof()

            if saved_data != actual_data:
                has_unsaved_changes = True
        except Exception:
            has_unsaved_changes = True

    if has_unsaved_changes:
        res = QMessageBox.warning(
            fpe_main_window,
            "Warning",
            "Changes will not be saved. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        return res == QMessageBox.StandardButton.Yes

    return True


def quit_program(fpe_main_window):
    fpe_main_window.close()
