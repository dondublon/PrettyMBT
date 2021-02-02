from typing import Type
from pprint import pprint
from examples.helloworld import HelloWorld2
from src.fsm import FsmMarkup


class HelloworldFsmMarkup(FsmMarkup):
    def __init__(self, model: Type[HelloWorld2]):
        super().__init__(model)
        self.add_event(model.turn_switch, None, None)
        self.add_event(model.increase_value, [1, 2, 3])
        self.state_values['Switch'] = lambda model_: model_.switch
        self.state_values['Value'] = lambda model_: model_.value


fsm = HelloworldFsmMarkup(HelloWorld2)
print("Random path:")
path = fsm.get_random_path(16)
pprint(path)
obj = HelloWorld2()
walk_result = fsm.walk(obj, path)
uml_text = fsm.dump_plantuml(walk_result)
with open("result.uml", 'w') as uml_file:
    uml_file.writelines(uml_text)

