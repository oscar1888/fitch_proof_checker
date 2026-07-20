from fitch_proof_checker.model.formula.connective import Not, And, Or, Implies, CoImplies, Falsum
from fitch_proof_checker.model.grammar.grammar_manager import GrammarManager
from fitch_proof_checker.model.formula.quantifier import ForAll, Exists

FOL_connectives = [
    Not,
    And,
    Or,
    Implies,
    CoImplies,
    Falsum
]

FOL_quantifiers = [
    ForAll,
    Exists
]


class GrammarFactory:

    @staticmethod
    def create_propositional_logic() -> GrammarManager:
        return GrammarManager(FOL_connectives.copy(), [])

    @staticmethod
    def create_first_order_logic() -> GrammarManager:
        return GrammarManager(FOL_connectives.copy(), FOL_quantifiers.copy())
