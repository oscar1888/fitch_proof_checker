from fitch_proof_checker.model.formula.connective import Not, Falsum
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class FalsumIntro(Rule):
    name = "⊥Intro"

    @staticmethod
    def _inner_check(first, second, actual_conclusion):
        return type(actual_conclusion) is Falsum and type(second) is Not and first == second.args[0]

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2: return False
        if isinstance(actual_premises[0], Subproof): return False
        if isinstance(actual_premises[1], Subproof): return False

        first = actual_premises[0]
        second = actual_premises[1]

        return (FalsumIntro._inner_check(first, second, actual_conclusion)
                or FalsumIntro._inner_check(second, first, actual_conclusion))
    