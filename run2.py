from typing import Type
from pprint import pprint
from examples.helloworld import HelloWorld2
from src.fsm import FsmMarkup


class HelloworldFsmMarkup(FsmMarkup):
    def __init__(self):
        super().__init__()
        self.model = HelloWorld2
        self.add_event(self.model.turn_switch, None, None)
        self.add_event(self.model.increase_value, [(1,), (2,), (3,)])
        self.state_values['Switch'] = lambda model_obj: model_obj.switch
        self.state_values['Value'] = lambda model_obj: model_obj.value


fsm = HelloworldFsmMarkup()
print("Random path:")
path = fsm.get_random_path(16)
pprint(path)
obj = HelloWorld2()
walk_result = fsm.walk(obj, path)
uml_text = fsm.dump_plantuml(walk_result)
with open("result.uml", 'w') as uml_file:
    uml_file.writelines(uml_text)

