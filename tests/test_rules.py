import pytest
from unittest.mock import MagicMock
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.rule.utils import flatten_connective
from fitch_proof_checker.model.formula.connective import And, Or, Not, Implies, CoImplies, Falsum
from fitch_proof_checker.model.formula.predicate import Predicate
from fitch_proof_checker.model.formula.quantifier import Exists, ForAll
from fitch_proof_checker.model.formula.const import Const
from fitch_proof_checker.model.formula.var import Var
from fitch_proof_checker.model.rule.and_elim import AndElim
from fitch_proof_checker.model.rule.and_intro import AndIntro
from fitch_proof_checker.model.rule.coimplies_elim import CoImpliesElim
from fitch_proof_checker.model.rule.coimplies_intro import CoImpliesIntro
from fitch_proof_checker.model.rule.equals_elim import EqualsElim
from fitch_proof_checker.model.rule.equals_intro import EqualsIntro
from fitch_proof_checker.model.rule.exists_elim import ExistsElim
from fitch_proof_checker.model.rule.exists_intro import ExistsIntro
from fitch_proof_checker.model.rule.falsum_elim import FalsumElim
from fitch_proof_checker.model.rule.falsum_intro import FalsumIntro
from fitch_proof_checker.model.rule.for_all_elim import ForAllElim
from fitch_proof_checker.model.rule.for_all_intro import ForAllIntro
from fitch_proof_checker.model.rule.implies_elim import ImpliesElim
from fitch_proof_checker.model.rule.implies_intro import ImpliesIntro
from fitch_proof_checker.model.rule.not_elim import NotElim
from fitch_proof_checker.model.rule.not_intro import NotIntro
from fitch_proof_checker.model.rule.or_elim import OrElim
from fitch_proof_checker.model.rule.or_intro import OrIntro
from fitch_proof_checker.model.rule.reit import Reit


def make_node(cls, **kwargs):
    obj = cls.__new__(cls)
    for k, v in kwargs.items():
        object.__setattr__(obj, k, v)
    return obj


@pytest.fixture
def ipp():
    mock = MagicMock()
    mock.constant_occurs_outside_subproof.return_value = False
    return mock


@pytest.fixture
def subproof():
    def _make(assumption, conclusion, constants=None):
        sp = Subproof.__new__(Subproof)
        object.__setattr__(sp, 'assumption', assumption)
        object.__setattr__(sp, 'lines', [conclusion])
        object.__setattr__(sp, 'constants', constants or [])
        object.__setattr__(sp, 'lines_range', (1, 2))
        return sp

    return _make


def test_flatten_connective():
    a, b, c = MagicMock(), MagicMock(), MagicMock()
    nested_and = make_node(And, args=[b, c])
    main_and = make_node(And, args=[a, nested_and])

    result = flatten_connective(main_and, And)
    assert result == [a, b, c]


def test_and_elim(ipp, subproof):
    a, b, c, d = MagicMock(), MagicMock(), MagicMock(), MagicMock()
    and_form = make_node(And, args=[a, b])

    assert AndElim.check(ipp, [and_form], a) is True
    assert AndElim.check(ipp, [and_form], b) is True
    assert AndElim.check(ipp, [and_form, and_form], a) is False
    assert AndElim.check(ipp, [subproof(a, b)], a) is False
    assert AndElim.check(ipp, [a], a) is False

    nested_and_bc = make_node(And, args=[b, c])
    and_abc = make_node(And, args=[a, nested_and_bc])

    concl_and_ab = make_node(And, args=[a, b])
    concl_and_ad = make_node(And, args=[a, d])

    assert AndElim.check(ipp, [and_abc], concl_and_ab) is True
    assert AndElim.check(ipp, [and_abc], concl_and_ad) is False


def test_and_intro(ipp, subproof):
    a, b = MagicMock(), MagicMock()
    and_form = make_node(And, args=[a, b])

    assert AndIntro.check(ipp, [a, b], and_form) is True
    assert AndIntro.check(ipp, [b, a], and_form) is True
    assert AndIntro.check(ipp, [a], and_form) is False
    assert AndIntro.check(ipp, [a, b], a) is False
    assert AndIntro.check(ipp, [a, subproof(b, a)], and_form) is False


def test_coimplies_elim(ipp, subproof):
    a, b = MagicMock(), MagicMock()
    coimp = make_node(CoImplies, args=[a, b])

    assert CoImpliesElim.check(ipp, [coimp, a], b) is True
    assert CoImpliesElim.check(ipp, [b, coimp], a) is True
    assert CoImpliesElim.check(ipp, [coimp, a], a) is False
    assert CoImpliesElim.check(ipp, [subproof(a, b), a], b) is False


