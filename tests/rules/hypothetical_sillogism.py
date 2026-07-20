from fitch_proof_checker.model.formula.connective import Implies
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "HypSill"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2:
            return False

        if isinstance(actual_premises[0], Subproof) or isinstance(actual_premises[1], Subproof):
            return False

        p1, p2 = actual_premises

        if type(p1) is not Implies or type(p2) is not Implies:
            return False

        if type(actual_conclusion) is not Implies:
            return False

        if p1.args[1] == p2.args[0]:
            expected_left = p1.args[0]
            expected_right = p2.args[1]
        elif p2.args[1] == p1.args[0]:
            expected_left = p2.args[0]
            expected_right = p1.args[1]
        else:
            return False

        return actual_conclusion.args[0] == expected_left and actual_conclusion.args[1] == expected_right
