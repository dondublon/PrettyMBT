from typing import List, Tuple, Dict, Callable, Any
from random import choice
from dataclasses import dataclass

Path = List[Tuple]
State = Dict  # dataclass variable: value
WalkResult = Any

class FSM(object):
    def __init__(self):
        self.events = []

    def event(self, inputs: List = None):
        def inner_event(func):
            self.events.append((func, inputs))
            return func

        return inner_event

    def get_random_path(self, length) -> Path:
        result = []  # TODO do as generator
        for i in range(length):
            event_proc, inputs = choice(self.events)
            if inputs:
                input = choice(inputs)
            else:
                input = None
            result.append((event_proc, input))
        return result

    def walk(self, obj: dataclass, path: Path) -> WalkResult:
        unique_states: List[State] = []
        transitions: List[Tuple[int, int, Callable, Any]] = []
        state0 = self.get_state(obj)
        unique_states.append(state0)
        for proc, input in path:
            old_state = self.get_state(obj)
            old_state_num = unique_states.index(old_state)
            assert old_state_num >= 0
            print(f"Executing {proc}/{input}")
            proc(obj, input)
            new_state = self.get_state(obj)
            print(f"Got state: {new_state}")
            try:
                new_state_num = unique_states.index(new_state)
                print("The state already in")
            except ValueError:
                unique_states.append(new_state)
                new_state_num = len(unique_states) - 1
            transition = (old_state_num, new_state_num, proc, input)
            if transition not in transitions:
                transitions.append(transition)

        return unique_states, transitions

    def get_state(self, obj: dataclass):
        result = {}
        for field in obj.__dataclass_fields__:
            result[field] = getattr(obj, field)
        return result

    def dump_plantuml(self, walk_result: WalkResult):
        text = ['@startuml']
        text.append('[*] --> State_0')
        # TODO dump initial state to the black circle
        for state_num, state in enumerate(walk_result[0]):
            for state_var, state_value in state.items():
                text.append(f'State_{state_num} : {state_var}={state_value}')
        for transition in walk_result[1]:
            in_vertex, out_vertex, proc, input = transition
            text.append(f'State_{in_vertex} --> State_{out_vertex} : {proc.__name__} {input}')
        text.append('@enduml')
        return '\n'.join(text)