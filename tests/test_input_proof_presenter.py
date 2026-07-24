import pytest
from unittest.mock import MagicMock
from lark.exceptions import LarkError
from fitch_proof_checker.model.formula import Subproof
from fitch_proof_checker.model.parse_error import ParseError
from fitch_proof_checker.presenter.input_proof_presenter import InputProofPresenter


class DummyLine:
    def __init__(self, formula="", just="", depth=0, is_assump=False, arb_consts=None, line_number=1):
        self.formula_field = MagicMock()
        self.formula_field.text.return_value = formula

        self.justification_field = MagicMock()
        self.justification_field.text.return_value = just

        self.line_number_label = MagicMock()
        self.line_number_label.text.return_value = str(line_number)

        self.depth = depth
        self.is_assump = is_assump
        self.arb_consts_introduced = arb_consts or []
        self.status_dot = MagicMock()


@pytest.fixture
def fpe_window(mocker):
    window = MagicMock()
    window.log_console = MagicMock()
    window.goal_field = MagicMock()
    window.goal_status_dot = MagicMock()
    window.proof_layout = MagicMock()
    return window


@pytest.fixture
def model(mocker):
    m = MagicMock()
    m.grammar_manager.formula_parser = MagicMock()
    m.check_step.return_value = True
    return m


@pytest.fixture
def presenter():
    ipp = MagicMock()
    ipp.fpe_main_window = MagicMock()
    ipp.fpe_main_window.goal_status_dot = MagicMock()
    ipp.fpe_main_window.log_console = MagicMock()
    return ipp


def test_constant_occurs_outside_subproof(presenter, mocker):
    line1 = DummyLine("P", line_number=1)
    line2 = DummyLine("Q", line_number=2)
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=[line1, line2])

    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.find_final_subproof_idx', return_value=2)

    ast_mock = MagicMock()
    ast_mock.contains.return_value = True
    presenter.model.grammar_manager.formula_parser.return_value = ast_mock

    result = InputProofPresenter.constant_occurs_outside_subproof(presenter, "c", (2, 2))
    assert result is True


def test_parse_formula_success(presenter):
    line = DummyLine("P")
    presenter.model.grammar_manager.formula_parser.return_value = "AST"
    assert InputProofPresenter._parse_formula(presenter, line) == "AST"


def test_parse_formula_errors(presenter):
    line = DummyLine("P")

    class MockLarkError(LarkError):
        def get_context(self, text):
            return "mocked context error line"

    presenter.model.grammar_manager.formula_parser.side_effect = MockLarkError("syntax")
    with pytest.raises(ParseError, match="Syntax error"):
        InputProofPresenter._parse_formula(presenter, line)

    presenter.model.grammar_manager.formula_parser.side_effect = ValueError("bad value")
    with pytest.raises(ParseError, match="Syntax error"):
        InputProofPresenter._parse_formula(presenter, line)


def test_parse_justification(mocker):
    line = DummyLine(just="AndIntro 1,2")
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.parse_justification', return_value="JUST_AST")
    assert InputProofPresenter._parse_justification(line) == "JUST_AST"

    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.parse_justification',
                 side_effect=LarkError("bad"))
    with pytest.raises(ParseError, match="Justification syntax error"):
        InputProofPresenter._parse_justification(line)


def test_parse_single_cited_line_bounds():
    with pytest.raises(ValueError, match="out of bounds"):
        InputProofPresenter._parse_single_cited_line(5, [], 2, DummyLine(), 0, None, [])


def test_parse_single_cited_line_future():
    with pytest.raises(ValueError, match="future or current"):
        InputProofPresenter._parse_single_cited_line(2, [DummyLine(), DummyLine()], 1, DummyLine(), 0, None, [])


def test_parse_single_cited_line_trapped():
    all_lines = [DummyLine(depth=1), DummyLine(depth=0)]
    with pytest.raises(ValueError, match="trapped inside a closed"):
        InputProofPresenter._parse_single_cited_line(1, all_lines, 1, all_lines[1], 0, None, [])


def test_parse_single_cited_line_subproof_closed():
    all_lines = [DummyLine(depth=1), DummyLine(depth=0), DummyLine(depth=1)]
    with pytest.raises(ValueError, match="has been closed"):
        InputProofPresenter._parse_single_cited_line(1, all_lines, 2, all_lines[2], 0, None, [])


