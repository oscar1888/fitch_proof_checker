import os
import re
import pytest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence
from fitch_proof_checker.model import Model
from fitch_proof_checker.presenter import InputProofPresenter, GMPresenter, LMPresenter
from fitch_proof_checker.view import FitchProofChecker, GrammarManagerDialog, LogicManagerDialog
from fitch_proof_checker.view.proof_layout import get_all_lines

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


class UIRobot:
    def __init__(self, window, default_delay=500):
        self.window = window
        self.delay = default_delay

    def press_shortcut(self, shortcut: str):
        QTest.qWait(self.delay)
        QTest.keySequence(self.window, QKeySequence(shortcut))
        QTest.qWait(self.delay)

    def click(self, widget):
        QTest.qWait(self.delay)
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton)
        QTest.qWait(self.delay)

    def type_text(self, widget, text: str):
        QTest.qWait(self.delay)
        QTest.keyClicks(widget, text)
        QTest.qWait(self.delay)


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class TestFitchProofChecker:

    def setup_method(self):
        self.main_window = FitchProofChecker()
        self.gmd = GrammarManagerDialog(self.main_window)
        self.lmd = LogicManagerDialog(self.main_window)

        self.model = Model()

        self.ipp = InputProofPresenter(self.main_window, self.model)
        self.gmp = GMPresenter(self.gmd, self.model)
        self.lmp = LMPresenter(self.lmd, self.model)

        self.main_window.show()
        QTest.qWaitForWindowExposed(self.main_window)

        self.robot = UIRobot(self.main_window, default_delay=250)

    def teardown_method(self):
        self.main_window.close()

    def test_open_and_save_as(self, qapp):
        original_path = os.path.join(TEST_DIR, "proofs", "dummy1.proof")
        save_path = os.path.join(TEST_DIR, "proofs", "dummy2.proof")

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(original_path, "Proof Files (*.proof)")):
            self.robot.press_shortcut("Ctrl+O")

        lines = get_all_lines(self.main_window)
        lines[-1].formula_field.setFocus()
        self.robot.press_shortcut("Ctrl+P")
        with patch('PyQt6.QtWidgets.QInputDialog.getText', return_value=("a", True)):
            self.robot.press_shortcut("Ctrl+T")
        lines = get_all_lines(self.main_window)
        self.robot.type_text(lines[-1].formula_field, "P(a)")
        self.robot.press_shortcut("Ctrl+A")
        lines = get_all_lines(self.main_window)
        self.robot.type_text(lines[-1].formula_field, "Q(a)")

        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=(save_path, "Proof Files (*.proof)")):
            next(
                a for m in self.main_window.menuBar().actions() if m.text() == "File" for a in m.menu().actions() if
                a.text() == "Save As..."
            ).trigger()

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(original_path, "Proof Files (*.proof)")):
            self.robot.press_shortcut("Ctrl+O")

        lines_dummy1 = get_all_lines(self.main_window)

        assert len(lines_dummy1) == 4
        assert lines_dummy1[0].formula_field.text() == "∀x (P(x) → Q(x))"
        assert lines_dummy1[1].formula_field.text() == "P(a)"
        assert lines_dummy1[2].formula_field.text() == "P(a) → Q(a)"
        assert lines_dummy1[3].formula_field.text() == "Q(a)"

        assert all(line.depth == 0 for line in lines_dummy1)

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(save_path, "Proof Files (*.proof)")):
            self.robot.press_shortcut("Ctrl+O")

        lines_dummy2 = get_all_lines(self.main_window)

        assert len(lines_dummy2) == 6

        assert lines_dummy2[0].formula_field.text() == "∀x (P(x) → Q(x))"
        assert lines_dummy2[3].formula_field.text() == "Q(a)"

        assert lines_dummy2[4].formula_field.text() == "P(a)"
        assert lines_dummy2[4].depth == 1

        assert "a" in lines_dummy2[4].arb_consts_introduced
        assert lines_dummy2[4].is_assump is True

        assert lines_dummy2[5].formula_field.text() == "Q(a)"
        assert lines_dummy2[5].depth == 1
        assert lines_dummy2[5].is_assump is False

    def test_all_fol_rules(self, qapp):
        original_path = os.path.join(TEST_DIR, "proofs", "all_fol_rules.proof")

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(original_path, "Proof Files (*.proof)")):
            self.robot.press_shortcut("Ctrl+O")

        lines = get_all_lines(self.main_window)
        lines[5].formula_field.setFocus()
        self.robot.press_shortcut("Ctrl+L")

        stylesheet = lines[5].status_dot.styleSheet().lower()

        match_background = re.search(r'background-color\s*:\s*#2ecc71', stylesheet)

        assert match_background is not None

        self.robot.press_shortcut("Ctrl+F")

        for i, line in enumerate(lines):
            if hasattr(line, 'status_dot'):
                stylesheet_proof = line.status_dot.styleSheet().lower()
                match_proof_bg = re.search(r'background-color\s*:\s*#2ecc71', stylesheet_proof)

                assert match_proof_bg is not None

        stylesheet_proof = self.main_window.goal_status_dot.styleSheet().lower()
        match_proof_bg = re.search(r'background-color\s*:\s*#2ecc71', stylesheet_proof)
        assert match_proof_bg is not None

    def test_extra_rules(self, qapp):
        rules = [
            "and_idemp.py",
            "contraposition.py",
            "de_morgan.py",
            "disjunctive_sillogism.py",
            "excluded_middle.py",
            "hypothetical_sillogism.py",
            "material_implication.py",
            "modus_tollens.py",
            "or_idemp.py",
            "quantifier_exchange.py",
            "rename_var.py"
        ]

        for rule in rules:
            with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                       return_value=(os.path.join(TEST_DIR, "rules", rule), "Proof Files (*.proof)")), \
                    patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
                self.lmd.btn_add.click()

        original_path = os.path.join(TEST_DIR, "proofs", "extra_rules.proof")

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(original_path, "Proof Files (*.proof)")):
            self.robot.press_shortcut("Ctrl+O")

        self.robot.press_shortcut("Ctrl+F")

        lines = get_all_lines(self.main_window)
        for i, line in enumerate(lines):
            if hasattr(line, 'status_dot'):
                stylesheet_proof = line.status_dot.styleSheet().lower()
                match_proof_bg = re.search(r'background-color\s*:\s*#2ecc71', stylesheet_proof)

                assert match_proof_bg is not None

        self.lmd.rule_list.setCurrentRow(29)
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
            self.lmd.btn_remove.click()

        assert self.lmd.rule_list.count() == 29

        remaining_items = [self.lmd.rule_list.item(i).text() for i in range(self.lmd.rule_list.count())]
        assert not any("RenameVar" in item for item in remaining_items)

        rule_names = [r.name for r in self.model.logic_manager.rules]
        assert "RenameVar" not in rule_names

    def test_xor(self, qapp):
        rules = [
            "xor_intro.py",
            "xor_elim.py"
        ]

        for rule in rules:
            with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                       return_value=(os.path.join(TEST_DIR, "rules", rule), "Proof Files (*.proof)")), \
                    patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
                self.lmd.btn_add.click()

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(os.path.join(TEST_DIR, "grammar", "xor.py"), "Proof Files (*.proof)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.gmd.btn_add_conn.click()

        original_path = os.path.join(TEST_DIR, "proofs", "xor.proof")

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(original_path, "Proof Files (*.proof)")):
            self.robot.press_shortcut("Ctrl+O")

        self.robot.press_shortcut("Ctrl+F")

        lines = get_all_lines(self.main_window)
        for i, line in enumerate(lines):
            if hasattr(line, 'status_dot'):
                stylesheet_proof = line.status_dot.styleSheet().lower()
                match_proof_bg = re.search(r'background-color\s*:\s*#2ecc71', stylesheet_proof)

                assert match_proof_bg is not None

        self.gmd.list_connectives.setCurrentRow(6)
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
            self.gmd.btn_remove_conn.click()

        assert self.gmd.list_connectives.count() == 6
        remaining_items = [self.gmd.list_connectives.item(i).text() for i in range(self.gmd.list_connectives.count())]
        assert not any("Xor" in item for item in remaining_items)

        connective_names = [c.name for c in self.model.grammar_manager.connectives]
        assert "Xor" not in connective_names

    def test_exists_unique(self, qapp):
        rules = [
            "exists_unique_intro.py",
            "exists_unique_elim.py"
        ]

        for rule in rules:
            with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                       return_value=(os.path.join(TEST_DIR, "rules", rule), "Proof Files (*.proof)")), \
                    patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
                self.lmd.btn_add.click()

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(os.path.join(TEST_DIR, "grammar", "exists_unique.py"), "Proof Files (*.proof)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.gmd.btn_add_quant.click()

        original_path = os.path.join(TEST_DIR, "proofs", "exists_unique.proof")

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(original_path, "Proof Files (*.proof)")):
            self.robot.press_shortcut("Ctrl+O")

        self.robot.press_shortcut("Ctrl+F")

        lines = get_all_lines(self.main_window)
        for i, line in enumerate(lines):
            if hasattr(line, 'status_dot'):
                stylesheet_proof = line.status_dot.styleSheet().lower()
                match_proof_bg = re.search(r'background-color\s*:\s*#2ecc71', stylesheet_proof)

                assert match_proof_bg is not None

        self.gmd.list_quantifiers.setCurrentRow(2)
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
            self.gmd.btn_remove_quant.click()

        assert self.gmd.list_quantifiers.count() == 2

        remaining_items = [self.gmd.list_quantifiers.item(i).text() for i in range(self.gmd.list_quantifiers.count())]
        assert not any("ExistsUnique" in item for item in remaining_items)

        quantifier_names = [q.name for q in self.model.grammar_manager.quantifiers]
        assert "ExistsUnique" not in quantifier_names

    def test_load_save_grammar(self, qapp):
        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(os.path.join(TEST_DIR, "grammar", "xor.py"), "Python Files (*.py)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.gmd.btn_add_conn.click()

        assert self.gmd.list_connectives.count() == 7

        save_path = os.path.join(TEST_DIR, "grammar", "test_grammar.json")
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName',
                   return_value=(save_path, "JSON Files (*.json)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.gmd.btn_save_profile.click()

        assert os.path.exists(save_path)

        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.gmd.btn_load_default.click()

        assert self.gmd.list_connectives.count() == 6
        remaining_items = [self.gmd.list_connectives.item(i).text() for i in range(self.gmd.list_connectives.count())]
        assert not any("Xor" in item for item in remaining_items)

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(save_path, "JSON Files (*.json)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.gmd.btn_load_profile.click()

        assert self.gmd.list_connectives.count() == 7
        restored_items = [self.gmd.list_connectives.item(i).text() for i in range(self.gmd.list_connectives.count())]
        assert any("Xor" in item for item in restored_items)

        if os.path.exists(save_path):
            os.remove(save_path)

    def test_load_save_logic(self, qapp):
        initial_rule_count = self.lmd.rule_list.count()

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(os.path.join(TEST_DIR, "rules", "xor_intro.py"), "Python Files (*.py)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.lmd.btn_add.click()

        assert self.lmd.rule_list.count() == initial_rule_count + 1

        save_path = os.path.join(TEST_DIR, "rules", "test_logic.json")
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName',
                   return_value=(save_path, "JSON Files (*.json)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.lmd.btn_save_as.click()

        assert os.path.exists(save_path)

        self.lmd.combo_defaults.setCurrentIndex(1)
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.lmd.btn_load_default.click()

        assert self.lmd.rule_list.count() == initial_rule_count
        remaining_items = [self.lmd.rule_list.item(i).text() for i in range(self.lmd.rule_list.count())]
        assert not any("XorIntro" in item for item in remaining_items)

        with patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName',
                   return_value=(save_path, "JSON Files (*.json)")), \
                patch('PyQt6.QtWidgets.QMessageBox.information', return_value=QMessageBox.StandardButton.Ok):
            self.lmd.btn_load.click()

        assert self.lmd.rule_list.count() == initial_rule_count + 1
        restored_items = [self.lmd.rule_list.item(i).text() for i in range(self.lmd.rule_list.count())]
        assert any("XorIntro" in item for item in restored_items)

        if os.path.exists(save_path):
            os.remove(save_path)
