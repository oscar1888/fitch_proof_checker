from fitch_proof_checker.model.formula.connective import Implies, Or, Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "MatImpl"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        premise = actual_premises[0]
        if isinstance(premise, Subproof):
            return False

        if type(premise) is Implies and type(actual_conclusion) is Or and len(actual_conclusion.args) == 2:
            if actual_conclusion.args[0] == Not(premise.args[0]) and actual_conclusion.args[1] == premise.args[1]:
                return True

        if type(premise) is Or and type(actual_conclusion) is Implies and len(premise.args) == 2:
            if premise.args[0] == Not(actual_conclusion.args[0]) and premise.args[1] == actual_conclusion.args[1]:
                return True

        return False
