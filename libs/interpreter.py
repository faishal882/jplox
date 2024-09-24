import sys, time
from .tokenizer import TokenType
from .parser import Expr, Stmt
from .enviornment import Environment
from .fun_impl.jplox_callable import LoxCallable
from .fun_impl.jplox_function import LoxFunction, NativeFunction
from .fun_impl.fun_return import Return

def castBooleanToString(value):
    if value == True:
        return "true"
    elif value == False:
        return "false"
    else:
        return value

def castStringToBoolean(value):
    if value == "true":
        return True
    elif value == "false":
        return False
    elif value == "nil":
        return False
    else:
        return value

class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class Interpreter(Expr.Visitor, Stmt.Visitor):
    # environment = Environment()
    globals = Environment()
    environment = globals

    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals

        # Define a native "clock" function, other native functions can be defined this way
        self.globals.define("clock", NativeFunction(
            arity_func=lambda: 0,
            call_func=lambda interpreter, arguments: time.time(),
            to_string_func=lambda: "<native fn>"
        ))

    def visit_literal_expr(self, expr):
        result = expr.value
        return result
    
    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(castStringToBoolean(left)):
                return left
        else:
            if not self.is_truthy(castStringToBoolean(left)):
                return left

        return self.evaluate(expr.right)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.BANG:
            # result = self.bangTruth(right)
            result = self.is_truthy(right)
        elif expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            result = -float(right)
        else:
            result = None

        return result
    
    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")

        function = callee 

        if len(arguments) != function.arity(): #arity: number of expected arguments
            raise RuntimeError(expr.paren, f"Expected {function.arity()} arguments but got {len(arguments)}.")

        return function.call(self, arguments)

    def visit_grouping_expr(self, expr):
        result = self.evaluate(expr.expression)
        return result

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            result = castBooleanToString(float(left) > float(right))
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            result = castBooleanToString(float(left) >= float(right))
        elif expr.operator.type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            result = castBooleanToString(float(left) < float(right))
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            result = castBooleanToString(float(left) <= float(right))
        elif expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            result = float(left) - float(right)
        elif expr.operator.type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                result = float(left) + float(right)
            elif isinstance(castStringToBoolean(left), str) and isinstance(castStringToBoolean(right), str):
                result = str(left) + str(right)
            else:
                raise RuntimeError(expr.operator, "Operands must be two numbers or two strings.")
        elif expr.operator.type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            result = float(left) / float(right)
        elif expr.operator.type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            result = float(left) * float(right)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            result = castBooleanToString(not self.isEqual(left, right))
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            result = castBooleanToString(self.isEqual(left, right))
        else:
            result = None
        
        return result
   
    def visit_expression_stmt(self, stmt):
        self.run(stmt.expression)
        return None
    
    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
        return None 
    
    def visit_if_stmt(self, stmt):
        #cast_to_boolean, python boolean True or False in lox true or false
        if self.is_truthy(castStringToBoolean(self.evaluate(stmt.condition))): 
            return self.run(stmt.then_branch)
        elif stmt.else_branch is not None:
            return self.run(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt):
        value = self.run(stmt.expression)
        return value
    
    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value) 
        
        # print("return", value)
        raise Return(value)

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.run(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)
        return None
    
    def visit_while_stmt(self, stmt):
        result = []
        while self.is_truthy(castStringToBoolean(self.evaluate(stmt.condition))):
            result.append(self.run(stmt.body))
        return result

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value


    def visit_variable_expr(self, expr):
        if self.environment.get(expr.name) is None:
            return "nil"
        return self.environment.get(expr.name)

    def run(self, stmt):
        return stmt.accept(self)
        
    def evaluate(self, expr):
        return expr.accept(self)
    
    def execute_block(self, statements, environment):
        previous = self.environment
        # result = []
        try:
            self.environment = environment

            for statement in statements:
                _result = self.run(statement)
                if _result is not None:
                    print(_result)
                    # result.append(_result)
        finally:
            self.environment = previous
        return None 

    def visit_block_stmt(self, stmt):
        return self.execute_block(stmt.declarations, Environment(self.environment))
        
    def isEqual(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b
    
    def is_truthy(self, obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return bool(obj)
        return True
    
    #Made this function to pass test for codecrafters challenge
    # def bangTruth(self, obj):
    #     if obj == "false":
    #         return "true"
    #     elif obj == "true":
    #         return "false"
    #     elif obj == "nil":
    #         return "true"
    #     else:
    #         return "false"
    
    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

