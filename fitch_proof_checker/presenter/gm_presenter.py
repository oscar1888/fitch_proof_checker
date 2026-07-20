import os
import importlib.util
from fitch_proof_checker.model.grammar import GrammarFactory


class GMPresenter:
    def __init__(self, view, model):
        self.model = model
        self.view = view
        self.view.add_presenter(self)

    def populate_list(self, item_type):
        if item_type == 'connective':
            self.view.list_connectives.clear()
            for conn in self.model.grammar_manager.connectives:
                self.view.list_connectives.addItem(f"{conn.name} ({conn.symbol})")
        elif item_type == 'quantifier':
            self.view.list_quantifiers.clear()
            for quant in self.model.grammar_manager.quantifiers:
                self.view.list_quantifiers.addItem(f"{quant.name} ({quant.symbol})")

    def get_item_name(self, item_type, index):
        target_list = (self.model.grammar_manager.connectives
                       if item_type == 'connective'
                       else self.model.grammar_manager.quantifiers)
        return target_list[index].name

    def is_protected_item(self, item_type, index) -> bool:
        item_name = self.get_item_name(item_type, index)

        FOL_grammar_manager = GrammarFactory.create_first_order_logic()
        PROTECTED_FOL_ITEMS = {e.name for e in FOL_grammar_manager.connectives + FOL_grammar_manager.quantifiers}

        return item_name in PROTECTED_FOL_ITEMS

    def remove_item(self, item_type, index):
        target_list = (self.model.grammar_manager.connectives
                       if item_type == 'connective'
                       else self.model.grammar_manager.quantifiers)
        target_list.pop(index)
        self.populate_list(item_type)
        self.model.grammar_manager.formula_parser = self.model.grammar_manager.create_formula_parser()

    def add_item(self, item_type, file_path) -> tuple[bool, str]:
        try:
            module_name = os.path.basename(file_path).replace('.py', '')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            custom_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(custom_module)

            expected_class = 'CustomConnective' if item_type == 'connective' else 'CustomQuantifier'

            if not hasattr(custom_module, expected_class):
                return False, f"The file must contain a class named '{expected_class}'."

            new_item = getattr(custom_module, expected_class)
            setattr(new_item, '__plugin_path__', file_path)

            if item_type == 'connective':
                self.model.grammar_manager.connectives.append(new_item)
            elif item_type == 'quantifier':
                self.model.grammar_manager.quantifiers.append(new_item)

            self.model.grammar_manager.formula_parser = self.model.grammar_manager.create_formula_parser()
            self.populate_list(item_type)
            return True, f"{item_type.capitalize()} '{new_item.name}' loaded successfully!"

        except Exception as e:
            return False, f"Failed to load {item_type}:\n\n{str(e)}"

    def load_default_grammar(self, preset_name):
        if "Propositional Logic" in preset_name:
            self.model.grammar_manager = GrammarFactory.create_propositional_logic()
        else:
            self.model.grammar_manager = GrammarFactory.create_first_order_logic()

        self.populate_list('connective')
        self.populate_list('quantifier')
        self.model.grammar_manager.formula_parser = self.model.grammar_manager.create_formula_parser()

    def load_profile(self, file_path) -> tuple[bool, str]:
        try:
            self.model.grammar_manager.load_vocabulary_from_json(file_path)
            self.populate_list('connective')
            self.populate_list('quantifier')
            return True, "Grammar Profile loaded successfully."
        except Exception as e:
            return False, f"Failed to load profile:\n\n{str(e)}"

    def save_profile(self, file_path) -> tuple[bool, str]:
        try:
            self.model.grammar_manager.save_vocabulary_to_json(file_path)
            return True, "Grammar Profile saved successfully."
        except Exception as e:
            return False, f"Failed to save profile:\n\n{str(e)}"
