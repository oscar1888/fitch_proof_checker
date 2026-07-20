from dataclasses import dataclass
from typing import ClassVar

from fitch_proof_checker.model.formula.formula import Formula
from fitch_proof_checker.model.formula.var import Var


@dataclass(frozen=True)
class Quantifier(Formula):
    variable: Var
    subformula: Formula

    name: ClassVar[str]
    symbol: ClassVar[str]

    def free_vars(self) -> set:
        return self.subformula.free_vars() - {self.variable.name}

    def _contains_children(self, other) -> bool:
        return self.variable.contains(other) or self.subformula.contains(other)

    def subst(self, to_subst, substituend):
        if self.variable == to_subst:
            return self

        return type(self)(
            self.variable,
            self.subformula.subst(to_subst, substituend)
        )

    def match_instantiation(self, other, allowed_vars, mapping=None) -> bool:
        if mapping is None:
            mapping = {}

        if type(self) is not type(other):
            return False

        if self.variable != other.variable:
            return False

        new_allowed = allowed_vars - {self.variable.name}

        return self.subformula.match_instantiation(other.subformula, new_allowed, mapping)

    def is_alpha_equiv(self, other, mapping=None) -> bool:
        if mapping is None:
            mapping = {}

        if type(self) is not type(other):
            return False

        new_mapping = mapping.copy()

        new_mapping[self.variable.name] = other.variable.name

        return self.subformula.is_alpha_equiv(other.subformula, new_mapping)

    def _check_eq_subst(self, target, t1, t2) -> bool:
        if self.variable != target.variable:
            return False
        return self.subformula.is_eq_subst(target.subformula, t1, t2)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.variable)}, {repr(self.subformula)})"


class ForAll(Quantifier):
    name = "For all"
    symbol = "∀"


class Exists(Quantifier):
    name = "Exists"
    symbol = "∃"
