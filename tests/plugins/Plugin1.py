class Plugin1(object):

    def actions_action1(self, parameters, arguments):
        return "p1ok1"

    def actions_action2(self, parameters, arguments):
        raise Exception("error plugin 1 action 2 !")
