from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen, QIcon, QFont

BASE_SIZE = 10
MIN_SIZE = 8
MAX_SIZE = 12

BASE_QLE_SIZE = 12


qle_font = QFont("Cambria Math", BASE_QLE_SIZE)

ARB_CONST_LABEL_STYLE = \
    """
        QLabel {
            border: 1px solid black;
            padding: 1px 4px;
            background-color: white;
            font-family: 'Cambria Math', serif;
            font-size: 14px;
        }
    """


def generate_app_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("#2c3e50"))

    painter = QPainter(pixmap)
    pen = QPen(QColor("#ecf0f1"))
    pen.setWidth(4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    painter.drawLine(20, 10, 20, 54)
    painter.drawLine(20, 26, 44, 26)

    painter.end()
    return QIcon(pixmap)


def apply(fpe_main_window):
    fpe_main_window.setStyleSheet("""    
    QLineEdit {
        border: none;
        border-bottom: 1px solid #ccc;
        background: transparent;
        padding: 6px 0;
        margin-bottom: 2px;
    }
    """)
