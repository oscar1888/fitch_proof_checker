from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit
from fitch_proof_checker.view.style import BASE_QLE_SIZE


class FPELineEdit(QLineEdit):
    def __init__(self, proof_line, fpe_main_window):
        super().__init__()
        self.fpe_main_window = fpe_main_window
        self.proof_line = proof_line
        font = QFont()
        font.setPointSize(BASE_QLE_SIZE)
        self.setFont(font)

    def keyPressEvent(self, event):
        from fitch_proof_checker.view.proof_layout.proof_layout import add_step_after

        if event.key() == Qt.Key.Key_A and (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            add_step_after(self.fpe_main_window)
            return
        super().keyPressEvent(event)
