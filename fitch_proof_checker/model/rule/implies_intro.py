from fitch_proof_checker.model.formula.connective import Implies
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class ImpliesIntro(Rule):
    name = "→Intro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1: return False
        if not isinstance(actual_premises[0], Subproof): return False
        if type(actual_conclusion) is not Implies: return False

        sp = actual_premises[0]
        first = actual_conclusion.args[0]
        second = actual_conclusion.args[1]

        return sp.assumption == first and sp.lines[-1] == second
