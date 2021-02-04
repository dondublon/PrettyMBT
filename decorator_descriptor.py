class ConditionalRunner:
    def __init__(self, obj, get_state_value, compare_to, additional_func, working_method):
        self.obj = obj
        self.get_state_value = get_state_value
        self.compare_to = compare_to
        self.additional_func = additional_func
        self.working_method = working_method

    def __call__(self, *args, **kwargs):
        if self.get_state_value(self.obj) == self.compare_to:
            self.additional_func(self.obj)
        return self.working_method(self.obj, *args, **kwargs)

class ConditionalRunWrapper:
    def __init__(self, state_value, compare_to, additional_func):
        self.state_value = state_value
        self.compare_to = compare_to
        self.additional_func = additional_func
        self._obj = None

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, value):
        assert self._obj is None
        self._obj = value

    def __call__(self, working_method):
        return ConditionalRunner(self.obj, self.state_value, self.compare_to, self.additional_func, working_method)


class StateValueWrapper(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        pass


class ModelDecorator(object):
    def __init__(self, class_):
        self.class_ = class_

    def __call__(self, *args, **kwargs):
        obj = self.class_(*args, **kwargs)
        for attr_name in dir(obj):
            attr = getattr(obj, attr_name)
            if isinstance(attr, ConditionalRunWrapper):
                attr.obj = obj
        return obj

    @staticmethod
    def conditional_run(state_value, compare_to, additional_func):
        return ConditionalRunWrapper(state_value, compare_to, additional_func)

    @staticmethod
    def state_value(name):
        return StateValueWrapper(name)

@ModelDecorator
class WorkingClass(object):
    def my_state_value(self):
        return 16


    def additional_func(self):
        print("I'm additional")

    # @my_state_value.equal(17).run(additional_func)
    # @TextContract("my_state_value == 16", additional_func)
    # @class_decorator
    @ModelDecorator.conditional_run(my_state_value, 16, additional_func)
    def working_method(self, msg):
        print(f"I'm working with {msg}! ")
        return f"I worked {msg}"


my_obj = WorkingClass()
print("invoking my_obj.my_state_value")
print(my_obj.working_method("^)"))