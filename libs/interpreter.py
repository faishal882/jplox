from .tokenizer import TokenType

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
    else:
        return value

class RuntimeError(Exception):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class Interpreter:
    def visit_literal_expr(self, expr):
        result = expr.value
        return result

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == TokenType.BANG:
            result = self.bangTruth(right)
        elif expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            result = -float(right)
        else:
            result = None

        return result

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
    
    def evaluate(self, expr):
        return expr.accept(self)

    def isEqual(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b

    def bangTruth(self, obj):
        if obj == "false":
            return "true"
        elif obj == "true":
            return "false"
        elif obj == "nil":
            return "true"
        else:
            return "false"
    
    def check_number_operand(self, operator, operand):
        if isinstance(operand, float):
            return
        raise RuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