def test_coimplies_intro(ipp, subproof):
    a, b = MagicMock(), MagicMock()
    coimp = make_node(CoImplies, args=[a, b])
    sp1, sp2 = subproof(a, b), subproof(b, a)

    assert CoImpliesIntro.check(ipp, [sp1, sp2], coimp) is True
    assert CoImpliesIntro.check(ipp, [sp2, sp1], coimp) is True
    assert CoImpliesIntro.check(ipp, [a, b], coimp) is False
    assert CoImpliesIntro.check(ipp, [sp1, sp2], a) is False


def test_equals_elim(ipp):
    a, b, c = MagicMock(), MagicMock(), MagicMock()
    eq = make_node(Predicate, name="=", args=[a, b])

    p1 = MagicMock()
    p1.is_eq_subst.return_value = True

    assert EqualsElim.check(ipp, [p1, eq], c) is True
    p1.is_eq_subst.assert_called_with(c, a, b)

    assert EqualsElim.check(ipp, [eq, p1], c) is True

    assert EqualsElim.check(ipp, [p1], c) is False
    bad_eq = make_node(Predicate, name="P", args=[a, b])
    assert EqualsElim.check(ipp, [p1, bad_eq], c) is False


def test_equals_intro(ipp):
    a = MagicMock()
    eq = make_node(Predicate, name="=", args=[a, a])
    neq = make_node(Predicate, name="=", args=[a, MagicMock()])

    assert EqualsIntro.check(ipp, [], eq) is True
    assert EqualsIntro.check(ipp, [a], eq) is False
    assert EqualsIntro.check(ipp, [], neq) is False


def test_exists_elim(ipp, subproof):
    a, c = MagicMock(), MagicMock()
    ex = make_node(Exists, variable=make_node(Var, name="x"), subformula=a)

    def mock_match(assump, peeled, mapping):
        mapping['x'] = make_node(Const, name="c_name")
        return True

    a.match_instantiation = MagicMock(side_effect=mock_match)
    sp = subproof(assumption=a, conclusion=c, constants=["c_name"])

    assert ExistsElim.check(ipp, [ex, sp], c) is True
    assert ExistsElim.check(ipp, [sp, ex], c) is True

    assert ExistsElim.check(ipp, [ex, a], c) is False

    assert ExistsElim.check(ipp, [ex], c) is False
    assert ExistsElim.check(ipp, [ex, sp, ex], c) is False

    sp_no_const = subproof(assumption=a, conclusion=c, constants=[])
    assert ExistsElim.check(ipp, [ex, sp_no_const], c) is False

    sp_no_assump = subproof(assumption=None, conclusion=c, constants=["c_name"])
    assert ExistsElim.check(ipp, [ex, sp_no_assump], c) is False

    wrong_concl = MagicMock()
    assert ExistsElim.check(ipp, [ex, sp], wrong_concl) is False

    ipp.constant_occurs_outside_subproof.return_value = True
    assert ExistsElim.check(ipp, [ex, sp], c) is False
    ipp.constant_occurs_outside_subproof.return_value = False

    a_fail = MagicMock()
    a_fail.match_instantiation.return_value = False
    ex_fail = make_node(Exists, variable=make_node(Var, name="x"), subformula=a_fail)

    assert ExistsElim.check(ipp, [ex_fail, sp], c) is False


def test_exists_intro(ipp):
    a = MagicMock()
    ex = make_node(Exists, variable=make_node(Var, name="x"), subformula=a)

    a.match_instantiation = MagicMock(return_value=True)

    assert ExistsIntro.check(ipp, [a], ex) is True
    assert ExistsIntro.check(ipp, [a, a], ex) is False
    assert ExistsIntro.check(ipp, [a], a) is False

    a_fail = MagicMock()
    a_fail.match_instantiation.return_value = False
    ex_fail = make_node(Exists, variable=make_node(Var, name="x"), subformula=a_fail)
    assert ExistsIntro.check(ipp, [a], ex_fail) is False


def test_falsum_elim(ipp, subproof):
    f, c = make_node(Falsum), MagicMock()

    assert FalsumElim.check(ipp, [f], c) is True
    assert FalsumElim.check(ipp, [c], c) is False
    assert FalsumElim.check(ipp, [subproof(f, c)], c) is False


def test_falsum_intro(ipp):
    a = MagicMock()
    not_a = make_node(Not, args=[a])
    f = make_node(Falsum)

    assert FalsumIntro.check(ipp, [a, not_a], f) is True
    assert FalsumIntro.check(ipp, [not_a, a], f) is True
    assert FalsumIntro.check(ipp, [a, a], f) is False


def test_forall_elim(ipp):
    a = MagicMock()
    fa = make_node(ForAll, variable=make_node(Var, name="x"), subformula=a)

    a.match_instantiation = MagicMock(return_value=True)

    assert ForAllElim.check(ipp, [fa], a) is True
    assert ForAllElim.check(ipp, [a], a) is False

    assert ForAllElim.check(ipp, [], a) is False
    assert ForAllElim.check(ipp, [fa, fa], a) is False

    a_fail = MagicMock()
    a_fail.match_instantiation.return_value = False
    fa_fail = make_node(ForAll, variable=make_node(Var, name="x"), subformula=a_fail)
    assert ForAllElim.check(ipp, [fa_fail], a) is False


