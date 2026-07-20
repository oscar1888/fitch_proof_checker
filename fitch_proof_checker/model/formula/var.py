from dataclasses import dataclass
from fitch_proof_checker.model.formula.term import Term


@dataclass(frozen=True)
class Var(Term):
    name: str

    def free_vars(self) -> set:
        return {self.name}

    def _check_eq_subst(self, target, t1, t2) -> bool:
        return self.name == target.name

    def subst(self, to_subst, substituend):
        if self == to_subst:
            return substituend
        return self

    def match_instantiation(self, other, allowed_vars, mapping=None) -> bool:
        if mapping is None:
            mapping = {}

        if self.name in allowed_vars:
            if self.name in mapping:
                return mapping[self.name] == other
            else:
                mapping[self.name] = other
                return True

        if type(self) is not type(other):
            return False
        return self.name == other.name

    def is_alpha_equiv(self, other, mapping=None) -> bool:
        if mapping is None:
            mapping = {}

        if type(self) is not type(other):
            return False

        expected_name = mapping.get(self.name, self.name)

        return expected_name == other.name

    def __repr__(self):
        return f"Var({repr(self.name)})"
