class ASTNode:
    def free_vars(self) -> set:
        return set()

    def match_instantiation(self, other, allowed_vars, mapping=None) -> bool:
        pass

    def is_eq_subst(self, target, t1, t2) -> bool:
        pass

    def contains(self, other) -> bool:
        if self == other:
            return True

        return self._contains_children(other)

    def _contains_children(self, other) -> bool:
        return False
