from fitch_proof_checker.model.formula.predicate import Predicate
from fitch_proof_checker.model.formula.quantifier import Exists
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "\\∃!Elim"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if any(isinstance(p, Subproof) for p in actual_premises):
            return False

        if len(actual_premises) == 1:
            p = actual_premises[0]
            if type(p).__name__ == "CustomQuantifier" and p.name == "Exists Unique" and type(actual_conclusion) is Exists:
                return p.variable == actual_conclusion.variable and p.subformula == actual_conclusion.subformula
            return False

        if len(actual_premises) == 3:
            ex_un_prem = actual_premises[0]

            if type(ex_un_prem).__name__ != "CustomQuantifier" or ex_un_prem.name != "Exists Unique":
                return False

            p_a_candidate = actual_premises[1]
            p_b_candidate = actual_premises[2]

            if type(actual_conclusion) is not Predicate or actual_conclusion.name != "=":
                return False

            term_a = actual_conclusion.args[0]
            term_b = actual_conclusion.args[1]

            var = ex_un_prem.variable
            body = ex_un_prem.subformula

            expected_p_a = body.subst(var, term_a)
            expected_p_b = body.subst(var, term_b)

            if (p_a_candidate == expected_p_a and p_b_candidate == expected_p_b) or \
                    (p_b_candidate == expected_p_a and p_a_candidate == expected_p_b):
                return True

        return False
