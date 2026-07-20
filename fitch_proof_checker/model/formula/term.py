from fitch_proof_checker.model.formula.ASTNode import ASTNode


class Term(ASTNode):
    def is_eq_subst(self, target, t1, t2) -> bool:
        if (self == t1 and target == t2) or (self == t2 and target == t1):
            return True

        if type(self) is not type(target):
            return False

        return self._check_eq_subst(target, t1, t2)
