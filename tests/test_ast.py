import pytest
from unittest.mock import MagicMock
from fitch_proof_checker.model.formula.ASTNode import ASTNode
from fitch_proof_checker.model.formula.var import Var
from fitch_proof_checker.model.formula.const import Const
from fitch_proof_checker.model.formula.func import Func
from fitch_proof_checker.model.formula.prop_var import PropVar
from fitch_proof_checker.model.formula.predicate import Predicate
from fitch_proof_checker.model.formula.connective import And, Or, Not, Implies, CoImplies, Falsum
from fitch_proof_checker.model.formula.quantifier import ForAll, Exists
from fitch_proof_checker.model.formula.justifiedline import JustifiedLine
from fitch_proof_checker.model.formula.subproof import Subproof
from fitch_proof_checker.model.formula.formula_transformer import FormulaTransformer


def test_astnode_base():
    node = ASTNode()
    assert node.free_vars() == set()
    assert node.match_instantiation(None, set()) is None
    assert node.is_eq_subst(None, None, None) is None

    node2 = ASTNode()
    assert node.contains(node) is True
    assert node.contains(node2) is False


def test_term_is_eq_subst():
    t1, t2 = Var("x"), Var("y")

    assert t1.is_eq_subst(t2, t1, t2) is True
    assert t2.is_eq_subst(t1, t1, t2) is True

    assert t1.is_eq_subst(PropVar("P"), t1, t2) is False


def test_formula_is_eq_subst():
    f1 = PropVar("P")

    assert f1.is_eq_subst(Var("x"), None, None) is False


def test_var():
    v1 = Var("x")
    v2 = Var("y")

    assert v1.free_vars() == {"x"}
    assert v1._check_eq_subst(Var("x"), None, None) is True
    assert v1._check_eq_subst(v2, None, None) is False
    assert repr(v1) == "Var('x')"

    assert v1.subst(v1, v2) == v2
    assert v1.subst(v2, v1) == v1

    assert v1.is_alpha_equiv(v2, {"x": "y"}) is True
    assert v1.is_alpha_equiv(v1) is True
    assert v1.is_alpha_equiv(Const("x")) is False

    mapping = {}
    assert v1.match_instantiation(v2, {"x"}, mapping) is True
    assert mapping["x"] == v2
    assert v1.match_instantiation(Const("c"), {"x"}, mapping) is False

    assert v1.match_instantiation(v1, set()) is True
    assert v1.match_instantiation(v2, set()) is False
    assert v1.match_instantiation(Const("x"), set()) is False


def test_const():
    c1, c2 = Const("c"), Const("d")

    assert c1._check_eq_subst(Const("c"), None, None) is True
    assert repr(c1) == "Const('c')"
    assert c1.subst(c1, c2) == c2
    assert c1.subst(c2, c1) == c1

    assert c1.is_alpha_equiv(Const("c")) is True
    assert c1.is_alpha_equiv(c2) is False
    assert c1.is_alpha_equiv(Var("c")) is False

    assert c1.match_instantiation(Const("c"), set()) is True
    assert c1.match_instantiation(Var("c"), set()) is False


def test_propvar():
    p1 = PropVar("P")
    assert p1._check_eq_subst(PropVar("P"), None, None) is True
    assert p1._check_eq_subst(PropVar("Q"), None, None) is False
    assert repr(p1) == "PropVar('P')"
    assert p1.subst(Var("x"), Var("y")) == p1

    assert p1.is_alpha_equiv(PropVar("P")) is True
    assert p1.is_alpha_equiv(PropVar("Q")) is False
    assert p1.is_alpha_equiv(Var("P")) is False

    assert p1.match_instantiation(PropVar("P"), set()) is True
    assert p1.match_instantiation(PropVar("Q"), set()) is False
    assert p1.match_instantiation(Var("P"), set()) is False


