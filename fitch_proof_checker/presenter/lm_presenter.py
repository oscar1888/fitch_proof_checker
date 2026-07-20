import os
import importlib.util
from fitch_proof_checker.model.logic import LogicFactory


class LMPresenter:
    def __init__(self, view, model):
        self.model = model
        self.view = view
        self.view.add_presenter(self)

    def populate_list(self):
        self.view.rule_list.clear()
        for rule in self.model.logic_manager.rules:
            self.view.rule_list.addItem(f"{rule.name}")

    def get_rule_name(self, index) -> str:
        return self.model.logic_manager.rules[index].name

    def remove_rule(self, index):
        self.model.logic_manager.rules.pop(index)
        self.populate_list()
        self._update_main_label("Custom Logic")

    def add_rule(self, file_path) -> tuple[bool, str]:
        try:
            module_name = os.path.basename(file_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            custom_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom_module)

            if not hasattr(custom_module, 'CustomRule'):
                return False, "The Python file must contain a class named 'CustomRule'."

            new_rule = custom_module.CustomRule
            setattr(new_rule, '__plugin_path__', file_path)

            if not hasattr(new_rule, 'check') or not callable(getattr(new_rule, 'check')):
                return False, "The 'CustomRule' class must implement a 'check' method."

            if new_rule.name in [e.name for e in self.model.logic_manager.rules]:
                return False, f"The rule {new_rule.name} is already present"

            self.model.logic_manager.rules.append(new_rule)
            self.populate_list()
            self._update_main_label("Custom Logic")

            return True, f"Rule '{new_rule.name}' loaded successfully!"

        except Exception as e:
            return False, f"Failed to load custom rule:\n\n{str(e)}"

    def load_default_logic(self, preset_name):
        if "Propositional Logic" in preset_name:
            self.model.logic_manager = LogicFactory.create_propositional_logic()
        else:
            self.model.logic_manager = LogicFactory.create_first_order_logic()

        self.populate_list()
        self._update_main_label(preset_name)

    def load_profile(self, file_path) -> tuple[bool, str]:
        try:
            self.model.logic_manager.load_rules_from_json(file_path)
            self.populate_list()
            profile_name = os.path.basename(file_path).replace('.json', '')
            self._update_main_label(f"Profile: {profile_name}")
            return True, "Logic Profile loaded successfully."
        except Exception as e:
            return False, f"Failed to load profile:\n\n{str(e)}"

    def save_profile(self, file_path) -> tuple[bool, str]:
        try:
            self.model.logic_manager.save_rules_to_json(file_path)
            return True, "Logic Profile saved successfully."
        except Exception as e:
            return False, f"Failed to save profile:\n\n{str(e)}"

    def _update_main_label(self, text):
        if hasattr(self.view.parent(), 'logic_label'):
            self.view.parent().logic_label.setText(text)
