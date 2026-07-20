from fitch_proof_checker.model.formula.connective import And
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule
from fitch_proof_checker.model.rule.utils import flatten_connective


class CustomRule(Rule):
    name = "IdempAnd"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        premise = actual_premises[0]
        if isinstance(premise, Subproof):
            return False

        if type(actual_conclusion) is not And: return False

        flat_args = flatten_connective(actual_conclusion, And)

        return all(e == premise for e in flat_args)
    