def test_parse_single_cited_line_parallel():
    all_lines = [DummyLine(depth=1), DummyLine(depth=1, is_assump=True), DummyLine(depth=1)]
    with pytest.raises(ValueError, match="parallel subproof"):
        InputProofPresenter._parse_single_cited_line(1, all_lines, 2, all_lines[2], 0, None, [])


def test_parse_single_cited_line_success():
    all_lines = [DummyLine("P", depth=0), DummyLine("Q", depth=0)]
    parser = MagicMock(return_value="AST")
    cited = []
    InputProofPresenter._parse_single_cited_line(1, all_lines, 1, all_lines[1], 0, parser, cited)
    assert cited == ["AST"]


def test_parse_single_cited_line_lark_error():
    all_lines = [DummyLine("P", depth=0), DummyLine("Q", depth=0)]
    parser = MagicMock(side_effect=LarkError("err"))
    with pytest.raises(ValueError, match="Syntax error in the formula at cited line 1."):
        InputProofPresenter._parse_single_cited_line(1, all_lines, 1, all_lines[1], 0, parser, [])


def test_parse_cited_subproof_errors(presenter, mocker):
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.find_final_subproof_idx', return_value=1)
    all_lines = [DummyLine("A", depth=1, is_assump=True), DummyLine("B", depth=1)]
    parser = MagicMock()

    with pytest.raises(ValueError, match="out of bounds"):
        InputProofPresenter._parse_cited_subproof(presenter, (1, 5), all_lines, 2, DummyLine(), parser, [])

    with pytest.raises(ValueError, match="future or current"):
        InputProofPresenter._parse_cited_subproof(presenter, (1, 2), all_lines, 1, DummyLine(), parser, [])

    with pytest.raises(ValueError, match="Invalid interval"):
        InputProofPresenter._parse_cited_subproof(presenter, (2, 1), all_lines, 3, DummyLine(), parser, [])

    bad_lines = [DummyLine("A", depth=1, is_assump=True), DummyLine("B", depth=2)]
    with pytest.raises(ValueError, match="misaligned"):
        InputProofPresenter._parse_cited_subproof(presenter, (1, 2), bad_lines, 3, DummyLine(), parser, [])

    not_assump = [DummyLine("A", depth=1, is_assump=False), DummyLine("B", depth=1)]
    with pytest.raises(ValueError, match="not an assumption"):
        InputProofPresenter._parse_cited_subproof(presenter, (1, 2), not_assump, 3, DummyLine(), parser, [])

    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.find_final_subproof_idx', return_value=2)
    with pytest.raises(ValueError, match="Partial citation"):
        InputProofPresenter._parse_cited_subproof(presenter, (1, 2), all_lines, 3, DummyLine(), parser, [])

    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.find_final_subproof_idx', return_value=1)
    with pytest.raises(ValueError, match="not accessible"):
        InputProofPresenter._parse_cited_subproof(presenter, (1, 2), all_lines, 3, DummyLine(depth=5), parser, [])


def test_parse_cited_subproof_success(presenter, mocker):
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.find_final_subproof_idx', return_value=1)
    all_lines = [DummyLine("A", depth=1, is_assump=True), DummyLine("B", depth=1)]
    parser = MagicMock(return_value="AST")
    cited = []
    InputProofPresenter._parse_cited_subproof(presenter, (1, 2), all_lines, 2, DummyLine(depth=0), parser, cited)
    assert len(cited) == 1
    assert isinstance(cited[0], Subproof)


def test_parse_cited_subproof_lark_error(presenter, mocker):
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.find_final_subproof_idx', return_value=1)
    all_lines = [DummyLine("A", depth=1, is_assump=True), DummyLine("B", depth=1)]
    parser = MagicMock(side_effect=LarkError("err"))
    with pytest.raises(ValueError, match="Syntax error inside the formula at line 1."):
        InputProofPresenter._parse_cited_subproof(presenter, (1, 2), all_lines, 2, DummyLine(depth=0), parser, [])


