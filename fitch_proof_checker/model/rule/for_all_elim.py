from fitch_proof_checker.model.formula.quantifier import ForAll
from fitch_proof_checker.model.rule.rule import Rule


class ForAllElim(Rule):
    name = "∀Elim"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False
        if actual_conclusion is None: return False

        premise = actual_premises[0]

        if not isinstance(premise, ForAll):
            return False

        peeled_vars = set()
        curr_body = premise

        while isinstance(curr_body, ForAll):
            peeled_vars.add(curr_body.variable.name)
            curr_body = curr_body.subformula

            mapping = {}
            if curr_body.match_instantiation(actual_conclusion, peeled_vars, mapping):
                return True

        return False
