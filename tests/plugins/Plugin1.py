from excalibur.core import Plugin

class Plugin1(Plugin):

    def actions_action1(self, parameters, arguments):
        return "p1ok1"

    def actions_action2(self, parameters, arguments):
        raise Exception("error plugin 1 action 2 !")