def test_func():
    v1, v2 = Var("x"), Var("y")
    f1 = Func("f", v1, v2)
    f2 = Func("f", v2, v1)
    f_empty = Func("h")

    assert f1.free_vars() == {"x", "y"}
    assert repr(f1) == "Func('f', Var('x'), Var('y'))"
    assert repr(f_empty) == "Func('h')"

    assert f1.subst(v1, Const("c")) == Func("f", Const("c"), v2)

    assert f1.is_alpha_equiv(Func("f", v2, v1), {"x": "y", "y": "x"}) is True
    assert f1.is_alpha_equiv(f2) is False
    assert f1.is_alpha_equiv(Func("g", v1, v2)) is False
    assert f1.is_alpha_equiv(Func("f", v1)) is False
    assert f1.is_alpha_equiv(Var("f")) is False

    assert f1.match_instantiation(f2, {"x", "y"}) is True
    assert f1.match_instantiation(Func("g", v1, v2), {"x", "y"}) is False
    assert f1.match_instantiation(Func("f", v1), {"x", "y"}) is False
    assert f1.match_instantiation(Var("f"), {"x", "y"}) is False

    assert f1._contains_children(v1) is True
    assert f1._contains_children(Const("c")) is False

    assert f1._check_eq_subst(Func("f", v1, v2), None, None) is True
    assert f1._check_eq_subst(Func("g", v1, v2), None, None) is False
    assert f1._check_eq_subst(Func("f", v1), None, None) is False
    assert f1._check_eq_subst(Func("f", Const("c"), v2), None, None) is False


def test_predicate():
    v1 = Var("x")
    p1 = Predicate("P", v1)
    p_empty = Predicate("E")
    p_2args = Predicate("P", v1, v1)

    assert p1.free_vars() == {"x"}
    assert repr(p1) == "Predicate('P', Var('x'))"
    assert repr(p_empty) == "Predicate('E')"

    assert p1.subst(v1, Const("c")) == Predicate("P", Const("c"))

    assert p1.is_alpha_equiv(p1) is True
    assert p1.is_alpha_equiv(Predicate("P", Var("y")), {"x": "y"}) is True
    assert p1.is_alpha_equiv(Predicate("Q", v1)) is False
    assert p1.is_alpha_equiv(p_empty) is False
    assert p1.is_alpha_equiv(Var("P")) is False

    assert p1.is_alpha_equiv(p_2args) is False

    assert p1.is_alpha_equiv(Predicate("P", Const("c"))) is False

    assert p1.match_instantiation(Predicate("P", Const("c")), {"x"}) is True
    assert p1.match_instantiation(Predicate("Q", v1), {"x"}) is False
    assert p1.match_instantiation(p_empty, {"x"}) is False
    assert p1.match_instantiation(Var("P"), {"x"}) is False

    assert p1.match_instantiation(p_2args, {"x"}) is False

    assert p1.match_instantiation(Predicate("P", Const("c")), set()) is False

    assert p1._contains_children(v1) is True
    assert p1._contains_children(Const("c")) is False

    assert p1._check_eq_subst(Predicate("P", v1), None, None) is True
    assert p1._check_eq_subst(Predicate("Q", v1), None, None) is False
    assert p1._check_eq_subst(p_empty, None, None) is False
    assert p1._check_eq_subst(Predicate("P", Const("c")), None, None) is False


def test_connective_init_and_props():
    v1, v2 = Var("x"), Var("y")

    with pytest.raises(ValueError, match="requires 2 arguments"):
        And(PropVar("P"))

    and_node = And(Predicate("P", v1), Predicate("Q", v2))
    assert and_node.free_vars() == {"x", "y"}
    assert repr(and_node) == "And(Predicate('P', Var('x')), Predicate('Q', Var('y')))"

    assert and_node._contains_children(v1) is True
    assert and_node._contains_children(Const("c")) is False

    assert and_node.subst(v1, Const("c")) == And(Predicate("P", Const("c")), Predicate("Q", v2))
    assert and_node._check_eq_subst(And(Predicate("P", v1), Predicate("Q", v2)), None, None) is True


def test_connective_alpha_and_match():
    p, q = PropVar("P"), PropVar("Q")
    and1 = And(p, q)
    and2 = And(p, q)
    or1 = Or(p, q)

    assert and1.is_alpha_equiv(and2) is True
    assert and1.is_alpha_equiv(or1) is False
    assert and1.is_alpha_equiv(PropVar("P")) is False
    assert And(p, p).is_alpha_equiv(And(p, q)) is False

    assert and1.match_instantiation(and2, set()) is True
    assert and1.match_instantiation(or1, set()) is False

    and_manipulated_len = And(p, q)
    object.__setattr__(and_manipulated_len, "args", (p,))
    assert and1.is_alpha_equiv(and_manipulated_len) is False
    assert and1.match_instantiation(and_manipulated_len, set()) is False
    assert and1._check_eq_subst(and_manipulated_len, None, None) is False

    and_manipulated_name = And(p, q)
    object.__setattr__(and_manipulated_name, "name", "FakeAnd")
    assert and1.is_alpha_equiv(and_manipulated_name) is False
    assert and1.match_instantiation(and_manipulated_name, set()) is False


