from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from fitch_proof_checker.view.fpe_line_edit.fpe_line_edit import FPELineEdit


class ProofLine(QWidget):
    def __init__(self, fpe_main_window, is_assump=False, depth=0):
        super().__init__()
        self.fpe_main_window = fpe_main_window
        self.is_assump = is_assump
        self.depth = depth

        self.OFFSET_FROM_NUM = 10
        self.INTERBAR_SPACE = 14
        self.TEXT_PADDING = 10

        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(10, 5, 10, 5)
        line_layout.setSpacing(5)

        self.line_number_label = QLabel("")
        self.line_number_label.setFixedWidth(25)
        line_layout.addWidget(self.line_number_label)

        bars_space = self.OFFSET_FROM_NUM + (max(0, self.depth) * self.INTERBAR_SPACE) + self.TEXT_PADDING
        line_layout.addSpacing(bars_space)

        self.formula_field = FPELineEdit(self, self.fpe_main_window)
        line_layout.addWidget(self.formula_field, stretch=8)

        line_layout.addStretch()

        if not self.is_assump:
            self.justification_field = FPELineEdit(self, self.fpe_main_window)
            line_layout.addWidget(self.justification_field, stretch=4)

    def paintEvent(self, event):
        from fitch_proof_checker.view.proof_layout.proof_layout import _get_premises

        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.black, 2, cap=Qt.PenCapStyle.SquareCap))

        start_x = self.line_number_label.geometry().right() + self.OFFSET_FROM_NUM
        last_x = start_x

        for i in range(self.depth + 1):
            last_x = start_x + (i * self.INTERBAR_SPACE)
            painter.drawLine(last_x, 15 if self.is_assump and i > 0 and i == self.depth else 0, last_x, self.height())

        glob_prem = _get_premises(self.fpe_main_window)

        if self.is_assump and (self == glob_prem[-1] or int(self.line_number_label.text()) > len(glob_prem)):
            y_base = self.formula_field.geometry().bottom() + 5
            painter.drawLine(last_x, y_base, last_x + 75, y_base)
