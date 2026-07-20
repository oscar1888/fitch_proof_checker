from fitch_proof_checker.model.grammar.grammar_factory import GrammarFactory
from fitch_proof_checker.model.logic.logic_factory import LogicFactory


class Model:
    def __init__(self):
        self.grammar_manager = GrammarFactory.create_first_order_logic()
        self.logic_manager = LogicFactory.create_first_order_logic()

    def check_step(self, ipp, cited_items, justified_line):
        try:
            rule = self.logic_manager.get_rule(justified_line.justification['rule_name'])
        except ValueError:
            raise ValueError('Unknown rule.')

        return rule.check(ipp, cited_items, justified_line.formula)
