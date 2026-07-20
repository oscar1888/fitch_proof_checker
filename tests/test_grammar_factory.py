from fitch_proof_checker.model.grammar.grammar_factory import GrammarFactory, FOL_connectives, FOL_quantifiers


def test_create_propositional_logic(mocker):
    mock_gm_class = mocker.patch('fitch_proof_checker.model.grammar.grammar_factory.GrammarManager')

    result = GrammarFactory.create_propositional_logic()

    mock_gm_class.assert_called_once_with(FOL_connectives, [])
    assert result == mock_gm_class.return_value


def test_create_first_order_logic(mocker):
    mock_gm_class = mocker.patch('fitch_proof_checker.model.grammar.grammar_factory.GrammarManager')

    result = GrammarFactory.create_first_order_logic()

    mock_gm_class.assert_called_once_with(FOL_connectives, FOL_quantifiers)
    assert result == mock_gm_class.return_value
