from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from fitch_proof_checker.view.fpe_line_edit import FPELineEdit
from fitch_proof_checker.view.utils import create_status_dot

OFFSET_FROM_NUM = 10
INTERBAR_SPACE = 14
TEXT_PADDING = 10


class ProofLine(QWidget):
    def __init__(self, fpe_main_window, is_assump=False, depth=0):
        super().__init__()
        self.fpe_main_window = fpe_main_window
        self.is_assump = is_assump
        self.arb_consts_introduced = []
        self.depth = depth

        line_layout = QHBoxLayout(self)
        line_layout.setContentsMargins(10, 5, 10, 5)
        line_layout.setSpacing(5)

        self.line_number_label = QLabel("")
        self.line_number_label.setFixedWidth(25)
        line_layout.addWidget(self.line_number_label)

        bars_space = OFFSET_FROM_NUM + self.depth * INTERBAR_SPACE + TEXT_PADDING
        line_layout.addSpacing(bars_space)

        self.formula_field = FPELineEdit(self, self.fpe_main_window)
        line_layout.addWidget(self.formula_field, stretch=8)

        line_layout.addStretch()

        if not self.is_assump:
            self.justification_field = FPELineEdit(self, self.fpe_main_window)
            line_layout.addWidget(self.justification_field, stretch=4)

            self.status_dot = create_status_dot()
            line_layout.addWidget(self.status_dot)

    def paintEvent(self, event):
        from fitch_proof_checker.view.proof_layout.proof_layout import get_premises

        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.black, 2, cap=Qt.PenCapStyle.SquareCap))

        start_x = self.line_number_label.geometry().right() + OFFSET_FROM_NUM
        last_x = start_x

        for i in range(self.depth + 1):
            last_x = start_x + (i * INTERBAR_SPACE)
            painter.drawLine(last_x, 15 if self.is_assump and i > 0 and i == self.depth else 0, last_x, self.height())

        glob_prem = get_premises(self.fpe_main_window)

        if self.is_assump and (self == glob_prem[-1] or int(self.line_number_label.text()) > len(glob_prem)):
            y_base = self.formula_field.geometry().bottom() + 5
            painter.drawLine(last_x, y_base, last_x + 75, y_base)
