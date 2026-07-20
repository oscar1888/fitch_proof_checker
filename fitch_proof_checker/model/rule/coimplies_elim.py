from fitch_proof_checker.model.formula.connective import CoImplies
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CoImpliesElim(Rule):
    name = "↔Elim"

    @staticmethod
    def _inner_check(first, second, actual_conclusion):
        if type(first) is not CoImplies: return False

        coimp = first
        ops = [coimp.args[0], coimp.args[1]]

        return (second == ops[0] and actual_conclusion == ops[1]
                or second == ops[1] and actual_conclusion == ops[0])

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2: return False
        if isinstance(actual_premises[0], Subproof): return False
        if isinstance(actual_premises[1], Subproof): return False

        return (CoImpliesElim._inner_check(actual_premises[0], actual_premises[1], actual_conclusion)
                or CoImpliesElim._inner_check(actual_premises[1], actual_premises[0], actual_conclusion))
