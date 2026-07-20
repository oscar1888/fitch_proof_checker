import sys
from PyQt6.QtWidgets import QApplication
from fitch_proof_checker.model import Model
from fitch_proof_checker.presenter import GMPresenter, LMPresenter, InputProofPresenter
from fitch_proof_checker.view import FitchProofChecker, GrammarManagerDialog, LogicManagerDialog, generate_app_icon


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(generate_app_icon())
    window = FitchProofChecker()
    gmd = GrammarManagerDialog(window)
    lmd = LogicManagerDialog(window)

    model = Model()

    InputProofPresenter(window, model)
    GMPresenter(gmd, model)
    LMPresenter(lmd, model)

    window.show()
    sys.exit(app.exec())
