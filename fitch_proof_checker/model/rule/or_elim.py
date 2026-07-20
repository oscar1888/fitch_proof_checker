from fitch_proof_checker.model.formula.connective import Or
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule
from fitch_proof_checker.model.rule.utils import flatten_connective


class OrElim(Rule):
    name = "∨Elim"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if actual_conclusion is None:
            return False

        formulas = [p for p in actual_premises if not isinstance(p, Subproof)]
        subproofs = [p for p in actual_premises if isinstance(p, Subproof)]

        if len(formulas) != 1:
            return False

        or_formula = formulas[0]

        if type(or_formula) is not Or:
            return False

        disjuncts = flatten_connective(or_formula, Or)

        unmatched_disjuncts = list(disjuncts)

        for sp in subproofs:
            assumption_formula = sp.assumption
            conclusion_formula = sp.lines[-1]

            if conclusion_formula != actual_conclusion:
                return False

            if type(assumption_formula) is Or:
                assumed_items = flatten_connective(assumption_formula, Or)
            else:
                assumed_items = [assumption_formula]

            for item in assumed_items:
                if item in unmatched_disjuncts:
                    unmatched_disjuncts.remove(item)
                else:
                    return False

        return len(unmatched_disjuncts) == 0
