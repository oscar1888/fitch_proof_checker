from fitch_proof_checker.model.formula.predicate import Predicate
from fitch_proof_checker.model.rule.rule import Rule


class EqualsIntro(Rule):
    name = "=Intro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 0: return False

        return (type(actual_conclusion) is Predicate
                and actual_conclusion.name == "="
                and actual_conclusion.args[0] == actual_conclusion.args[1])
