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
    file_path, _ = QFileDialog.getOpenFileName(fpe_main_window, "Open Proof File", "", "Proof Files (*.proof)")
    if file_path:
        with open(file_path, "r") as f:
            content = f.read()
            # TODO: parse file content and render in proof layout


def save(fpe_main_window):
    # TODO: implement this function
    pass


def save_as(fpe_main_window):
    # TODO: implement this function
    pass


def _can_quit(fpe_main_window):
    if fpe_main_window.edited:  # TODO: replace condition with "if not saved and edited or saved and saved serialization != actual serialization"
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
    if _can_quit(fpe_main_window):
        fpe_main_window.close()
