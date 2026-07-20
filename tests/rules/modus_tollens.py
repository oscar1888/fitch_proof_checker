from fitch_proof_checker.model.formula.connective import Implies, Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "ModusTollens"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2:
            return False

        if isinstance(actual_premises[0], Subproof) or isinstance(actual_premises[1], Subproof):
            return False

        p1, p2 = actual_premises
        impl_premise = None

        if type(p1) is Implies and p2 == Not(p1.args[1]):
            impl_premise = p1
        elif type(p2) is Implies and p1 == Not(p2.args[1]):
            impl_premise = p2
        else:
            return False

        return actual_conclusion == Not(impl_premise.args[0])
