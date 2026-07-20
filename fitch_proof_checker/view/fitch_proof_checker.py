from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from fitch_proof_checker.view.menu_bar.file_menu import can_quit
from fitch_proof_checker.view.utils import style
from fitch_proof_checker.view.check_buttons import setup_check_buttons
from fitch_proof_checker.view.logic_description import setup_logic_description
from fitch_proof_checker.view.msg_box import setup_msg_box
from fitch_proof_checker.view.proof_layout import setup_proof_layout
from fitch_proof_checker.view.menu_bar import setup_menu_bar
from fitch_proof_checker.view.utils import add_separator


class FitchProofChecker(QMainWindow):
    def __init__(self):
        super().__init__()

        self.presenter = None
        self.current_file_path = None
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
        add_separator(self)
        setup_logic_description(self)
        add_separator(self)
        setup_proof_layout(self)
        setup_msg_box(self)

    def add_input_proof_presenter(self, presenter):
        self.presenter = presenter
        self.btn_check_step.clicked.connect(lambda: presenter.check_step())
        self.btn_check_proof.clicked.connect(lambda: presenter.check_proof())
        verify_line_action = next(
            a for m in self.menuBar().actions() if m.text() == "Proof" for a in m.menu().actions() if
            a.text() == "Verify Line"
        )
        verify_line_action.triggered.connect(presenter.check_step)
        verify_proof_action = next(
            a for m in self.menuBar().actions() if m.text() == "Proof" for a in m.menu().actions() if
            a.text() == "Verify Proof"
        )
        verify_proof_action.triggered.connect(presenter.check_proof)

    def closeEvent(self, event):
        if can_quit(self):
            event.accept()
        else:
            event.ignore()
