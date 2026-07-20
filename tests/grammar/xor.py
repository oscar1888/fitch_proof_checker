from fitch_proof_checker.model.formula.connective import Connective


class CustomConnective(Connective):
    is_custom = True
    name = "Xor"
    symbol = "XOR"
    arity = 2
