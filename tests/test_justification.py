import pytest
from lark.exceptions import LarkError
from fitch_proof_checker.model.parse_error import ParseError
from fitch_proof_checker.model.justification import parse_justification


def test_parse_empty_justification():
    with pytest.raises(ParseError, match="Empty justification"):
        parse_justification("")

    with pytest.raises(ParseError, match="Empty justification"):
        parse_justification("   \t  \n ")


def test_parse_invalid_syntax():
    invalid_inputs = [
        "123Rule",
        "AndIntro 1-",
        "AndIntro 1,,2",
        "AndIntro -5",
        "Rule 1.5",
    ]
    for text in invalid_inputs:
        with pytest.raises(LarkError):
            parse_justification(text)


def test_parse_rule_only():
    result = parse_justification("Premise")
    assert result == {
        'rule_name': 'Premise',
        'references': None
    }


def test_parse_single_line():
    result = parse_justification("Reit 5")
    assert result == {
        'rule_name': 'Reit',
        'references': [5]
    }


def test_parse_multiple_lines():
    result = parse_justification("AndIntro 1, 2, 3")
    assert result == {
        'rule_name': 'AndIntro',
        'references': [1, 2, 3]
    }

    result_no_spaces = parse_justification("AndIntro 1,2,3")
    assert result == result_no_spaces


def test_parse_subproof_range():
    result = parse_justification("ImpliesIntro 4-7")
    assert result == {
        'rule_name': 'ImpliesIntro',
        'references': [(4, 7)]
    }


def test_parse_mixed_references():
    result = parse_justification("OrElim 1, 2-4, 5, 6-8")
    assert result == {
        'rule_name': 'OrElim',
        'references': [1, (2, 4), 5, (6, 8)]
    }


def test_parse_rule_name_special_characters():
    result = parse_justification("Rule_With_Underscore 1")
    assert result == {
        'rule_name': 'Rule_With_Underscore',
        'references': [1]
    }

    result = parse_justification("∀-Intro 2-4")
    assert result == {
        'rule_name': '∀-Intro',
        'references': [(2, 4)]
    }