def test_parse_cited_lines(presenter, mocker):
    current_line = DummyLine()
    parsed_just = {'references': [(1, 2), 3]}
    all_lines = [DummyLine(), current_line, DummyLine(), DummyLine()]
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=all_lines)
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_premises', return_value=[])

    presenter._parse_cited_subproof = MagicMock()
    mock_single = mocker.patch.object(InputProofPresenter, '_parse_single_cited_line')

    InputProofPresenter._parse_cited_lines(presenter, current_line, parsed_just)
    presenter._parse_cited_subproof.assert_called_once()
    mock_single.assert_called_once()


def test_parse_cited_lines_value_error(presenter, mocker):
    current_line = DummyLine()
    parsed_just = {'references': [3]}
    all_lines = [DummyLine(), current_line, DummyLine(), DummyLine()]
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=all_lines)
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_premises', return_value=[])
    mocker.patch.object(InputProofPresenter, '_parse_single_cited_line', side_effect=ValueError("TestError"))

    with pytest.raises(ParseError, match="Citation error: TestError"):
        InputProofPresenter._parse_cited_lines(presenter, current_line, parsed_just)


def test_check_step(presenter, mocker):
    from fitch_proof_checker.view.proof_layout.proof_line_view import ProofLine

    mock_qapp = mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.QApplication')
    mock_qapp.instance.return_value.focusWidget.return_value = None

    InputProofPresenter.check_step(presenter)

    widget = MagicMock(spec=ProofLine)
    line = MagicMock()
    widget.proof_line = line
    line.is_assump = True

    mock_qapp.instance.return_value.focusWidget.return_value = widget

    InputProofPresenter.check_step(presenter)

    line.is_assump = False

    presenter._parse_formula.return_value = "AST"
    presenter._parse_cited_lines.return_value = []
    presenter.model.check_step.return_value = True

    mocker.patch.object(InputProofPresenter, '_parse_justification', return_value={"rule_name": "AndIntro"})

    presenter._set_line_feedback.side_effect = lambda l, v, m: InputProofPresenter._set_line_feedback(presenter, l, v,
                                                                                                      m)

    mock_set = mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.set_status')

    InputProofPresenter.check_step(presenter)
    mock_set.assert_called_with(line.status_dot, True)

    presenter._parse_formula.side_effect = ParseError("err")
    InputProofPresenter.check_step(presenter)
    mock_set.assert_called_with(line.status_dot, False)


def test_check_proof_valid_and_invalid(presenter, mocker):
    line1 = DummyLine("A", is_assump=True)
    line2 = DummyLine("A", just="Reit 1")
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=[line1, line2])

    presenter._parse_formula.return_value = "GOAL_AST"
    presenter._parse_justification.return_value = {"rule": "Reit"}
    presenter._parse_cited_lines.return_value = []
    presenter.model.grammar_manager.formula_parser.return_value = "GOAL_AST"
    presenter.model.check_step.return_value = True

    InputProofPresenter.check_proof(presenter)

    presenter.model.check_step.return_value = False
    InputProofPresenter.check_proof(presenter)
    assert "Invalid application" in presenter.fpe_main_window.log_console.setText.call_args[0][0]

    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=[line1])
    InputProofPresenter.check_proof(presenter)
    assert "at least one derived step" in presenter.fpe_main_window.log_console.setText.call_args[0][0]


def test_check_proof_goal_none(presenter, mocker):
    line1 = DummyLine("A", is_assump=True)
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines',
                 return_value=[line1, DummyLine("A", just="Reit 1")])
    presenter._parse_formula.return_value = "AST"
    presenter._parse_justification.return_value = {"rule": "Reit"}
    presenter._parse_cited_lines.return_value = []
    presenter.model.check_step.return_value = True

    presenter.model.grammar_manager.formula_parser.return_value = None
    mock_set = mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.set_status')

    InputProofPresenter.check_proof(presenter)
    mock_set.assert_any_call(presenter.fpe_main_window.goal_status_dot, None)


