from collections import Counter
from fitch_proof_checker.model.formula.connective import And, Or, Not
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule
from fitch_proof_checker.model.rule.utils import flatten_connective


class CustomRule(Rule):
    name = "DeMorgan"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        premise = actual_premises[0]
        if isinstance(premise, Subproof):
            return False

        if type(premise) is not Not:
            return False

        inner_formula = premise.args[0]

        if type(inner_formula) is And:
            expected_conclusion_type = Or
        elif type(inner_formula) is Or:
            expected_conclusion_type = And
        else:
            return False

        if type(actual_conclusion) is not expected_conclusion_type:
            return False

        inner_args = flatten_connective(inner_formula, type(inner_formula))
        conclusion_args = flatten_connective(actual_conclusion, expected_conclusion_type)

        expected_negations = Counter(Not(arg) for arg in inner_args)
        actual_negations = Counter(conclusion_args)

        return expected_negations == actual_negations
