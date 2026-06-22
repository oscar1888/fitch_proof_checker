from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QFrame, QLabel


def add_action(fpe_main_window, menu, name, action, shortcut):
    new_action = QAction(name, fpe_main_window)
    new_action.triggered.connect(lambda: action(fpe_main_window))
    if shortcut:
        new_action.setShortcut(QKeySequence(shortcut))
    menu.addAction(new_action)


def create_status_dot():
    status_dot = QLabel()
    status_dot.setFixedSize(12, 12)
    status_dot.setToolTip("Not yet verified")
    set_status(status_dot, None)
    return status_dot


def _set_dot_color(status_dot, color_hex):
    status_dot.setStyleSheet(f"""
        QLabel {{
            min-width: 12px;
            max-width: 12px;
            min-height: 12px;
            max-height: 12px;
            background-color: {color_hex};
            border-radius: 6px;
            margin-left: 5px;
        }}
    """)


def set_status(status_dot, is_valid):
    if is_valid:
        _set_dot_color(status_dot, "#2ecc71")
        status_dot.setToolTip("Correct")
    elif is_valid == False:
        _set_dot_color(status_dot, "#e74c3c")
        status_dot.setToolTip("Error on justification")
    else:
        _set_dot_color(status_dot, "#cccccc")
        status_dot.setToolTip("Not yet verified")


def add_separator(fpe_main_window):
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Sunken)
    separator.setStyleSheet("color: #cccccc;")
    fpe_main_window.global_layout.addWidget(separator)
