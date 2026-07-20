from collections import Counter

from fitch_proof_checker.model.formula.connective import And
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule
from fitch_proof_checker.model.rule.utils import flatten_connective


class AndIntro(Rule):
    name = "∧Intro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) < 2:
            return False

        premise_formulas = list()
        for item in actual_premises:
            if isinstance(item, Subproof):
                return False
            premise_formulas.extend(flatten_connective(item, And))
        premise_formulas = Counter(premise_formulas)

        if type(actual_conclusion) is not And:
            return False

        flat_args = Counter(flatten_connective(actual_conclusion, And))

        return premise_formulas == flat_args
