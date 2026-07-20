from fitch_proof_checker.model.formula.connective import Not, Falsum
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class NotIntro(Rule):
    name = "¬Intro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1: return False
        sp = actual_premises[0]
        if not isinstance(actual_premises[0], Subproof): return False

        assumption = sp.assumption
        if assumption is None: return False

        sp_conclusion_formula = sp.lines[-1]

        if type(sp_conclusion_formula) is not Falsum: return False

        return (type(actual_conclusion) is Not and actual_conclusion.args[0] == assumption
                or type(assumption) is Not and assumption.args[0] == actual_conclusion)
