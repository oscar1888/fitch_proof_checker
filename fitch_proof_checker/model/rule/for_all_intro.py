from itertools import permutations
from fitch_proof_checker.model.formula.connective import Implies
from fitch_proof_checker.model.formula.const import Const
from fitch_proof_checker.model.formula.quantifier import ForAll
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.formula.var import Var
from fitch_proof_checker.model.rule.rule import Rule


class ForAllIntro(Rule):
    name = "∀Intro"

    @staticmethod
    def _check_gen_cond_proof(ipp, actual_premises, actual_conclusion):
        if len(actual_premises) != 1: return False
        sp = actual_premises[0]
        if not isinstance(sp, Subproof): return False

        constants = getattr(sp, 'constants', [])
        if not constants: return False

        assumption = getattr(sp, 'assumption', None)
        if assumption is None: return False

        sp_conclusion_formula = sp.lines[-1]
        if sp_conclusion_formula is None: return False

        if actual_conclusion is None: return False

        for c in constants:
            if ipp.constant_occurs_outside_subproof(Const(c), sp.lines_range):
                return False

        base_transformed = Implies(assumption, sp_conclusion_formula)

        for permuted_constants in permutations(constants):
            transformed_formula = base_transformed
            for c in permuted_constants:
                v_term = Var(f'${c}')
                c_term = Const(c)

                transformed_formula = transformed_formula.subst(c_term, v_term)
                transformed_formula = ForAll(v_term, transformed_formula)
            if transformed_formula.is_alpha_equiv(actual_conclusion): return True

        return False

    @staticmethod
    def _check_univ_intro(ipp, actual_premises, actual_conclusion):
        if len(actual_premises) != 1: return False
        sp = actual_premises[0]
        if not isinstance(sp, Subproof): return False
        if actual_conclusion is None: return False

        constants = sp.constants
        if not constants: return False

        assumption = getattr(sp, 'assumption', None)
        if assumption is not None: return False

        sp_conclusion = sp.lines[-1]
        if sp_conclusion is None: return False

        for c in constants:
            if ipp.constant_occurs_outside_subproof(Const(c), sp.lines_range): return False

        base_transformed = sp_conclusion

        for permuted_constants in permutations(constants):
            transformed_formula = base_transformed
            for c in permuted_constants:
                v_term = Var(f'${c}')
                c_term = Const(c)

                transformed_formula = transformed_formula.subst(c_term, v_term)
                transformed_formula = ForAll(v_term, transformed_formula)
            if transformed_formula.is_alpha_equiv(actual_conclusion): return True

        return False

    @staticmethod
    def check(ipp, actual_premises, actual_conclusion) -> bool:
        return (ForAllIntro._check_gen_cond_proof(ipp, actual_premises, actual_conclusion)
                or ForAllIntro._check_univ_intro(ipp, actual_premises, actual_conclusion))
