from fitch_proof_checker.model.formula.predicate import Predicate
from fitch_proof_checker.model.formula.quantifier import ForAll
from fitch_proof_checker.model.formula.connective import Implies
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.rule import Rule


class CustomRule(Rule):
    name = "∃!Intro"

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        if len(actual_premises) != 2:
            return False

        if isinstance(actual_premises[0], Subproof) or isinstance(actual_premises[1], Subproof):
            return False

        if type(actual_conclusion).__name__ != "CustomQuantifier" or actual_conclusion.name != "Exists Unique":
            return False

        var = actual_conclusion.variable
        body = actual_conclusion.subformula

        p1, p2 = actual_premises

        forall_premise = None
        other_premise = None

        if type(p1) is ForAll:
            forall_premise, other_premise = p1, p2
        elif type(p2) is ForAll:
            forall_premise, other_premise = p2, p1
        else:
            return False

        if forall_premise.variable != var:
            return False

        if type(forall_premise.subformula) is not Implies:
            return False

        impl = forall_premise.subformula

        if impl.args[0] != body:
            return False

        if type(impl.args[1]) is not Predicate or impl.args[1].name != "=":
            return False

        eq = impl.args[1]

        c = None
        if eq.args[0] == var:
            c = eq.args[1]
        elif eq.args[1] == var:
            c = eq.args[0]
        else:
            return False

        expected_existence_premise = body.subst(var, c)

        return other_premise == expected_existence_premise
