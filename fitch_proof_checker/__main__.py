import sys

from PyQt6.QtWidgets import QApplication
from fitch_proof_checker.model import Model
from fitch_proof_checker.model.grammar_manager.grammar_manager import GrammarManager
from fitch_proof_checker.model.logic_manager.logic_manager import LogicManager
from fitch_proof_checker.view import FitchProofChecker
from fitch_proof_checker.view.utils import generate_app_icon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(generate_app_icon())
    model = Model()
    grammar_manager = GrammarManager()
    logic_manager = LogicManager()
    window = FitchProofChecker(model, grammar_manager, logic_manager)
    window.show()
    sys.exit(app.exec())
