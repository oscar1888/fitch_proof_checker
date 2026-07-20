import importlib
import inspect
import json
import os
from lark import Lark
from fitch_proof_checker.model.formula.formula_transformer import FormulaTransformer


class GrammarManager:
    def __init__(self, connectives, quantifiers):
        self.connectives = connectives
        self.quantifiers = quantifiers
        self.formula_parser = self.create_formula_parser()

    def create_formula_parser(self) -> Lark:
        symbol_map = {}
        unary_ops, binary_ops, nullary_ops, nary_ops, quantifiers = [], [], [], [], []

        for conn in getattr(self, 'connectives', []):
            if getattr(conn, 'is_custom', False):
                lark_symbol = f"\\{conn.symbol}"
                symbol_map[lark_symbol] = conn
                nary_ops.append(f'"\\\\{conn.symbol}"')
            else:
                symbol_map[conn.symbol] = conn
                esc = f'"{conn.symbol}"'

                if conn.arity == 0:
                    nullary_ops.append(esc)
                elif conn.arity == 1:
                    unary_ops.append(esc)
                elif conn.arity == 2:
                    binary_ops.append(esc)

        for q in getattr(self, 'quantifiers', []):
            if getattr(q, 'is_custom', False):
                lark_symbol = f"\\{q.symbol}"
                symbol_map[lark_symbol] = q
                quantifiers.append(f'"\\\\{q.symbol}"')
            else:
                symbol_map[q.symbol] = q
                quantifiers.append(f'"{q.symbol}"')

        rule_nullary = " | ".join(nullary_ops) if nullary_ops else '"__NONE_NULLARY__"'
        rule_unary = " | ".join(unary_ops) if unary_ops else '"__NONE_UNARY__"'
        rule_nary = " | ".join(nary_ops) if nary_ops else '"__NONE_NARY__"'
        rule_quant = " | ".join(quantifiers) if quantifiers else '"__NONE_QUANT__"'

        bin_rules = []
        bin_alts = []
        bin_terminals = []

        for i, op in enumerate(binary_ops):
            rule_name = f"bin_rule_{i}"
            term_name = f"BIN_OP_{i}"

            bin_terminals.append(f"{term_name}: {op}")

            bin_rules.append(f"?{rule_name}: {rule_name} {term_name} formula_un -> bin_op")
            bin_rules.append(f"           | formula_un {term_name} formula_un -> bin_op")

            bin_alts.append(rule_name)

        formula_alternatives = " | ".join(bin_alts) + " | formula_un" if bin_alts else "formula_un"
        dynamic_binary_block = "\n    ".join(bin_rules)
        dynamic_terminals_block = "\n    ".join(bin_terminals)

        dynamic_grammar = f"""
            ?start: formula

            ?formula: {formula_alternatives}

            {dynamic_binary_block}

            ?formula_un: UNARY_OP formula_un -> un_op
                       | QUANTIFIER VAR_NAME formula_un -> quantified
                       | formula_atom

            ?formula_atom: term "=" term -> eq
                         | NARY_OP "(" formula ("," formula)* ")" -> nary_op
                         | PRED_NAME "(" term ("," term)* ")" -> pred
                         | PRED_NAME -> prop_var
                         | NULLARY_OP -> nullary_op
                         | "(" formula ")"
                         | "[" formula "]"
                         | "{{" formula "}}"

            ?term: FUNC_NAME "(" term ("," term)* ")" -> func
                 | FUNC_NAME -> const
                 | VAR_NAME -> var

            {dynamic_terminals_block}

            UNARY_OP: {rule_unary}
            NULLARY_OP: {rule_nullary}
            NARY_OP: {rule_nary}
            QUANTIFIER: {rule_quant}

            VAR_NAME: /[n-z]+/
            FUNC_NAME: /[a-m]+/
            PRED_NAME: /[A-Z][a-zA-Z]*/

            %import common.WS
            %ignore WS
            """

        parser = Lark(dynamic_grammar, parser='lalr', transformer=FormulaTransformer(symbol_map))

        def _parse_formula(text: str):
            if not text.strip(): return None
            ast = parser.parse(text)
            if ast.free_vars():
                raise ValueError(f"Free variables found ({', '.join(ast.free_vars())})")
            return ast

        return _parse_formula

    def save_vocabulary_to_json(self, file_path: str):
        def serialize_item(cls):
            data = {
                "class_name": cls.__name__
            }

            if cls.__name__ in ('CustomConnective', 'CustomQuantifier'):
                data["plugin_path"] = cls.__plugin_path__
            else:
                data["module"] = cls.__module__

            return data

        vocabulary = {
            "connectives": [serialize_item(c) for c in self.connectives],
            "quantifiers": [serialize_item(q) for q in self.quantifiers]
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(vocabulary, f, indent=4)

    def load_vocabulary_from_json(self, file_path: str):
        from fitch_proof_checker.model.grammar import GrammarFactory
        with open(file_path, "r", encoding="utf-8") as f:
            vocabulary = json.load(f)

        def deserialize_item(item_data):
            class_name = item_data["class_name"]

            if class_name in ('CustomConnective', 'CustomQuantifier'):
                plugin_path = item_data.get("plugin_path")
                if not plugin_path or not os.path.exists(plugin_path):
                    raise FileNotFoundError(f"Cannot find the custom plugin file: {plugin_path}")

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
                return getattr(module, class_name)

        loaded_connectives = [deserialize_item(c_data) for c_data in vocabulary.get("connectives", [])]
        loaded_quantifiers = [deserialize_item(q_data) for q_data in vocabulary.get("quantifiers", [])]

        fol_manager = GrammarFactory.create_first_order_logic()
        protected_connectives = {getattr(c, 'name', c.__name__): c for c in fol_manager.connectives}
        protected_quantifiers = {getattr(q, 'name', q.__name__): q for q in fol_manager.quantifiers}

        self.connectives = list(protected_connectives.values())
        self.quantifiers = list(protected_quantifiers.values())

        for c in loaded_connectives:
            c_name = getattr(c, 'name', c.__name__)
            if c_name not in protected_connectives and c not in self.connectives:
                self.connectives.append(c)

        for q in loaded_quantifiers:
            q_name = getattr(q, 'name', q.__name__)
            if q_name not in protected_quantifiers and q not in self.quantifiers:
                self.quantifiers.append(q)

        self.formula_parser = self.create_formula_parser()
