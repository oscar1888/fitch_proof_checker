from lark import Transformer
from fitch_proof_checker.model.formula.const import Const
from fitch_proof_checker.model.formula.func import Func
from fitch_proof_checker.model.formula.predicate import Predicate
from fitch_proof_checker.model.formula.prop_var import PropVar
from fitch_proof_checker.model.formula.var import Var


class FormulaTransformer(Transformer):
    def __init__(self, symbol_map):
        super().__init__()
        self.symbol_map = symbol_map

    def bin_op(self, args):
        op_sym = str(args[1])
        return self.symbol_map[op_sym](args[0], args[2])

    def un_op(self, args):
        op_sym = str(args[0])
        return self.symbol_map[op_sym](args[1])

    def nary_op(self, args):
        op_sym = str(args[0])
        formulas = args[1:]
        return self.symbol_map[op_sym](*formulas)

    def nullary_op(self, args):
        op_sym = str(args[0])
        return self.symbol_map[op_sym]()

    def quantified(self, args):
        quant_sym = str(args[0])
        quant_obj = self.symbol_map[quant_sym]
        var_node = Var(str(args[1]))
        return quant_obj(var_node, args[2])

    def pred(self, args):
        pred_name = str(args[0])
        terms = args[1:]
        return Predicate(pred_name, *terms)

    def eq(self, args):
        return Predicate("=", *args)

    def prop_var(self, args):
        return PropVar(str(args[0]))

    def var(self, args):
        return Var(str(args[0]))

    def const(self, args):
        return Const(str(args[0]))

    def func(self, args):
        func_name = str(args[0])
        terms = args[1:]
        return Func(func_name, *terms)