def test_connective_subclasses_exist():
    p = PropVar("P")
    assert Not(p).arity == 1
    assert Or(p, p).arity == 2
    assert Implies(p, p).arity == 2
    assert CoImplies(p, p).arity == 2
    assert Falsum().arity == 0


def test_quantifiers():
    vx = Var("x")
    vy = Var("y")
    px = Predicate("P", vx)
    py = Predicate("P", vy)

    forall = ForAll(vx, px)
    exists = Exists(vx, px)

    assert forall.free_vars() == set()
    assert ForAll(vy, px).free_vars() == {"x"}

    assert repr(forall) == "ForAll(Var('x'), Predicate('P', Var('x')))"

    assert forall._contains_children(vx) is True
    assert forall._contains_children(px) is True

    assert forall.subst(vx, Const("c")) == forall
    assert ForAll(vy, px).subst(vx, Const("c")) == ForAll(vy, Predicate("P", Const("c")))

    assert forall.is_alpha_equiv(ForAll(vy, py)) is True
    assert forall.is_alpha_equiv(exists) is False
    assert forall.is_alpha_equiv(Var("x")) is False

    mapping = {}
    assert forall.match_instantiation(ForAll(vx, px), {"x"}, mapping) is True
    assert forall.match_instantiation(ForAll(vy, py), {"y"}, mapping) is False
    assert forall.match_instantiation(Exists(vx, px), {"x"}) is False

    assert forall._check_eq_subst(ForAll(vx, px), None, None) is True
    assert forall._check_eq_subst(ForAll(vy, px), None, None) is False


def test_subproof_and_justified_line():
    p = PropVar("P")
    line = JustifiedLine(p, "Premise")
    assert line.formula == p
    assert line.justification == "Premise"

    sp = Subproof(["c"], (1, 2), p, [p])
    assert sp.constants == ["c"]
    assert sp.lines_range == (1, 2)
    assert sp.assumption == p
    assert sp.lines == [p]


def test_formula_transformer():
    mock_and = MagicMock(return_value="AND_NODE")
    mock_not = MagicMock(return_value="NOT_NODE")
    mock_forall = MagicMock(return_value="FORALL_NODE")
    mock_false = MagicMock(return_value="FALSUM_NODE")

    symbol_map = {
        "∧": mock_and,
        "¬": mock_not,
        "∀": mock_forall,
        "⊥": mock_false
    }

    transformer = FormulaTransformer(symbol_map)

    assert transformer.bin_op(["arg1", "∧", "arg2"]) == "AND_NODE"
    mock_and.assert_called_with("arg1", "arg2")

    assert transformer.un_op(["¬", "arg"]) == "NOT_NODE"
    mock_not.assert_called_with("arg")

    assert transformer.nullary_op(["⊥"]) == "FALSUM_NODE"
    mock_false.assert_called_with()

    assert transformer.quantified(["∀", "x", "body"]) == "FORALL_NODE"
    call_args = mock_forall.call_args[0]
    assert isinstance(call_args[0], Var)
    assert call_args[0].name == "x"
    assert call_args[1] == "body"

    pred = transformer.pred(["P", "term1", "term2"])
    assert isinstance(pred, Predicate)
    assert pred.name == "P"
    assert pred.args == ("term1", "term2")

    eq = transformer.eq(["term1", "term2"])
    assert isinstance(eq, Predicate)
    assert eq.name == "="

    pv = transformer.prop_var(["P"])
    assert isinstance(pv, PropVar)
    assert pv.name == "P"

    v = transformer.var(["x"])
    assert isinstance(v, Var)
    assert v.name == "x"

    c = transformer.const(["c"])
    assert isinstance(c, Const)
    assert c.name == "c"

    f = transformer.func(["f", "t1", "t2"])
    assert isinstance(f, Func)
    assert f.name == "f"
    assert f.args == ("t1", "t2")
