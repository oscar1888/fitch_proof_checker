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
    fpe_main_window.gmd.tabs.setCurrentIndex(0)
    fpe_main_window.gmd.list_quantifiers.clearSelection()
    fpe_main_window.gmd.list_quantifiers.setCurrentRow(-1)
    fpe_main_window.gmd.list_quantifiers.clearFocus()
    fpe_main_window.gmd.list_connectives.clearSelection()
    fpe_main_window.gmd.list_connectives.setCurrentRow(-1)
    fpe_main_window.gmd.list_connectives.clearFocus()
    fpe_main_window.gmd.combo_defaults.setCurrentIndex(0)
    fpe_main_window.gmd.exec()


def manage_rule_set(fpe_main_window):
    fpe_main_window.lmd.rule_list.clearSelection()
    fpe_main_window.lmd.rule_list.setCurrentRow(-1)
    fpe_main_window.lmd.rule_list.clearFocus()
    fpe_main_window.lmd.combo_defaults.setCurrentIndex(0)
    fpe_main_window.lmd.exec()
