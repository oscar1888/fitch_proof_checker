import subprocess
import sys
from PyQt6.QtWidgets import QFileDialog
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


def quit_program(fpe_main_window):
    # TODO: implement "Changes will not be saved. Are you sure?" dialog in case of nonempty proof
    fpe_main_window.close()
