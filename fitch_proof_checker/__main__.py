import sys
from PyQt6.QtWidgets import QApplication
from fitch_proof_checker.model import Model
from fitch_proof_checker.view import FitchProofChecker


if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = Model()
    window = FitchProofChecker(model)
    window.show()
    sys.exit(app.exec())
