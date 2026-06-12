from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit

from fitch_proof_checker.view.utils.style import BASE_QLE_SIZE


class FPELineEdit(QLineEdit):
    def __init__(self, proof_line, fpe_main_window):
        super().__init__()
        self.fpe_main_window = fpe_main_window
        self.proof_line = proof_line
        font = QFont("Cambria Math")
        font.setItalic(True)
        font.setPointSize(BASE_QLE_SIZE)
        self.setFont(font)
        self.textEdited.connect(self._handle_first_edit)

    def _handle_first_edit(self, _):
        self.fpe_main_window.edited = True
        self.textEdited.disconnect(self._handle_first_edit)

    def keyPressEvent(self, event):
        from fitch_proof_checker.view.fpe_line_edit.utils import shortcuts_conds

        for cond, act in shortcuts_conds:
            if cond(event):
                act(self.fpe_main_window)
                return

        super().keyPressEvent(event)
