from fitch_proof_checker.view.grammar_manager_dialog import \
    GrammarManagerDialog
from fitch_proof_checker.view.logic_manager_dialog import LogicManagerDialog
from fitch_proof_checker.view.utils import add_action


def setup(fpe_main_window):
    logic_menu = fpe_main_window.menuBar().addMenu("Logic")
    action_data = [
        ("Manage grammar", manage_grammar, ""),
        ("Manage rule set", manage_rule_set, ""),
    ]
    for name, fun, shortcut in action_data:
        add_action(fpe_main_window, logic_menu, name, fun, shortcut)


def manage_grammar(fpe_main_window):
    GrammarManagerDialog(fpe_main_window.grammar_manager, fpe_main_window).exec()


def manage_rule_set(fpe_main_window):
    LogicManagerDialog(fpe_main_window.logic_manager, fpe_main_window).exec()
