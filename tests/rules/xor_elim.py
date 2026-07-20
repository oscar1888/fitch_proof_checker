from fitch_proof_checker.model.formula.connective import Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "XorElim"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2:
            return False

        p1, p2 = actual_premises

        if isinstance(p1, Subproof) or isinstance(p2, Subproof):
            return False

        xor_premise = None
        other_premise = None

        if type(p1).__name__ == "CustomConnective" and p1.name == "Xor":
            xor_premise = p1
            other_premise = p2
        elif type(p2).__name__ == "CustomConnective" and p2.name == "Xor":
            xor_premise = p2
            other_premise = p1
        else:
            return False

        if len(xor_premise.args) != 2: return False

        left = xor_premise.args[0]
        right = xor_premise.args[1]

        if other_premise == left and actual_conclusion == Not(right):
            return True

        if other_premise == right and actual_conclusion == Not(left):
            return True

        if other_premise == Not(left) and actual_conclusion == right:
            return True

        if other_premise == Not(right) and actual_conclusion == left:
            return True

        return False
