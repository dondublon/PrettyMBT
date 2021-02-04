class Comparator(object):
    def __init__(self, get_state_value):
        self.get_state_value = get_state_value

    def compare(self, obj, compare_to):
        raise NotImplementedError("Must inherit")


class Equal(Comparator):
    def compare(self, obj, compare_to):
        return self.get_state_value(obj) == compare_to


class ConditionalRunner:
    def __init__(self, obj, conditions_list, additional_func, working_method):
        self.obj = obj
        self.conditions_list = conditions_list
        self.additional_func = additional_func
        self.working_method = working_method

    def __call__(self, *args, **kwargs):
        for get_state_value, compare_to in self.conditions_list:
            comparator = get_state_value()
            if not comparator.compare(self.obj, compare_to):
                break
        else:
            self.additional_func(self.obj)
        return self.working_method(self.obj, *args, **kwargs)


class ConditionalRunWrapper:
    def __init__(self, conditions_list, additional_func):
        self.conditions_list = conditions_list
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
        return ConditionalRunner(self.obj, self.conditions_list, self.additional_func, working_method)


class StateValueInternal(object):
    def __init__(self, name, get_state_value):
        self.name = name
        self.get_state_value = get_state_value

    def equal(self):
        return Equal(self.get_state_value)

class StateValueWrapper(object):
    def __init__(self, name):
        self.name = name

    def __call__(self, get_state_value):
        return StateValueInternal(self.name, get_state_value)


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
    def conditional_run(comparison_list, additional_func):
        """:param comparison_list: [(get_state_value, compare_to), ...]
        """
        return ConditionalRunWrapper(comparison_list, additional_func)

    @staticmethod
    def state_value(name):
        return StateValueWrapper(name)

@ModelDecorator
class WorkingClass(object):
    @ModelDecorator.state_value("My state value")
    def my_state_value(self):
        return 16

    def additional_func(self):
        print("I'm additional")

    @ModelDecorator.conditional_run([(my_state_value.equal, 16), (my_state_value.equal, 16)], additional_func)
    def working_method(self, msg):
        print(f"I'm working with {msg}! ")
        return f"I worked {msg}"


my_obj = WorkingClass()
print("invoking my_obj.my_state_value")
print(my_obj.working_method("^)"))