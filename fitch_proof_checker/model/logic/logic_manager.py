import json
import inspect
import os
import importlib
import importlib.util


class LogicManager:
    def __init__(self, rules):
        self.rules = rules

    def get_rule(self, name):
        return self.rules[[r.name for r in self.rules].index(name)]

    def save_rules_to_json(self, file_path: str):
        def serialize_rule(rule):
            cls = rule
            data = {
                "class_name": cls.__name__
            }

            if cls.__name__ == 'CustomRule':
                data["plugin_path"] = cls.__plugin_path__
            else:
                data["module"] = cls.__module__

            return data

        rules_data = [serialize_rule(r) for r in self.rules]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(rules_data, f, indent=4)

    def load_rules_from_json(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            rules_data = json.load(f)

        def deserialize_rule(item_data):
            class_name = item_data["class_name"]

            if class_name == 'CustomRule':
                plugin_path = item_data.get("plugin_path")
                if not plugin_path or not os.path.exists(plugin_path):
                    raise FileNotFoundError(f"Cannot find the custom rule plugin file: {plugin_path}")

                module_name = os.path.basename(plugin_path).replace('.py', '')
                spec = importlib.util.spec_from_file_location(module_name, plugin_path)
                custom_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(custom_module)

                cls = getattr(custom_module, class_name)
                setattr(cls, '__plugin_path__', plugin_path)
                return cls
            else:
                module_name = item_data["module"]
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                return cls

        self.rules = [deserialize_rule(r_data) for r_data in rules_data]
