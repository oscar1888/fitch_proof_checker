import json
import pytest
from unittest.mock import MagicMock
from fitch_proof_checker.model.grammar.grammar_manager import GrammarManager


class MockNullary:
    name = "Falsum"
    symbol = "⊥"
    arity = 0


class MockUnary:
    name = "Not"
    symbol = "¬"
    arity = 1


class MockBinary:
    name = "And"
    symbol = "∧"
    arity = 2


class CustomConnective:
    name = "MyConn"
    symbol = "C"
    is_custom = True


class MockQuantifier:
    name = "ForAll"
    symbol = "∀"


class CustomQuantifier:
    name = "MyQuant"
    symbol = "Q"
    is_custom = True


@pytest.fixture
def mock_lark(mocker):
    return mocker.patch('fitch_proof_checker.model.grammar.grammar_manager.Lark')


@pytest.fixture
def mock_transformer(mocker):
    return mocker.patch('fitch_proof_checker.model.grammar.grammar_manager.FormulaTransformer')


def test_create_formula_parser(mock_lark, mock_transformer):
    connectives = [MockNullary, MockUnary, MockBinary, CustomConnective]
    quantifiers = [MockQuantifier, CustomQuantifier]

    GrammarManager(connectives, quantifiers)

    mock_lark.assert_called_once()

    generated_grammar = mock_lark.call_args[0][0]
    assert '"⊥"' in generated_grammar
    assert '"¬"' in generated_grammar
    assert '"∧"' in generated_grammar
    assert '"\\\\C"' in generated_grammar
    assert '"∀"' in generated_grammar
    assert '"\\\\Q"' in generated_grammar


def test_create_formula_parser_empty(mock_lark, mock_transformer):
    GrammarManager([], [])

    generated_grammar = mock_lark.call_args[0][0]
    assert '"__NONE_NULLARY__"' in generated_grammar
    assert '"__NONE_QUANT__"' in generated_grammar


def test_parse_formula_success(mock_lark, mock_transformer):
    mock_ast = MagicMock()
    mock_ast.free_vars.return_value = set()
    mock_lark.return_value.parse.return_value = mock_ast

    gm = GrammarManager([], [])

    result = gm.formula_parser("valid formula")
    assert result == mock_ast


def test_parse_formula_empty_string(mock_lark, mock_transformer):
    gm = GrammarManager([], [])
    assert gm.formula_parser("   ") is None
    assert gm.formula_parser("") is None


def test_parse_formula_free_variables(mock_lark, mock_transformer):
    mock_ast = MagicMock()
    mock_ast.free_vars.return_value = {"x", "y"}
    mock_lark.return_value.parse.return_value = mock_ast

    gm = GrammarManager([], [])

    with pytest.raises(ValueError, match="Free variables found"):
        gm.formula_parser("P(x)")


def test_save_vocabulary_to_json(tmp_path, mock_lark, mock_transformer, mocker):
    CustomConnective.__plugin_path__ = "/fake/path/plugin.py"
    CustomQuantifier.__plugin_path__ = "/fake/path/plugin.py"

    gm = GrammarManager([MockBinary, CustomConnective], [CustomQuantifier])

    file_path = tmp_path / "vocab.json"
    gm.save_vocabulary_to_json(str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["connectives"][0] == {"class_name": "MockBinary", "module": MockBinary.__module__}
    assert data["connectives"][1] == {"class_name": "CustomConnective", "plugin_path": "/fake/path/plugin.py"}
    assert data["quantifiers"][0] == {"class_name": "CustomQuantifier", "plugin_path": "/fake/path/plugin.py"}


def test_load_vocabulary_success(tmp_path, mock_lark, mock_transformer, mocker):
    plugin_file = tmp_path / "custom_plugin.py"
    plugin_file.write_text("""
class CustomConnective:
    name = "LoadedCustomConn"
    symbol = "C"
    is_custom = True

class CustomQuantifier:
    name = "LoadedCustomQuant"
    symbol = "Q"
    is_custom = True
""")

    json_data = {
        "connectives": [
            {"class_name": "MockBinary", "module": "test_grammar_manager"},
            {"class_name": "CustomConnective", "plugin_path": str(plugin_file)}
        ],
        "quantifiers": [
            {"class_name": "CustomQuantifier", "plugin_path": str(plugin_file)}
        ]
    }
    json_file = tmp_path / "vocab.json"
    json_file.write_text(json.dumps(json_data))

    mock_fol_manager = MagicMock()
    mock_fol_manager.connectives = [MockNullary]
    mock_fol_manager.quantifiers = [MockQuantifier]
    mocker.patch(
        'fitch_proof_checker.model.grammar.grammar_factory.GrammarFactory.create_first_order_logic',
        return_value=mock_fol_manager
    )

    import sys
    mocker.patch('importlib.import_module', return_value=sys.modules[__name__])

    gm = GrammarManager([], [])
    gm.load_vocabulary_from_json(str(json_file))

    conn_names = [getattr(c, 'name', getattr(c, '__name__', '')) for c in gm.connectives]
    quant_names = [getattr(q, 'name', getattr(q, '__name__', '')) for q in gm.quantifiers]

    assert "Falsum" in conn_names
    assert "And" in conn_names
    assert "LoadedCustomConn" in conn_names

    assert "ForAll" in quant_names
    assert "LoadedCustomQuant" in quant_names

    assert mock_lark.call_count == 2


def test_load_vocabulary_missing_plugin(tmp_path, mock_lark, mock_transformer, mocker):
    json_data = {
        "connectives": [
            {"class_name": "CustomConnective", "plugin_path": "/path/that/does/not/exist.py"}
        ]
    }
    json_file = tmp_path / "vocab.json"
    json_file.write_text(json.dumps(json_data))

    gm = GrammarManager([], [])

    with pytest.raises(FileNotFoundError, match="Cannot find the custom plugin file"):
        gm.load_vocabulary_from_json(str(json_file))
