from fitch_proof_checker.model.formula.connective import Not
from fitch_proof_checker.model.formula.quantifier import ForAll, Exists
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "QuantEx"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 1:
            return False

        premise = actual_premises[0]
        if isinstance(premise, Subproof):
            return False

        if type(premise) is Not:
            inner_formula = premise.args[0]

            if type(inner_formula) is ForAll:
                expected_conclusion_type = Exists
            elif type(inner_formula) is Exists:
                expected_conclusion_type = ForAll
            else:
                return False

            if type(actual_conclusion) is not expected_conclusion_type:
                return False

            if inner_formula.variable != actual_conclusion.variable:
                return False

            return actual_conclusion.subformula == Not(inner_formula.subformula)
        elif type(premise) in (ForAll, Exists):

            if type(premise) is ForAll:
                expected_inner_type = Exists
            else:
                expected_inner_type = ForAll

            if type(actual_conclusion) is not Not:
                return False

            conclusion_inner = actual_conclusion.args[0]
            if type(conclusion_inner) is not expected_inner_type:
                return False

            if premise.variable != conclusion_inner.variable:
                return False

            return Not(premise.subformula) == conclusion_inner.subformula

        return False
