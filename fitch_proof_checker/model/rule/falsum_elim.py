from fitch_proof_checker.model.formula.connective import Falsum
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class FalsumElim(Rule):
    name = "⊥Elim"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1: return False
        if isinstance(actual_premises[0], Subproof): return False

        return type(actual_premises[0]) is Falsum and actual_conclusion is not None
