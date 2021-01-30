from pprint import pprint
from examples.helloworld import helloworld_fsm, HelloWorld

print(helloworld_fsm)
print(helloworld_fsm.events)
print("Random path:")
path = helloworld_fsm.get_random_path(16)
pprint(path)
obj = HelloWorld(False, 0)
walk_result = helloworld_fsm.walk(obj, path)
uml_text = helloworld_fsm.dump_plantuml(walk_result)
with open("result.uml", 'w') as uml_file:
    uml_file.writelines(uml_text)

