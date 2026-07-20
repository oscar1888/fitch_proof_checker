import json
import pytest
from fitch_proof_checker.model.logic.logic_manager import LogicManager


class MockStandardRule:
    name = "StandardRule"


class CustomRule:
    name = "MyCustomRule"


def test_init_and_get_rule():
    rule1 = MockStandardRule()
    rule2 = CustomRule()

    manager = LogicManager([rule1, rule2])

    assert len(manager.rules) == 2

    retrieved = manager.get_rule("MyCustomRule")
    assert retrieved == rule2

    with pytest.raises(ValueError):
        manager.get_rule("NonExistentRule")


import json


def test_save_rules_to_json(tmp_path, mocker):
    mocker.patch('inspect.getfile', return_value="/fake/path/to/plugin.py")

    CustomRule.__plugin_path__ = "/fake/path/to/plugin.py"

    manager = LogicManager([MockStandardRule, CustomRule])

    file_path = tmp_path / "rules.json"
    manager.save_rules_to_json(str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 2

    assert data[0]["class_name"] == "MockStandardRule"
    assert "module" in data[0]
    assert data[0]["module"] == MockStandardRule.__module__

    assert data[1]["class_name"] == "CustomRule"
    assert data[1]["plugin_path"] == "/fake/path/to/plugin.py"
    assert "module" not in data[1]


def test_load_rules_from_json_success(tmp_path, mocker):
    plugin_file = tmp_path / "custom_rule_plugin.py"
    plugin_file.write_text("""
class CustomRule:
    name = "LoadedCustomRule"
""")

    json_data = [
        {"class_name": "MockStandardRule", "module": "test_logic_manager"},
        {"class_name": "CustomRule", "plugin_path": str(plugin_file)}
    ]
    json_file = tmp_path / "rules.json"
    json_file.write_text(json.dumps(json_data))

    import sys
    mocker.patch('importlib.import_module', return_value=sys.modules[__name__])

    manager = LogicManager([])
    manager.load_rules_from_json(str(json_file))

    assert len(manager.rules) == 2

    rule_classes = manager.rules

    assert rule_classes[0].__name__ == "MockStandardRule"
    assert rule_classes[1].__name__ == "CustomRule"
    assert rule_classes[1].name == "LoadedCustomRule"


def test_load_rules_missing_plugin(tmp_path):
    json_data = [
        {"class_name": "CustomRule", "plugin_path": "/percorso/inesistente/plugin.py"}
    ]
    json_file = tmp_path / "rules.json"
    json_file.write_text(json.dumps(json_data))

    manager = LogicManager([])

    with pytest.raises(FileNotFoundError, match="Cannot find the custom rule plugin file"):
        manager.load_rules_from_json(str(json_file))
