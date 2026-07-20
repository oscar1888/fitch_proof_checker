from fitch_proof_checker.model.formula.connective import And
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule
from fitch_proof_checker.model.rule.utils import flatten_connective


class AndElim(Rule):
    name = "∧Elim"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        item = actual_premises[0]
        if isinstance(item, Subproof):
            return False

        if type(item) is not And:
            return False

        flat_args = flatten_connective(item, And)

        if type(actual_conclusion) is And:
            flat_conclusion_args = flatten_connective(actual_conclusion, And)
            return all(c_arg in flat_args for c_arg in flat_conclusion_args)

        return actual_conclusion in flat_args
