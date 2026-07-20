from fitch_proof_checker.model.formula.quantifier import Quantifier
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "RenameVar"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        premise = actual_premises[0]

        if isinstance(premise, Subproof):
            return False

        if not isinstance(premise, Quantifier):
            return False

        return premise.is_alpha_equiv(actual_conclusion)
