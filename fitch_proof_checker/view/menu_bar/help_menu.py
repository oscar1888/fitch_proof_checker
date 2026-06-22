from fitch_proof_checker.view.menu_bar.shortcuts_dialog import ShortcutsDialog
from fitch_proof_checker.view.utils import add_action


def setup(fpe_main_window):
    help_menu = fpe_main_window.menuBar().addMenu("Help")
    action_data = [
        ("Special symbols shortcuts", show_shortcuts_dialog, ""),
    ]
    for name, fun, shortcut in action_data:
        add_action(fpe_main_window, help_menu, name, fun, shortcut)


def show_shortcuts_dialog(fpe_main_window):
    dialog = ShortcutsDialog(fpe_main_window)
    dialog.exec()
