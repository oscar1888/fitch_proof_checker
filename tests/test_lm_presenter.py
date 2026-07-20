import pytest
from unittest.mock import MagicMock

from fitch_proof_checker.model.logic.logic_manager import LogicManager
from fitch_proof_checker.presenter.lm_presenter import LMPresenter


@pytest.fixture
def view():
    v = MagicMock()
    v.rule_list = MagicMock()

    parent_mock = MagicMock()
    parent_mock.logic_label = MagicMock()
    v.parent.return_value = parent_mock

    return v


@pytest.fixture
def model():
    m = MagicMock()

    rule = MagicMock()
    rule.name = "AndIntro"

    m.logic_manager.rules = [rule]

    return m


@pytest.fixture
def presenter(view, model):
    return LMPresenter(view, model)


def test_init(view, model):
    pres = LMPresenter(view, model)
    assert pres.model == model
    assert pres.view == view
    view.add_presenter.assert_called_once_with(pres)


def test_populate_list(presenter, view):
    presenter.populate_list()

    view.rule_list.clear.assert_called_once()
    view.rule_list.addItem.assert_called_once_with("AndIntro")


def test_update_main_label_with_label(presenter, view):
    presenter._update_main_label("New Logic")
    view.parent().logic_label.setText.assert_called_once_with("New Logic")


def test_update_main_label_without_label(presenter, view):
    del view.parent().logic_label

    presenter._update_main_label("New Logic")


def test_get_rule_name(presenter):
    assert presenter.get_rule_name(0) == "AndIntro"


def test_remove_rule(presenter, mocker):
    mocker.patch.object(presenter, 'populate_list')
    mocker.patch.object(presenter, '_update_main_label')

    initial_len = len(presenter.model.logic_manager.rules)

    presenter.remove_rule(0)

    assert len(presenter.model.logic_manager.rules) == initial_len - 1
    presenter.populate_list.assert_called_once()
    presenter._update_main_label.assert_called_once_with("Custom Logic")


def test_add_rule_success(presenter, tmp_path, mocker):
    mocker.patch.object(presenter, 'populate_list')
    mocker.patch.object(presenter, '_update_main_label')

    plugin_file = tmp_path / "valid_rule.py"
    plugin_file.write_text("""
class CustomRule:
    name = 'MySuperRule'
    def check(self):
        return True
""")

    success, msg = presenter.add_rule(str(plugin_file))

    assert success is True
    assert "loaded successfully!" in msg
    assert len(presenter.model.logic_manager.rules) == 2
    presenter.populate_list.assert_called_once()
    presenter._update_main_label.assert_called_once_with("Custom Logic")


def test_add_rule_missing_class(presenter, tmp_path):
    plugin_file = tmp_path / "bad_rule1.py"
    plugin_file.write_text("class WrongName:\n    pass\n")

    success, msg = presenter.add_rule(str(plugin_file))

    assert success is False
    assert "must contain a class named 'CustomRule'" in msg


def test_add_rule_missing_check_method(presenter, tmp_path):
    plugin_file = tmp_path / "bad_rule2.py"
    plugin_file.write_text("class CustomRule:\n    name = 'NoCheck'\n")

    success, msg = presenter.add_rule(str(plugin_file))

    assert success is False
    assert "must implement a 'check' method" in msg


def test_add_rule_exception(presenter):
    success, msg = presenter.add_rule("/percorso/finto/file.py")

    assert success is False
    assert "Failed to load custom rule" in msg


def test_load_default_logic(presenter, mocker):
    mock_pl = ["PL_Rule1", "PL_Rule2"]
    mock_fol = ["FOL_Rule1"]

    mocker.patch('fitch_proof_checker.presenter.lm_presenter.LogicFactory.create_propositional_logic',
                 return_value=LogicManager(mock_pl))
    mocker.patch('fitch_proof_checker.presenter.lm_presenter.LogicFactory.create_first_order_logic',
                 return_value=LogicManager(mock_fol))
    mocker.patch.object(presenter, 'populate_list')
    mocker.patch.object(presenter, '_update_main_label')

    presenter.load_default_logic("Propositional Logic (PL)")
    assert presenter.model.logic_manager.rules == mock_pl
    presenter._update_main_label.assert_called_with("Propositional Logic (PL)")

    presenter.load_default_logic("First-Order Logic (FOL)")
    assert presenter.model.logic_manager.rules == mock_fol
    presenter._update_main_label.assert_called_with("First-Order Logic (FOL)")

    assert presenter.populate_list.call_count == 2


def test_load_profile_success(presenter, mocker):
    mocker.patch.object(presenter, 'populate_list')
    mocker.patch.object(presenter, '_update_main_label')

    success, msg = presenter.load_profile("/path/to/my_logic.json")

    assert success is True
    presenter.model.logic_manager.load_rules_from_json.assert_called_once_with("/path/to/my_logic.json")
    presenter.populate_list.assert_called_once()
    presenter._update_main_label.assert_called_once_with("Profile: my_logic")


def test_load_profile_exception(presenter):
    presenter.model.logic_manager.load_rules_from_json.side_effect = Exception("Format Error")

    success, msg = presenter.load_profile("logic.json")

    assert success is False
    assert "Format Error" in msg


def test_save_profile_success(presenter):
    success, msg = presenter.save_profile("out_logic.json")

    assert success is True
    presenter.model.logic_manager.save_rules_to_json.assert_called_once_with("out_logic.json")


def test_save_profile_exception(presenter):
    presenter.model.logic_manager.save_rules_to_json.side_effect = Exception("Disk Full")

    success, msg = presenter.save_profile("out_logic.json")

    assert success is False
    assert "Disk Full" in msg
