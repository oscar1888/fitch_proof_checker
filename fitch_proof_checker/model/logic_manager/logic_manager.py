class Rule:
    def __init__(self, name):
        self.name = name


class Logic:
    def __init__(self):
        self.rules = []


class LogicManager:
    def __init__(self):
        # TODO: implement this
        self.active_logic = Logic()
        pass
