from typing import List, Any, Union
from .tokenizer import Token, TokenType

class Expr:
    class Visitor:
        def visit_binary_expr(self, expr):
            pass

        def visit_grouping_expr(self, expr):
            pass

        def visit_literal_expr(self, expr):
            pass

        def visit_unary_expr(self, expr):
            pass

    class Binary:
        def __init__(self, left, operator, right):
            self.left = left
            self.operator = operator
            self.right = right

        def accept(self, visitor):
            return visitor.visit_binary_expr(self)

    class Grouping:
        def __init__(self, expression):
            self.expression = expression

        def accept(self, visitor):
            return visitor.visit_grouping_expr(self)

    class Literal:
        def __init__(self, value):
            self.value = value

        def accept(self, visitor):
            return visitor.visit_literal_expr(self)

    class Unary:
        def __init__(self, operator, right):
            self.operator = operator
            self.right = right

        def accept(self, visitor):
            return visitor.visit_unary_expr(self)

class Lox:
    @staticmethod
    def error(token, message):
        if token.type == TokenType.EOF:
            print("")
        else:
            print(f"[Line {token.line}] Error at '{token.lexeme}': {message}")

class ParseError(Exception):
    pass

def error(token, message):
    if token.type == TokenType.EOF:
        Lox.error(token, message)
    else:
        Lox.error(token, message)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self):
        try:
            return self.expression()
        except ParseError:
            self.synchronize()
            return None

    def expression(self):
        return self.equality()

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Expr.Binary(expr, operator, right)
        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Expr.Unary(operator, right)
        return self.primary()

    def primary(self):
        if self.match(TokenType.FALSE):
            return Expr.Literal("false")
        if self.match(TokenType.TRUE):
            return Expr.Literal("true")
        if self.match(TokenType.NIL):
            return Expr.Literal("nil")
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Expr.Literal(self.previous().literal)
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect expression")
            return Expr.Grouping(expr)
        if self.match(TokenType.IDENTIFIER):
            return Expr.Literal(self.previous().literal)

        raise self.error(self.peek(), "I AM FUCKED.")

    def match(self, *types: TokenType):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False

    def consume(self, type: TokenType, message):
        if self.check(type):
            return self.advance()
        if self.is_at_end():
            raise self.error(self.peek(), "")
        raise self.error(self.peek(), message)

    def check(self, type: TokenType):
        if self.is_at_end():
            return False
        return self.peek().type == type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]
    
    def error(self, token: Token, message):
        Lox.error(token, message)
        return ParseError()

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.peek().type in [
                TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR,
                TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN
            ]:
                return

            self.advance()

    
#A Vistor class (Visitor Pattern)
class AstPrinter(Expr.Visitor):
    def print(self, expr: Expr) -> str:
        if expr is not None:
             return expr.accept(self)
        # else: 
            # return ""

    def visit_binary_expr(self, expr: Expr.Binary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Expr.Grouping) -> str:
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr: Expr.Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        builder = []

        builder.append(f"({name}")
        for expr in exprs:
            builder.append(" ")
            builder.append(expr.accept(self))
        builder.append(")")

        return "".join(builder)
