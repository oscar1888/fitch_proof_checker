from fitch_proof_checker.model.logic.logic_factory import LogicFactory
from fitch_proof_checker.model.rule import (
    AndIntro, AndElim, OrIntro, OrElim, NotIntro, NotElim,
    FalsumIntro, FalsumElim, ImpliesIntro, ImpliesElim,
    CoImpliesIntro, CoImpliesElim, Reit, EqualsIntro,
    EqualsElim, ForAllIntro, ForAllElim, ExistsIntro, ExistsElim
)


def test_create_propositional_logic():
    manager = LogicFactory.create_propositional_logic()

    expected_rules = [
        AndIntro, AndElim, OrIntro, OrElim, NotIntro, NotElim,
        FalsumIntro, FalsumElim, ImpliesIntro, ImpliesElim,
        CoImpliesIntro, CoImpliesElim, Reit
    ]

    assert manager.rules == expected_rules
    assert len(manager.rules) == 13


def test_create_first_order_logic():
    manager = LogicFactory.create_first_order_logic()

    expected_pl_rules = [
        AndIntro, AndElim, OrIntro, OrElim, NotIntro, NotElim,
        FalsumIntro, FalsumElim, ImpliesIntro, ImpliesElim,
        CoImpliesIntro, CoImpliesElim, Reit
    ]

    expected_fol_rules = [
        EqualsIntro, EqualsElim, ForAllIntro, ForAllElim,
        ExistsIntro, ExistsElim
    ]

    expected_total_rules = expected_pl_rules + expected_fol_rules

    assert manager.rules == expected_total_rules
    assert len(manager.rules) == 19
