from fitch_proof_checker.model.formula.predicate import Predicate
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class EqualsElim(Rule):
    name = "=Elim"

    @staticmethod
    def _inner_check(premise_1, premise_2, concl):
        if premise_1 is None or premise_2 is None or concl is None: return False
        if not isinstance(premise_2, Predicate): return False
        if premise_2.name != '=': return False

        first = premise_2.args[0]
        second = premise_2.args[1]

        return premise_1.is_eq_subst(concl, first, second)

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2: return False
        if isinstance(actual_premises[0], Subproof): return False
        if isinstance(actual_premises[1], Subproof): return False

        return (EqualsElim._inner_check(actual_premises[0], actual_premises[1], actual_conclusion)
                or EqualsElim._inner_check(actual_premises[1], actual_premises[0], actual_conclusion))
