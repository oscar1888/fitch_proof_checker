from fitch_proof_checker.model.logic.logic_manager import LogicManager
from fitch_proof_checker.model.rule import AndElim, AndIntro, CoImpliesElim, CoImpliesIntro, EqualsElim, EqualsIntro, \
    ExistsElim, ExistsIntro, FalsumElim, FalsumIntro, ForAllElim, ForAllIntro, ImpliesElim, ImpliesIntro, NotElim, \
    NotIntro, OrElim, OrIntro, Reit


class LogicFactory:

    @staticmethod
    def create_propositional_logic() -> LogicManager:
        rules = [
            AndIntro,
            AndElim,
            OrIntro,
            OrElim,
            NotIntro,
            NotElim,
            FalsumIntro,
            FalsumElim,
            ImpliesIntro,
            ImpliesElim,
            CoImpliesIntro,
            CoImpliesElim,
            Reit
        ]

        return LogicManager(rules)

    @staticmethod
    def create_first_order_logic() -> LogicManager:
        pl = LogicFactory.create_propositional_logic()

        fol_rules = [
            EqualsIntro,
            EqualsElim,
            ForAllIntro,
            ForAllElim,
            ExistsIntro,
            ExistsElim
        ]

        pl.rules.extend(fol_rules)

        return pl
