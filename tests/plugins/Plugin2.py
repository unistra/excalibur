class Plugin2(object):

    def actions_action1(self, parameters, arguments):
        return "p2ok1"

    def actions_action2(self, parameters, arguments):
        raise Exception("error plugin 2 action 2 !")
