from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel

from fitch_proof_checker.view.proof_layout.fpe_line_edit import FPELineEdit


class ProofLine(QWidget):
    def __init__(self, fpe_main_window, is_premise=False, depth=0):
        super().__init__()
        self.fpe_main_window = fpe_main_window
        self.is_premise = is_premise
        self.depth = depth

        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(10, 5, 10, 5)
        line_layout.setSpacing(15)
        self.line_number_label = QLabel("")
        self.line_number_label.setFixedWidth(25)
        line_layout.addWidget(self.line_number_label)

        self.formula_field = FPELineEdit(self, self.fpe_main_window)

        line_layout.addSpacing(10)
        line_layout.addWidget(self.formula_field, stretch=8)
        line_layout.addStretch()
        if not self.is_premise:
            self.justification_field = FPELineEdit(self, self.fpe_main_window)
            line_layout.addWidget(self.justification_field, stretch=4)

    def paintEvent(self, event):
        from fitch_proof_checker.view.proof_layout.proof_layout import _get_premises

        painter = QPainter(self)

        pen = QPen(Qt.GlobalColor.black, 2)
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        painter.setPen(pen)

        num_right = self.line_number_label.geometry().right()
        formula_left = self.formula_field.geometry().left()
        x_line = (num_right + formula_left) // 2

        y_base = self.formula_field.geometry().bottom() + 5

        painter.drawLine(x_line, 0, x_line, y_base)

        if self.is_premise and self == _get_premises(self.fpe_main_window)[-1]:
            painter.drawLine(x_line, y_base, x_line + 100, y_base)