def test_forall_intro(ipp, subproof, mocker):
    mock_implies = mocker.patch('fitch_proof_checker.model.rule.for_all_intro.Implies')
    mock_forall = mocker.patch('fitch_proof_checker.model.rule.for_all_intro.ForAll')
    mocker.patch('fitch_proof_checker.model.rule.for_all_intro.Var')
    mocker.patch('fitch_proof_checker.model.rule.for_all_intro.Const')

    mock_implies_inst, mock_forall_inst = MagicMock(), MagicMock()
    mock_implies.return_value = mock_implies_inst
    mock_implies_inst.subst.return_value = MagicMock()

    mock_forall.return_value = mock_forall_inst
    mock_forall_inst.is_alpha_equiv.return_value = True

    concl = MagicMock()

    sp1 = subproof(assumption=MagicMock(), conclusion=MagicMock(), constants=["c"])
    assert ForAllIntro.check(ipp, [sp1], concl) is True

    ipp.constant_occurs_outside_subproof.return_value = True
    assert ForAllIntro.check(ipp, [sp1], concl) is False
    ipp.constant_occurs_outside_subproof.return_value = False

    mock_forall_inst.is_alpha_equiv.return_value = False
    assert ForAllIntro.check(ipp, [sp1], concl) is False

    mock_forall_inst.is_alpha_equiv.return_value = True
    sp2 = subproof(assumption=None, conclusion=MagicMock(), constants=["c"])
    sp2.lines[-1].subst = MagicMock()
    assert ForAllIntro.check(ipp, [sp2], concl) is True

    mock_forall_inst.is_alpha_equiv.return_value = False
    assert ForAllIntro.check(ipp, [sp2], concl) is False


def test_implies_elim(ipp):
    a, b = MagicMock(), MagicMock()
    imp = make_node(Implies, args=[a, b])

    assert ImpliesElim.check(ipp, [imp, a], b) is True
    assert ImpliesElim.check(ipp, [a, imp], b) is True
    assert ImpliesElim.check(ipp, [imp, b], a) is False


def test_implies_intro(ipp, subproof):
    a, b = MagicMock(), MagicMock()
    imp = make_node(Implies, args=[a, b])
    sp = subproof(a, b)

    assert ImpliesIntro.check(ipp, [sp], imp) is True
    assert ImpliesIntro.check(ipp, [sp], a) is False


def test_not_elim(ipp):
    a = MagicMock()
    not_a = make_node(Not, args=[a])
    not_not_a = make_node(Not, args=[not_a])

    assert NotElim.check(ipp, [not_not_a], a) is True
    assert NotElim.check(ipp, [not_a], a) is False


def test_not_intro(ipp, subproof):
    a = MagicMock()
    not_a = make_node(Not, args=[a])
    f = make_node(Falsum)

    sp1, sp2 = subproof(a, f), subproof(not_a, f)

    assert NotIntro.check(ipp, [sp1], not_a) is True
    assert NotIntro.check(ipp, [sp2], a) is True


def test_or_elim(ipp, subproof):
    a, b, c = MagicMock(), MagicMock(), MagicMock()
    or_ab = make_node(Or, args=[a, b])
    sp1, sp2 = subproof(a, c), subproof(b, c)

    assert OrElim.check(ipp, [or_ab, sp1, sp2], c) is True
    assert OrElim.check(ipp, [or_ab, sp1], c) is False
    assert OrElim.check(ipp, [or_ab, sp1, subproof(b, a)], c) is False

    assert OrElim.check(ipp, [or_ab, sp1, sp2], None) is False

    assert OrElim.check(ipp, [sp1, sp2], c) is False
    assert OrElim.check(ipp, [or_ab, or_ab, sp1, sp2], c) is False

    assert OrElim.check(ipp, [a, sp1, sp2], c) is False

    sp_or = subproof(or_ab, c)
    assert OrElim.check(ipp, [or_ab, sp_or], c) is True

    d = MagicMock()
    sp_bad = subproof(d, c)
    assert OrElim.check(ipp, [or_ab, sp1, sp_bad], c) is False


def test_or_intro(ipp, subproof):
    a, b = MagicMock(), MagicMock()
    or_ab = make_node(Or, args=[a, b])

    assert OrIntro.check(ipp, [a], or_ab) is True
    assert OrIntro.check(ipp, [b], or_ab) is True
    assert OrIntro.check(ipp, [a, b], or_ab) is False
    assert OrIntro.check(ipp, [a], a) is False

    sp = subproof(a, b)
    assert OrIntro.check(ipp, [sp], or_ab) is False


def test_reit(ipp, subproof):
    a = MagicMock()
    assert Reit.check(ipp, [a], a) is True
    assert Reit.check(ipp, [a, a], a) is False
    assert Reit.check(ipp, [subproof(a, a)], a) is False
