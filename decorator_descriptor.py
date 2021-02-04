from src.fsm_markup import *

@ModelDecorator
class WorkingClass(object):
    @ModelDecorator.state_value("My state value")
    def my_state_value(self):
        return 18

    def additional_func(self):
        print("I'm additional")

    @ModelDecorator.conditional_run([my_state_value.between(16, 17), my_state_value.bool()], additional_func, "or")
    def working_method(self, msg):
        print(f"I'm working with {msg}! ")
        return f"I worked {msg}"


my_obj = WorkingClass()
print("invoking my_obj.my_state_value")
print(my_obj.working_method("^)"))