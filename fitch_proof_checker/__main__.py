import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from fitch_proof_checker.view.menu_bar.menu_bar import setup_menu_bar
from fitch_proof_checker.view.proof_layout.proof_layout import setup_proof_layout


class FitchProofChecker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.windows = []
        self.zoom_level = 0
        self.setWindowTitle("Fitch Proof Checker")
        self.resize(600, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.global_layout = QVBoxLayout(central_widget)

        setup_menu_bar(self)
        setup_proof_layout(self)
        # TODO: complete UI


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FitchProofChecker()
    window.show()
    sys.exit(app.exec())
