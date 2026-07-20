from fitch_proof_checker.model.formula.connective import Or, Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "DisjunSill"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2:
            return False

        if isinstance(actual_premises[0], Subproof) or isinstance(actual_premises[1], Subproof):
            return False

        p1, p2 = actual_premises
        expected_conclusion = None

        if type(p1) is Or and len(p1.args) == 2:
            if p2 == Not(p1.args[0]):
                expected_conclusion = p1.args[1]
            elif p2 == Not(p1.args[1]):
                expected_conclusion = p1.args[0]

        if expected_conclusion is None and type(p2) is Or and len(p2.args) == 2:
            if p1 == Not(p2.args[0]):
                expected_conclusion = p2.args[1]
            elif p1 == Not(p2.args[1]):
                expected_conclusion = p2.args[0]

        if expected_conclusion is None:
            return False

        return actual_conclusion == expected_conclusion
