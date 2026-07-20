from fitch_proof_checker.model.formula.const import Const
from fitch_proof_checker.model.formula.quantifier import Exists
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class ExistsElim(Rule):
    name = "∃Elim"

    @staticmethod
    def _check_combination(ipp, exists_premise, sp, actual_conclusion) -> bool:
        if not isinstance(exists_premise, Exists):
            return False
        if not isinstance(sp, Subproof):
            return False

        constants = getattr(sp, 'constants', [])
        if not constants:
            return False

        assumption = getattr(sp, 'assumption', None)
        if assumption is None:
            return False

        sp_conclusion_formula = sp.lines[-1]
        if sp_conclusion_formula is None: return False

        if actual_conclusion != sp_conclusion_formula:
            return False

        for c in constants:
            if ipp.constant_occurs_outside_subproof(Const(c), sp.lines_range):
                return False

        peeled_vars = set()
        curr_body = exists_premise

        while isinstance(curr_body, Exists):
            peeled_vars.add(curr_body.variable.name)
            curr_body = curr_body.subformula

            mapping = {}
            if curr_body.match_instantiation(assumption, peeled_vars, mapping):

                mapped_terms = list(mapping.values())

                if all(isinstance(t, Const) for t in mapped_terms):
                    mapped_names = [t.name for t in mapped_terms]

                    if all(name in constants for name in mapped_names):
                        return True

        return False

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2:
            return False

        p1, p2 = actual_premises

        return (ExistsElim._check_combination(ipp, p1, p2, actual_conclusion) or
                ExistsElim._check_combination(ipp, p2, p1, actual_conclusion))
