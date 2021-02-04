class Comparator(object):
    def __init__(self, get_state_value, *args, **kwargs):
        self.get_state_value = get_state_value

    def compare(self, obj):
        raise NotImplementedError("Must inherit")


class Equal(Comparator):
    def __init__(self, get_state_value, equal_to):
        super().__init__(get_state_value, equal_to)
        self.equal_to = equal_to

    def compare(self, obj):
        return self.get_state_value(obj) == self.equal_to


class Between(Comparator):
    def __init__(self, get_state_value, value1, value2):
        super().__init__(get_state_value, value1, value2)
        self.value1 = value1
        self.value2 = value2

    def compare(self, obj):
        return self.value1 <= self.get_state_value(obj) <= self.value2


class Less(Comparator):
    def __init__(self, get_state_value, compare_to):
        super().__init__(get_state_value, compare_to)
        self.compare_to = compare_to

    def compare(self, obj):
        return self.get_state_value(obj) < self.compare_to


class Greater(Comparator):
    def __init__(self, get_state_value, compare_to):
        super().__init__(get_state_value, compare_to)
        self.compare_to = compare_to

    def compare(self, obj):
        return self.get_state_value(obj) > self.compare_to


class Bool(Comparator):
    def compare(self, obj):
        return bool(self.get_state_value(obj))


class ConditionalRunner:
    def __init__(self, logic_mode, obj, conditions_list, additional_func, working_method):
        self.logic_mode = logic_mode
        self.obj = obj
        self.conditions_list = conditions_list
        self.additional_func = additional_func
        self.working_method = working_method

    def __call__(self, *args, **kwargs):
        if self.logic_mode == "and":
            for comparator in self.conditions_list:
                if not comparator.compare(self.obj):
                    break
            else:
                self.additional_func(self.obj)
        elif self.logic_mode == "or":
            for comparator in self.conditions_list:
                if comparator.compare(self.obj):
                    self.additional_func(self.obj)
                    break
        return self.working_method(self.obj, *args, **kwargs)


class ConditionalRunWrapper:
    def __init__(self, conditions_list, additional_func, logic_mode):
        self.logic_mode = logic_mode
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
        return ConditionalRunner(self.logic_mode, self.obj, self.conditions_list, self.additional_func, working_method)


class StateValueInternal(object):
    def __init__(self, name, get_state_value):
        self.name = name
        self.get_state_value = get_state_value

    def equal(self, compare_to):
        return Equal(self.get_state_value, compare_to)

    def between(self, value1, value2):
        return Between(self.get_state_value, value1, value2)

    def less(self, compare_to):
        return Less(self.get_state_value, compare_to)

    def greater(self, compare_to):
        return Greater(self.get_state_value, compare_to)

    def bool(self):
        return Bool(self.get_state_value)

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
    def conditional_run(comparison_list, additional_func, logic_mode='and'):
        """
        :param logic_mode: "and" or "or", how to compare comparison_list.
        :param comparison_list: [(get_state_value, compare_to), ...]
        """
        return ConditionalRunWrapper(comparison_list, additional_func, logic_mode)

    @staticmethod
    def state_value(name):
        return StateValueWrapper(name)
