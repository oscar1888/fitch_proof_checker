from fitch_proof_checker.view.utils import add_action


def setup(fpe_main_window):
    edit_menu = fpe_main_window.menuBar().addMenu("Edit")
    action_data = [
        ("Undo", "undo", "Ctrl+z"),
        ("Redo", "redo", "Ctrl+y"),
        ("Cut", "cut", "Ctrl+x"),
        ("Copy", "copy", "Ctrl+c"),
        ("Paste", "paste", "Ctrl+v"),
        ("Clear", "clear", ""),
        ("Select All", "selectAll", ""),
    ]
    for name, fun_name, shortcut in action_data:
        add_action(fpe_main_window, edit_menu, name, edit_action(fun_name), shortcut)


def edit_action(action_name):
    def _act(fpe_main_window):
        widget = fpe_main_window.focusWidget()
        if hasattr(widget, action_name):
            getattr(widget, action_name)()
    return _act
