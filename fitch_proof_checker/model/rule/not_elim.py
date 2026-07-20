from fitch_proof_checker.model.formula.connective import Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class NotElim(Rule):
    name = "¬Elim"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1: return False
        if isinstance(actual_premises[0], Subproof): return False

        pr = actual_premises[0]

        return type(pr) is Not and type(pr.args[0]) is Not and pr.args[0].args[0] == actual_conclusion