def test_check_proof_goal_mismatch_or_depth(presenter, mocker):
    line1 = DummyLine("A", is_assump=True)
    line2 = DummyLine("B", just="Reit 1")
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=[line1, line2])
    presenter._parse_formula.return_value = "AST_B"
    presenter._parse_justification.return_value = {"rule": "Reit"}
    presenter._parse_cited_lines.return_value = []
    presenter.model.check_step.return_value = True

    presenter.model.grammar_manager.formula_parser.return_value = "AST_GOAL"
    mock_set = mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.set_status')

    InputProofPresenter.check_proof(presenter)
    mock_set.assert_any_call(presenter.fpe_main_window.goal_status_dot, False)

    line2.depth = 1
    presenter.model.grammar_manager.formula_parser.return_value = "AST_B"
    InputProofPresenter.check_proof(presenter)
    mock_set.assert_any_call(presenter.fpe_main_window.goal_status_dot, False)


def test_serialize_proof(presenter, mocker):
    line1 = DummyLine("P", is_assump=True, depth=0)
    line2 = DummyLine("Q", just="Rule", is_assump=False, depth=0, arb_consts=["a"])
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=[line1, line2])

    presenter.fpe_main_window.goal_field.text.return_value = "Goal"

    data = InputProofPresenter.serialize_proof(presenter)

    assert data["goal"] == "Goal"
    assert data["lines"][0]["formula"] == "P"
    assert data["lines"][0]["justification"] is None
    assert data["lines"][1]["justification"] == "Rule"
    assert data["lines"][1]["arb_consts_introduced"] == ["a"]


def test_deserialize_proof(presenter, mocker):
    proof_data = {
        "goal": "Q",
        "lines": [
            {"formula": "P", "is_assump": True, "depth": 0},
            {"formula": "Q", "justification": "Rule", "is_assump": False, "depth": 0, "arb_consts_introduced": ["a"]}
        ]
    }

    mock_layout = presenter.fpe_main_window.proof_layout
    mock_item = MagicMock()
    mock_widget = MagicMock()
    mock_item.widget.return_value = mock_widget
    mock_layout.count.side_effect = [1, 0]
    mock_layout.takeAt.return_value = mock_item

    mocker.patch('fitch_proof_checker.view.proof_layout.proof_line_view.ProofLine')
    mocker.patch('PyQt6.QtWidgets.QLabel')
    mocker.patch('fitch_proof_checker.view.proof_layout.proof_layout.update_layout')

    InputProofPresenter.deserialize_proof(presenter, proof_data)

    mock_widget.deleteLater.assert_called_once()
    presenter.fpe_main_window.goal_field.setText.assert_called_with("Q")
    assert mock_layout.addWidget.call_count == 2


def test_init():
    fpe_main_window = MagicMock()
    model = MagicMock()

    presenter = InputProofPresenter(fpe_main_window, model)

    assert presenter.fpe_main_window == fpe_main_window
    assert presenter.model == model
    fpe_main_window.add_input_proof_presenter.assert_called_once_with(presenter)


def test_constant_occurs_outside_subproof_exceptions(presenter, mocker):
    line1 = DummyLine("BAD_SYNTAX")
    line2 = DummyLine("P")
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=[line1, line2])

    ast_mock = MagicMock()
    ast_mock.contains.return_value = False

    presenter.model.grammar_manager.formula_parser.side_effect = [LarkError("err"), ast_mock]

    result = InputProofPresenter.constant_occurs_outside_subproof(presenter, "c", (3, 3))

    assert result is False


def test_check_proof_goal_lark_error(presenter, mocker):
    line1 = DummyLine("A", is_assump=True)
    line2 = DummyLine("A", just="Reit 1")
    mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.get_all_lines', return_value=[line1, line2])

    presenter._parse_formula.return_value = "AST"
    presenter._parse_justification.return_value = {"rule": "Reit"}
    presenter._parse_cited_lines.return_value = []
    presenter.model.check_step.return_value = True

    presenter.model.grammar_manager.formula_parser.side_effect = LarkError("mocked goal syntax error")
    mock_set = mocker.patch('fitch_proof_checker.presenter.input_proof_presenter.set_status')

    InputProofPresenter.check_proof(presenter)

    mock_set.assert_any_call(presenter.fpe_main_window.goal_status_dot, False)
    presenter.fpe_main_window.log_console.setText.assert_any_call("Goal Syntax Error:\n\tmocked goal syntax error")
