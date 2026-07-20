from PyQt6.QtWidgets import QTextEdit, QLabel


def setup_msg_box(fpe_main_window):
    log_label = QLabel("Info:")
    log_label.setStyleSheet("font-weight: bold; color: #333;")
    fpe_main_window.global_layout.addWidget(log_label)
    fpe_main_window.log_console = QTextEdit()
    fpe_main_window.log_console.setReadOnly(True)
    fpe_main_window.log_console.setMaximumHeight(80)
    fpe_main_window.log_console.setStyleSheet("background-color: #f5f5f5; color: #555555; font-family: monospace;")
    fpe_main_window.global_layout.addWidget(fpe_main_window.log_console)
