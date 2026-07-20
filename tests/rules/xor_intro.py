from fitch_proof_checker.model.formula.connective import Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "XorIntro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2:
            return False

        if isinstance(actual_premises[0], Subproof) or isinstance(actual_premises[1], Subproof):
            return False

        if (type(actual_conclusion).__name__ != "CustomConnective"
                or actual_conclusion.name != "Xor" or len(actual_conclusion.args) != 2):
            return False

        p1, p2 = actual_premises
        left_node = actual_conclusion.args[0]
        right_node = actual_conclusion.args[1]

        if (p1 == left_node and p2 == Not(right_node)) or \
           (p2 == left_node and p1 == Not(right_node)):
            return True

        if (p1 == Not(left_node) and p2 == right_node) or \
           (p2 == Not(left_node) and p1 == right_node):
            return True

        return False
