from typing import List, Tuple, Dict, Callable, Any, NamedTuple
from random import choice
from dataclasses import dataclass, asdict
from .fsm_markup import ConditionalRunner, Model

State = Dict  # dataclass variable: value
StatePredicate = Callable[[State], bool]
StateObjFunction = Callable
SDA = Tuple[StatePredicate, Callable]  # State-Dependent Action
CheckObj = Tuple[StateObjFunction, Callable]
# Path = List[Tuple[Callable, Any, List[Check]]]

# For separated model:
Behavior = object
GetStateValue = Callable[[Behavior], Any]


class PathItem(NamedTuple):
    method: Callable  # method of class.
    input: Tuple  # input for one method invocation

Path = List[PathItem]  #

# (old_state_num, new_state_num, proc, input, checks_before_to_scheme)
class Transition(NamedTuple):
    old_state_num: int
    new_state_num: int
    proc: Callable
    input: Tuple
    sda_before_str: List[str]

class Event(NamedTuple):
    procedure: Callable
    inputs: List[State]
    sda_before: List[SDA]  # "sda" means state-dependent actions.


# TODO declare
class WalkResult(NamedTuple):
    states: List
    transitions: List[Transition]


class FSM(object):
    def __init__(self):
        self.events: List[Event] = []

    def event(self, inputs: List = None, sda_before: List[SDA] = None):
        def inner_event(func):
            self.events.append(Event(func, inputs, sda_before))
            return func

        return inner_event

    def get_random_path(self, length) -> Path:
        result = []  # TODO do as generator
        for i in range(length):
            # event_proc, inputs, before_checks = choice(self.events)
            event:Event = choice(self.events)
            if event.inputs:
                input = choice(event.inputs)
            else:
                input = []
            result.append(PathItem(event.procedure, input))
        return result

    def walk(self, obj: dataclass, path: Path) -> WalkResult:
        unique_states: List[State] = []
        transitions: List[Transition] = []
        state0 = self.get_state(obj)
        unique_states.append(state0)
        for proc, input in path:
            old_state = self.get_state(obj)
            old_state_num = unique_states.index(old_state)
            print(f"Executing {proc}/{input}")
            checks_before_to_scheme = []
            if isinstance(proc, ConditionalRunner):
                assert proc.obj == obj
                # we won't execute working method, just collect the conditions for scheme
                if proc.check(obj):
                    checks_before_to_scheme.append(proc.action_as_str())
                proc.working_method(obj, *input)
            else:
                proc(obj, *input)
            new_state = self.get_state(obj)
            print(f"Got state: {new_state}")
            try:
                new_state_num = unique_states.index(new_state)
                print("The state already in")
            except ValueError:
                unique_states.append(new_state)
                new_state_num = len(unique_states) - 1
            transition = Transition(old_state_num, new_state_num, proc, input, checks_before_to_scheme)
            if transition not in transitions:
                transitions.append(transition)

        return WalkResult(unique_states, transitions)

    def get_state(self, obj: dataclass):
        result = asdict(obj)
        return result


class Dumper(object):
    def get_plantuml(self, walk_result: WalkResult):
        yield '@startuml'
        yield '[*] --> State_0'
        # TODO dump initial state to the black circle
        for state_num, state in enumerate(walk_result.states):
            for state_var, state_value in state.items():
                yield f'State_{state_num} : {state_var}={state_value}'
        for transition in walk_result.transitions:
            in_vertex, out_vertex, proc, input, sdas_before = transition
            yield f'State_{in_vertex} --> State_{out_vertex} : {proc.__name__} {input if input else ""}'
            if sdas_before:
                yield 'note on link'
                for check_description in sdas_before:
                    yield f"Action before: {check_description}"
                yield 'end note'
        yield '@enduml'


class FsmMarkup(FSM):
    """To subclass for each model. Interface as dataclass.
    """
    model: Model = None

    def __init__(self):
        super().__init__()  # <- self.events here
        # Fill self.events here in ancestors.
        # TODO universal, move to the parent:
        attrs = list(self.model.enumerate_state_values())
        self.state_values = {svi.name: svi.get_state_value for svi in attrs}

    def asdict(self, obj) -> Dict:
        result = {field: get_state_value(obj) for field, get_state_value in self.state_values.items()}
        return result

    def add_event(self, class_method, inputs: List = None, sda_before: List[CheckObj] = None):
        """:param sda_before : "sda" meand state-dependent actions."""
        self.events.append(Event(class_method, inputs, sda_before))

    def get_state(self, obj):
        result = self.asdict(obj)
        return result

    @property
    def model_class(self):
        return self.model.class_
