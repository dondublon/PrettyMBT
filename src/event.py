from typing import List, Tuple, Dict
from random import choice
from dataclasses import dataclass

Path = List[Tuple]
State = Dict  # dataclass variable: value

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

    def walk(self, obj: object, path: Path):
        self.states = []
        for proc, input in path:
            print(f"Executing {proc}/{input}")
            proc(obj, input)
            # noinspection PyTypeChecker
            state = self.get_state(obj)
            print(f"Got state: {state}")

    def get_state(self, obj):
        result = {}
        for field in obj.__dataclass_fields__:
            result[field] = getattr(obj, field)
        return result