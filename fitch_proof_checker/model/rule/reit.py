from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class Reit(Rule):
    name = "Reit"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if actual_conclusion is None: return False
        if len(actual_premises) != 1: return False
        if isinstance(actual_premises[0], Subproof): return False

        return actual_premises[0] == actual_conclusion
