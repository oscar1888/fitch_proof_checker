from PyQt6.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from fitch_proof_checker.view.fpe_line_edit.utils import symbol_map

type_style = """
    QLabel {
        font-family: Consolas, monospace;
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        padding: 3px 6px;
        border-radius: 3px;
        color: #198754;
    }
"""

key_style = """
    QLabel {
        font-weight: bold;
        background-color: #e9ecef;
        border: 1px solid #adb5bd;
        border-bottom: 2px solid #6c757d;
        padding: 3px 8px;
        border-radius: 4px;
        color: #212529;
    }
"""


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Special symbols shortcuts")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        grid = QGridLayout()
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(20)

        for row, (shortcut, info) in enumerate(symbol_map.items()):
            desc = f'{info[0]} ({info[1]})'
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("font-size: 13px;")

            key_layout = QHBoxLayout()
            key_layout.setContentsMargins(0, 0, 0, 0)
            key_layout.setSpacing(6)

            if shortcut.endswith(" "):
                typed_text = shortcut[:-1]
                has_space = True
            else:
                typed_text = shortcut
                has_space = False

            type_label = QLabel(typed_text)
            type_label.setStyleSheet(type_style)
            key_layout.addWidget(type_label)

            if has_space:
                plus_label = QLabel("+")
                key_layout.addWidget(plus_label)

                space_key = QLabel("Space")
                space_key.setStyleSheet(key_style)
                key_layout.addWidget(space_key)

            key_layout.addStretch()

            k_widget = QWidget()
            k_widget.setLayout(key_layout)

            grid.addWidget(desc_label, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(k_widget, row, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addLayout(grid)
