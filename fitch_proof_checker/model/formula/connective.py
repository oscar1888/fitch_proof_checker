from dataclasses import dataclass
from typing import Tuple, ClassVar

from fitch_proof_checker.model.formula.formula import Formula


@dataclass(init=False, frozen=True)
class Connective(Formula):
    args: Tuple[Formula, ...]

    name: ClassVar[str]
    symbol: ClassVar[str]
    arity: ClassVar[int]
    is_custom: ClassVar[bool] = True

    def __init__(self, *args: Formula):
        if len(args) != self.arity:
            raise ValueError(f"'{self.name}' requires {self.arity} arguments.")
        object.__setattr__(self, "args", tuple(args))

    def free_vars(self) -> set:
        res = set()
        for arg in self.args:
            res.update(arg.free_vars())
        return res

    def match_instantiation(self, other, allowed_vars, mapping=None) -> bool:
        if mapping is None:
            mapping = {}

        if type(self) is not type(other):
            return False

        if getattr(self, 'name', None) != getattr(other, 'name', None):
            return False

        if len(self.args) != len(other.args):
            return False

        return all(a.match_instantiation(b, allowed_vars, mapping) for a, b in zip(self.args, other.args))

    def is_alpha_equiv(self, other, mapping=None) -> bool:
        if mapping is None:
            mapping = {}

        if type(self) is not type(other):
            return False

        if getattr(self, 'name', None) != getattr(other, 'name', None):
            return False

        if len(self.args) != len(other.args):
            return False

        return all(a.is_alpha_equiv(b, mapping) for a, b in zip(self.args, other.args))

    def _contains_children(self, other) -> bool:
        return any(arg.contains(other) for arg in self.args)

    def subst(self, to_subst, substituend):
        return type(self)(
            *[arg.subst(to_subst, substituend) for arg in self.args]
        )

    def _check_eq_subst(self, target, t1, t2) -> bool:
        if len(self.args) != len(target.args):
            return False
        return all(a.is_eq_subst(b, t1, t2) for a, b in zip(self.args, target.args))

    def __repr__(self):
        args_str = ", ".join(repr(a) for a in self.args)
        return f"{self.__class__.__name__}({args_str})"


class Not(Connective):
    is_custom = False
    name = "Not"
    symbol = "¬"
    arity = 1


class And(Connective):
    is_custom = False
    name = "And"
    symbol = "∧"
    arity = 2


class Or(Connective):
    is_custom = False
    name = "Or"
    symbol = "∨"
    arity = 2


class Implies(Connective):
    is_custom = False
    name = "Implies"
    symbol = "→"
    arity = 2


class CoImplies(Connective):
    is_custom = False
    name = "CoImplies"
    symbol = "↔"
    arity = 2


class Falsum(Connective):
    is_custom = False
    name = "False"
    symbol = "⊥"
    arity = 0
