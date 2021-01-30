from pprint import pprint
from examples.helloworld import helloworld_fsm, HelloWorld

print(helloworld_fsm)
print(helloworld_fsm.events)
print("Random path:")
path = helloworld_fsm.get_random_path(6)
pprint(path)
obj = HelloWorld(False, 0)
helloworld_fsm.walk(obj, path)
