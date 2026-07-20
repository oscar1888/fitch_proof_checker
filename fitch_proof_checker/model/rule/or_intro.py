from fitch_proof_checker.model.formula.connective import Or
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule
from fitch_proof_checker.model.rule.utils import flatten_connective


class OrIntro(Rule):
    name = "∨Intro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        item = actual_premises[0]
        if isinstance(item, Subproof):
            return False
        item = flatten_connective(item, Or)

        if type(actual_conclusion) is not Or:
            return False

        flat_args = flatten_connective(actual_conclusion, Or)

        return all(it in flat_args for it in item)
