from .jplox_callable import LoxCallable
from .fun_return import Return
from libs.enviornment import Environment

class LoxFunction(LoxCallable):
    def __init__(self, declaration):
        self.declaration = declaration

    def arity(self):
        arity = len(self.declaration.params)
        return int(arity) 

    def call(self, interpreter, arguments):
        environment = Environment(interpreter.globals)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value
        return None
    
    def to_string(self):
        return f"<fn {self.declaration.name.lexeme}>"

class NativeFunction(LoxCallable):
    def __init__(self, arity_func, call_func, to_string_func):
        self.arity_func = arity_func
        self.call_func = call_func
        self.to_string_func = to_string_func

    def arity(self):
        return self.arity_func()

    def call(self, interpreter, arguments):
        return self.call_func(interpreter, arguments)

    def to_string(self):
        return self.to_string_func()

