from fitch_proof_checker.model.formula.quantifier import Exists
from fitch_proof_checker.model.rule.rule import Rule


class ExistsIntro(Rule):
    name = "∃Intro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        premise = actual_premises[0]
        if premise is None: return False

        if not isinstance(actual_conclusion, Exists):
            return False

        peeled_vars = set()
        curr_body = actual_conclusion

        while isinstance(curr_body, Exists):
            peeled_vars.add(curr_body.variable.name)
            curr_body = curr_body.subformula

            mapping = {}
            if curr_body.match_instantiation(premise, peeled_vars, mapping):
                return True

        return False
