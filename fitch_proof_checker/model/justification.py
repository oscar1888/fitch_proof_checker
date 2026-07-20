from lark import Lark, Transformer
from fitch_proof_checker.model.parse_error import ParseError

justification_grammar = """
?start: justification

justification: rule_name [arguments]

rule_name: /[^\d\s,][^\s,]*/

arguments: reference ("," reference)*

?reference: single_line | subproof_range

single_line: INT
subproof_range: INT "-" INT

%import common.INT
%import common.WS
%ignore WS
"""


class JustificationTransformer(Transformer):
    def single_line(self, args):
        return int(args[0])

    def subproof_range(self, args):
        start, end = int(args[0]), int(args[1])
        return (start, end)

    def arguments(self, args):
        return list(args)

    def rule_name(self, args):
        return str(args[0])

    def justification(self, args):
        rule = args[0]
        refs = args[1] if len(args) > 1 else []
        return {
            'rule_name': rule,
            'references': refs
        }


justification_parser = Lark(
    justification_grammar,
    parser='lalr',
    transformer=JustificationTransformer()
)


def parse_justification(text: str):
    if not text.strip():
        raise ParseError("Empty justification")
    return justification_parser.parse(text)
