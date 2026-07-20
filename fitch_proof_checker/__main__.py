import sys
from PyQt6.QtWidgets import QApplication
from fitch_proof_checker.model import Model
from fitch_proof_checker.presenter import GMPresenter, LMPresenter, InputProofPresenter
from fitch_proof_checker.view import FitchProofChecker, GrammarManagerDialog, LogicManagerDialog, generate_app_icon


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(generate_app_icon())
    model = Model()
    grammar_manager = GrammarManager()
    logic_manager = LogicManager()
    window = FitchProofChecker(model, grammar_manager, logic_manager)
    window.show()
    sys.exit(app.exec())
