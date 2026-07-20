from fitch_proof_checker.model.formula.connective import Implies
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class ImpliesElim(Rule):
    name = "→Elim"

    @staticmethod
    def _inner_check(first, second, actual_conclusion):
        if type(first) is not Implies: return False

        first_op = first.args[0]
        second_op = first.args[1]

        return first_op == second and second_op == actual_conclusion

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2: return False
        if isinstance(actual_premises[0], Subproof): return False
        if isinstance(actual_premises[1], Subproof): return False

        return (ImpliesElim._inner_check(actual_premises[0], actual_premises[1], actual_conclusion)
                or ImpliesElim._inner_check(actual_premises[1], actual_premises[0], actual_conclusion))
