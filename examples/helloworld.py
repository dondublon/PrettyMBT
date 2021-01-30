from dataclasses import dataclass
from src.event import FSM

helloworld_fsm = FSM()

@dataclass
class HelloWorld(object):
    switch: bool
    value: int  # from 0 to 2

    def initial_state(self):
        # TODO seems no need, values are reauired in constructor.
        self.switch = False
        self.value = 0

    @helloworld_fsm.event([])
    def turn_switch(self, input):
        self.switch = not self.switch

    @helloworld_fsm.event([1, 2, 3])
    def increase_value(self, input):
        self.value = (self.value + input) % 3
