from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from fitch_proof_checker.view.menu_bar.file_menu import _can_quit
from fitch_proof_checker.view.utils import style
from fitch_proof_checker.view.check_buttons import setup_check_buttons
from fitch_proof_checker.view.logic_description import setup_logic_description
from fitch_proof_checker.view.msg_box import setup_msg_box
from fitch_proof_checker.view.proof_layout.proof_layout import setup_proof_layout
from fitch_proof_checker.view.menu_bar.menu_bar import setup_menu_bar


class FitchProofChecker(QMainWindow):
    def __init__(self, model):
        super().__init__()

        self.model = model

        self.zoom_level = 0
        self.edited = False
        self.setWindowTitle("Fitch Proof Checker")
        self.resize(600, 800)
        style.apply(self)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.global_layout = QVBoxLayout(central_widget)
        self.global_layout.setSpacing(10)

        setup_menu_bar(self)
        setup_check_buttons(self)
        setup_logic_description(self)
        setup_proof_layout(self)
        setup_msg_box(self)

    def closeEvent(self, event):
        if _can_quit(self):
            event.accept()
        else:
            event.ignore()
