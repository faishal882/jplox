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
        def visit_logical_expr(self, expr):
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

    class Logical:
        def __init__(self, left, operator, right):
            self.left = left         
            self.operator = operator  
            self.right = right       

        def accept(self, visitor):
            return visitor.visit_logical_expr(self)


class Stmt:
    class Visitor:
        def visit_expression_stmt(self, stmt):
            pass

        def visit_print_stmt(self, stmt):
            pass

        def visit_var_stmt(self, stmt):
            pass

        def visit_if_stmt(self, stmt):
            pass

        def visit_block_stmt(self, stmt):
            pass

        def visit_while_stmt(self, stmt):
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
    
    class If:
        def __init__(self, condition, then_branch, else_branch=None):
            self.condition = condition 
            self.then_branch = then_branch  
            self.else_branch = else_branch 

        def accept(self, visitor):
            return visitor.visit_if_stmt(self)
    
    class While:
        def __init__(self, condition, body):
            self.condition = condition 
            self.body = body 

        def accept(self, visitor):
            return visitor.visit_while_stmt(self)

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
        expr = self.or_expr()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(expr, Expr.Variable):
                name = expr.name
                return Expr.Assign(name, value)

            raise self.error(equals, "Invalid assignment target.")

        return expr

    def or_expr(self):
        expr = self.and_expr()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expr()
            expr = Expr.Logical(expr, operator, right)

        return expr
    
    def and_expr(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Expr.Logical(expr, operator, right)

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
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement() 
        return self.expression_statement()
    
    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()

        return Stmt.If(condition, then_branch, else_branch)

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
    
    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return Stmt.While(condition, body)
    
    def for_statement(self):
        #syntactic sugar
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        # Add increment to the end of the body
        if increment is not None:
            body = Stmt.Block([body, Stmt.Expression(increment)])

        # Use 'true' as the default condition if none is provided
        if condition is None:
            condition = Expr.Literal(True)

        body = Stmt.While(condition, body)

        # If there's an initializer, wrap it with the loop in a block
        if initializer is not None:
            body = Stmt.Block([initializer, body])

        return body

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
    
    def visit_logical_expr(self, expr: Expr.Logical):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_expression_stmt(self, stmt: Stmt.Expression):
        return self.print(stmt.expression)
    
    def visit_print_stmt(self, stmt: Stmt.Print):
        return self.parenthesize("print", stmt.expression)

    def visit_var_stmt(self, stmt: Stmt.Var):
        return self.parenthesize(stmt.name, stmt.initializer)
    
    def visit_if_stmt(self, stmt: Stmt.If):
        return self.parenthesize("if", stmt.condition, stmt.then_branch, stmt.else_branch)

    def visit_while_stmt(self, stmt: Stmt.While):
        return self.parenthesize("while", stmt.condition, stmt.body)
    
    def visit_block_stmt(self, stmt: Stmt.Block):
        return self.parenthesize("block", *stmt.declarations)    

    def parenthesize(self, name: str, *exprs: Expr) -> str:
        builder = []

        builder.append(f"({name}")
        for expr in exprs:
            builder.append(" ")
            if expr is not None:
                builder.append(expr.accept(self))
        builder.append(")")

        return "".join(builder)
