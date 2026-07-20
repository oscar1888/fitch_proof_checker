from fitch_proof_checker.model.formula.connective import Implies, Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "Contrap"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        premise = actual_premises[0]
        if isinstance(premise, Subproof):
            return False

        if type(premise) is not Implies or type(actual_conclusion) is not Implies:
            return False

        if actual_conclusion.args[0] == Not(premise.args[1]) and actual_conclusion.args[1] == Not(premise.args[0]):
            return True

        if premise.args[0] == Not(actual_conclusion.args[1]) and premise.args[1] == Not(actual_conclusion.args[0]):
            return True

        return False
