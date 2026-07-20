from fitch_proof_checker.model.formula.quantifier import Quantifier


class CustomQuantifier(Quantifier):
    name = "Exists Unique"
    symbol = "∃!"
