from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from fitch_proof_checker.view import style
from fitch_proof_checker.view.proof_layout.proof_layout import setup_proof_layout
from fitch_proof_checker.view.menu_bar.menu_bar import setup_menu_bar


class FitchProofChecker(QMainWindow):
    def __init__(self, model):
        super().__init__()

        self.model = model

        self.zoom_level = 0
        self.setWindowTitle("Fitch Proof Checker")
        self.resize(600, 800)
        style.apply(self)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.global_layout = QVBoxLayout(central_widget)

        setup_menu_bar(self)
        setup_proof_layout(self)
        # TODO: complete UI
