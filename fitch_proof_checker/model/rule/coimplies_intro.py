from fitch_proof_checker.model.formula.connective import CoImplies
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CoImpliesIntro(Rule):
    name = "↔Intro"

    @staticmethod
    def _inner_check(sp1, sp2, actual_conclusion):
        first_op = actual_conclusion.args[0]
        second_op = actual_conclusion.args[1]

        return (sp1.assumption == first_op and sp1.lines[-1] == second_op
                and sp2.assumption == second_op and sp2.lines[-1] == first_op)

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2: return False
        if not isinstance(actual_premises[0], Subproof): return False
        if not isinstance(actual_premises[1], Subproof): return False
        if type(actual_conclusion) is not CoImplies: return False

        sp1 = actual_premises[0]
        sp2 = actual_premises[1]

        return (CoImpliesIntro._inner_check(sp1, sp2, actual_conclusion)
                or CoImpliesIntro._inner_check(sp2, sp1, actual_conclusion))
