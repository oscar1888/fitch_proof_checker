from PyQt6.QtWidgets import QHBoxLayout, QLabel, QFrame


def setup_logic_description(fpe_main_window):
    logic_layout = QHBoxLayout()

    logic_title = QLabel("Logic:")
    logic_title.setStyleSheet("font-weight: bold;")

    fpe_main_window.logic_label = QLabel("First Order Logic")

    logic_layout.addWidget(logic_title)
    logic_layout.addWidget(fpe_main_window.logic_label)
    logic_layout.addStretch()

    fpe_main_window.global_layout.addLayout(logic_layout)

    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Sunken)
    separator.setStyleSheet("color: #cccccc;")
    fpe_main_window.global_layout.addWidget(separator)
