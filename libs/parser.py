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

        def visit_variable_expr(self, expr):
            pass

        def visit_assign_expr(self, expr):
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

    class Variable:
        def __init__(self, name):
            self.name = name

        def accept(self, visitor):
            return visitor.visit_variable_expr(self)

    class Assign:
        def __init__(self, name, value):
            self.name = name  
            self.value = value  

        def accept(self, visitor):
            return visitor.visit_assign_expr(self)


class Stmt:
    class Visitor:
        def visit_expression_stmt(self, stmt):
            pass

        def visit_print_stmt(self, stmt):
            pass

        def visit_var_stmt(self, stmt):
            pass

        def visit_block_stmt(self, stmt):
            pass

    class Expression:
        def __init__(self, expression):
            self.expression = expression

        def accept(self, visitor):
            return visitor.visit_expression_stmt(self)

    class Print:
        def __init__(self, expression):
            self.expression = expression

        def accept(self, visitor):
            return visitor.visit_print_stmt(self)

    class Var:
        def __init__(self, name, initializer):
            self.name = name
            self.initializer = initializer

        def accept(self, visitor):
            return visitor.visit_var_stmt(self)
    
    class Block:
        def __init__(self, declarations):
            self.declarations = declarations 

        def accept(self, visitor):
            return visitor.visit_block_stmt(self)

class Lox:
    @staticmethod
    def error(token, message):
        if token.type == TokenType.EOF:
            print(f"[Line {token.line}] Error at end: {message}")
        else:
            print(f"[Line {token.line}] Error at '{token.lexeme}': {message}")

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.has_errors = False 
   
    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements


    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)

            raise self.error(equals, "Invalid assignment target.")

        return expr

    
    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.has_errors = True
            self.synchronize()
            return None 

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Stmt.Block(self.block())
        return self.expression_statement()

    def print_statement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Stmt.Print(value)
    
    def var_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Stmt.Var(name, initializer)

    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Stmt.Expression(expr)
    
    def block(self):
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

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
            return Expr.Variable(self.previous())

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
            raise self.error(self.peek(), message)
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
class AstPrinter(Expr.Visitor, Stmt.Visitor):
    def print(self, expr: Expr) -> str:
        if expr is not None:
             return expr.accept(self)

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
    
    def visit_variable_expr(self, expr: Expr.Variable):
        return self.parenthesize(expr.name)
    
    def visit_assign_expr(self, expr: Expr.Assign):
        return self.parenthesize(expr.name.lexeme, expr.value)

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        return self.print(stmt.expression)
    
    def visit_print_stmt(self, stmt: Stmt.Print):
        return self.parenthesize("print", stmt.expression)

    def visit_var_stmt(self, stmt: Stmt.Var):
        return self.parenthesize(stmt.name, stmt.initializer)

    def visit_block_stmt(self, stmt: Stmt.Block):
        return self.parenthesize("block", *stmt.declarations)    

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        builder = []

        builder.append(f"({name}")
        for expr in exprs:
            builder.append(" ")
            builder.append(expr.accept(self))
        builder.append(")")

        return "".join(builder)
