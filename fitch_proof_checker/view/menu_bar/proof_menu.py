from fitch_proof_checker.view.proof_layout.proof_layout import add_premise, add_step_after, add_step_before, \
    delete_step, new_subproof, end_subproof, edit_goal, verify_line, verify_proof, new_arbitary_constant, \
    delete_arbitrary_constant
from fitch_proof_checker.view.utils import add_action


def setup(fpe_main_window):
    proof_menu = fpe_main_window.menuBar().addMenu("Proof")
    action_data = [
        ("Add Premise", add_premise, "Ctrl+r"),
        ("Add Step After", add_step_after, "Ctrl+a"),
        ("Add Step Before", add_step_before, "Ctrl+b"),
        ("Delete Step", delete_step, "Ctrl+d"),
        ("New Subproof", new_subproof, "Ctrl+p"),
        ("End Subproof", end_subproof, "Ctrl+e"),
        ("New arbitrary constant", new_arbitary_constant, "Ctrl+t"),
        ("Delete arbitrary constant", delete_arbitrary_constant, "Ctrl+i"),
        ("Edit Goal", edit_goal, "Ctrl+g"),
        ("Verify Line", verify_line, "Ctrl+l"),
        ("Verify Proof", verify_proof, "Ctrl+f"),
    ]
    for name, fun, shortcut in action_data:
        add_action(fpe_main_window, proof_menu, name, fun, shortcut)
