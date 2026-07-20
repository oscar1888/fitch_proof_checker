import pytest
from unittest.mock import MagicMock
from fitch_proof_checker.model.model import Model


def test_model_init(mocker):
    mock_gf = mocker.patch('fitch_proof_checker.model.model.GrammarFactory.create_first_order_logic')
    mock_lf = mocker.patch('fitch_proof_checker.model.model.LogicFactory.create_first_order_logic')

    model = Model()

    mock_gf.assert_called_once()
    mock_lf.assert_called_once()
    assert model.grammar_manager == mock_gf.return_value
    assert model.logic_manager == mock_lf.return_value


def test_check_step_success(mocker):
    mocker.patch('fitch_proof_checker.model.model.GrammarFactory')
    mocker.patch('fitch_proof_checker.model.model.LogicFactory')

    model = Model()

    mock_rule = MagicMock()
    mock_rule.check.return_value = True
    model.logic_manager.get_rule = MagicMock(return_value=mock_rule)

    ipp = MagicMock()
    cited_items = [MagicMock(), MagicMock()]

    justified_line = MagicMock()
    justified_line.justification = {'rule_name': 'ValidRule'}
    justified_line.formula = MagicMock()

    result = model.check_step(ipp, cited_items, justified_line)

    model.logic_manager.get_rule.assert_called_once_with('ValidRule')
    mock_rule.check.assert_called_once_with(ipp, cited_items, justified_line.formula)
    assert result is True


def test_check_step_unknown_rule(mocker):
    mocker.patch('fitch_proof_checker.model.model.GrammarFactory')
    mocker.patch('fitch_proof_checker.model.model.LogicFactory')

    model = Model()

    model.logic_manager.get_rule = MagicMock(side_effect=ValueError("Original error message"))

    ipp = MagicMock()
    cited_items = []

    justified_line = MagicMock()
    justified_line.justification = {'rule_name': 'MissingRule'}

    with pytest.raises(ValueError, match='Unknown rule.'):
        model.check_step(ipp, cited_items, justified_line)

    model.logic_manager.get_rule.assert_called_once_with('MissingRule')
