from dataclasses import dataclass
from fitch_proof_checker.model.formula.term import Term


@dataclass
class Const(Term):
    name: str

    def _check_eq_subst(self, target, t1, t2) -> bool:
        return self.name == target.name

    def __repr__(self):
        return f"Const({repr(self.name)})"

    def subst(self, to_subst, substituend):
        if self == to_subst:
            return substituend
        return self

    def is_alpha_equiv(self, other, mapping=None) -> bool:
        if type(self) is not type(other):
            return False

        return self.name == other.name

    def match_instantiation(self, other, allowed_vars, mapping=None) -> bool:
        if type(self) is not type(other):
            return False

        return self.name == other.name