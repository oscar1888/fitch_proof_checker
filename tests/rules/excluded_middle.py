from fitch_proof_checker.model.formula.connective import Or, Not
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "ExclMid"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 0:
            return False

        if type(actual_conclusion) is not Or or len(actual_conclusion.args) != 2:
            return False

        if actual_conclusion.args[1] == Not(actual_conclusion.args[0]):
            return True

        if actual_conclusion.args[0] == Not(actual_conclusion.args[1]):
            return True

        return False
