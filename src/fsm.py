from typing import List, Tuple, Dict, Callable, Any, NamedTuple
from random import choice
from dataclasses import dataclass, asdict

State = Dict  # dataclass variable: value
StatePredicate = Callable[[State], bool]
StateObjFunction = Callable
Check = Tuple[StatePredicate, Callable]
CheckObj = Tuple[StateObjFunction, Callable]
Path = List[Tuple[Callable, Any, List[Check]]]
# For separated model:
Behavior = object
GetStateValue = Callable[[Behavior], Any]


class Event(NamedTuple):
    procedure: Callable
    inputs: List
    before_checks: List


# TODO declare
WalkResult = Any


class FSM(object):
    def __init__(self):
        self.events: List[Event] = []

    def event(self, inputs: List = None, before_checks: List[Check] = None):
        def inner_event(func):
            self.events.append(Event(func, inputs, before_checks))
            return func

        return inner_event

    def get_random_path(self, length) -> Path:
        result = []  # TODO do as generator
        for i in range(length):
            # event_proc, inputs, before_checks = choice(self.events)
            event = choice(self.events)
            if event.inputs:
                input = choice(event.inputs)
            else:
                input = []
            result.append((event.procedure, input, event.before_checks))
        return result

    def walk(self, obj: dataclass, path: Path) -> WalkResult:
        unique_states: List[State] = []
        transitions: List[Tuple[int, int, Callable, Any, List[str]]] = []
        state0 = self.get_state(obj)
        unique_states.append(state0)
        for proc, input, before_checks in path:
            old_state = self.get_state(obj)
            old_state_num = unique_states.index(old_state)
            print(f"Executing {proc}/{input}")
            checks_before_to_scheme = []
            if before_checks:
                for check_state, check_body in before_checks:
                    if check_state(obj):
                        checks_before_to_scheme.append(check_body.__name__)
                        # noinspection PyArgumentList
                        check_body(obj)
            proc(obj, *input)
            new_state = self.get_state(obj)
            print(f"Got state: {new_state}")
            try:
                new_state_num = unique_states.index(new_state)
                print("The state already in")
            except ValueError:
                unique_states.append(new_state)
                new_state_num = len(unique_states) - 1
            transition = (old_state_num, new_state_num, proc, input, checks_before_to_scheme)
            if transition not in transitions:
                transitions.append(transition)

        return unique_states, transitions

    def get_state(self, obj: dataclass):
        result = asdict(obj)
        return result

    def get_plantuml(self, walk_result: WalkResult):
        yield '@startuml'
        yield '[*] --> State_0'
        # TODO dump initial state to the black circle
        for state_num, state in enumerate(walk_result[0]):
            for state_var, state_value in state.items():
                yield f'State_{state_num} : {state_var}={state_value}'
        for transition in walk_result[1]:
            in_vertex, out_vertex, proc, input, checks_before = transition
            yield f'State_{in_vertex} --> State_{out_vertex} : {proc.__name__} {input if input else ""}'
            if checks_before:
                yield 'note on link'
                for check_description in checks_before:
                    yield f"Check before: {check_description}"
                yield 'end note'
        yield '@enduml'


class FsmMarkup(FSM):
    """To subclass for each model. Interface as dataclass.
    """

    def __init__(self):
        self.model = None
        self.state_values: Dict[str, GetStateValue] = {}
        super().__init__()  # <- self.events here
        # Fill self.events here in ancestors.
        # Fill self.state_values here

    def asdict(self, obj) -> Dict:
        result = {field: get_state_value(obj) for field, get_state_value in self.state_values.items()}
        return result

    def add_event(self, class_method, inputs: List = None, checks_before: List[CheckObj] = None):
        # TODO checks before
        self.events.append(Event(class_method, inputs, checks_before))

    def get_state(self, obj):
        result = self.asdict(obj)
        return result

