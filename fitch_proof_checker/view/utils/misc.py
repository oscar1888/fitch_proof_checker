from PyQt6.QtGui import QAction, QKeySequence


def add_action(fpe_main_window, menu, name, action, shortcut):
    new_action = QAction(name, fpe_main_window)
    new_action.triggered.connect(lambda: action(fpe_main_window))
    if shortcut:
        new_action.setShortcut(QKeySequence(shortcut))
    menu.addAction(new_action)
