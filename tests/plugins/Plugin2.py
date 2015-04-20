from excalibur.plugin import Plugin


class Plugin2(Plugin):

    def actions_action1(self, parameters, arguments):
        return "p2ok1"

    def actions_action2(self, parameters, arguments):
        raise Exception("error plugin 2 action 2 !")
