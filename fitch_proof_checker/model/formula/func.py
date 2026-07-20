from dataclasses import dataclass
from typing import Tuple
from fitch_proof_checker.model.formula.term import Term


@dataclass(init=False)
class Func(Term):
    name: str
    args: Tuple[Term, ...]

    def __init__(self, name: str, *args: Term):
        self.name = name
        self.args = tuple(args)

    def free_vars(self) -> set:
        res = set()
        for arg in self.args:
            res.update(arg.free_vars())
        return res

    def subst(self, to_subst, substituend):
        return type(self)(
            self.name,
            *[arg.subst(to_subst, substituend) for arg in self.args]
        )

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

    def _contains_children(self, other) -> bool:
        return any(arg.contains(other) for arg in self.args)

    def _check_eq_subst(self, target, t1, t2) -> bool:
        if self.name != target.name or len(self.args) != len(target.args):
            return False
        return all(a.is_eq_subst(b, t1, t2) for a, b in zip(self.args, target.args))

    def __repr__(self):
        args_str = ", ".join(repr(a) for a in self.args)
        if args_str:
            return f"Func({repr(self.name)}, {args_str})"
        return f"Func({repr(self.name)})"
