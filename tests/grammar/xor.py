from fitch_proof_checker.model.formula.connective import Connective


class CustomConnective(Connective):
    name = "Xor"
    symbol = "XOR"
    arity = 2
