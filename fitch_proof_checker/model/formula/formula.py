from fitch_proof_checker.model.formula.ASTNode import ASTNode


class Formula(ASTNode):
    def is_eq_subst(self, target, t1, t2) -> bool:
        if type(self) is not type(target):
            return False

        return self._check_eq_subst(target, t1, t2)
