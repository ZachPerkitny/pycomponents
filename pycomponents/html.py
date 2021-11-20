from lark import Lark, Transformer, v_args

from .base import Renderable, RenderableList, Section
from .indenter import ParserIndenter
from .value import *


class Tag(Renderable):
    def __init__(self, name, attrs, body):
        self.name = name
        self.attrs = attrs
        self.body = body

    def render(self, context):
        output = ''
        output += f'<{self.name}'
        for attr in self.attrs:
            output += f' {attr.render(context)}'
        output += '>'
        output += self.body.render(context)
        output += f'</{self.name}>'
        return output


class Attr(Renderable):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def render(self, context):
        return f'{self.key}="{self.value.resolve(context)}"'


class IfStmt(Renderable):
    def __init__(self, expression, if_body, else_body):
        self.expression = expression
        self.if_body = if_body
        self.else_body = else_body

    def render(self, context):
        res = self.expression.resolve(context)
        if res:
            return self.if_body.render(context)
        return self.else_body.render(context)


class ForStmt(Renderable):
    def __init__(self, identifier, iterable, body):
        self.identifier = identifier
        self.iterable = iterable
        self.body = body

    def render(self, context):
        output = ''
        iterable = self.iterable.resolve(context)
        for i in iterable:
            with context.push(**{self.identifier: i}):
                output += self.body.render(context)
        return output


class Assignment(Renderable):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def render(self, context):
        context[self.identifier] = self.value.resolve(context)
        return ''


class TextLine(Renderable):
    def __init__(self, parts):
        self.parts = parts

    def render(self, context):
        output = ''
        for part in self.parts:
            output += str(part.resolve(context))
        if output[0] == ' ':
            output = output[1:]
        return output


class HTMLSectionTransformer(Transformer):
    def start(self, stmts):
        return RenderableList(stmts)

    @v_args(inline=True)
    def block(self, *blocks):
        return RenderableList(blocks)

    @v_args(inline=True)
    def attr(self, key, value):
        return Attr(str(key), value)

    def attrs_list(self, attrs):
        return attrs

    @v_args(inline=True)
    def assignment(self, identifier, value):
        return Assignment(str(identifier), value)

    @v_args(inline=True)
    def text(self, text):
        return Primitive(str(text))

    def textline(self, parts):
        return TextLine(parts)

    @v_args(inline=True)
    def ifstmt(self, expression, if_body, else_body):
        return IfStmt(expression, if_body, else_body)

    @v_args(inline=True)
    def forstmt(self, identifier, iterable, body):
        return ForStmt(identifier, iterable, body)

    @v_args(inline=True)
    def tag(self, identifier, attrs, body):
        return Tag(identifier, attrs, body)

    @v_args(inline=True)
    def add(self, left, right):
        return AddExpression(left, right)

    @v_args(inline=True)
    def sub(self, left, right):
        return SubExpression(left, right)

    @v_args(inline=True)
    def mul(self, left, right):
        return MulExpression(left, right)

    @v_args(inline=True)
    def div(self, left, right):
        return DivExpression(left, right)

    pair = tuple

    def dict(self, pairs):
        return Dictionary(pairs)

    def list(self, values):
        return Array(values)

    @v_args(inline=True)
    def string(self, value):
        return Primitive(value[1:-1])

    @v_args(inline=True)
    def variable(self, value):
        return Variable(str(value))

    @v_args(inline=True)
    def integer(self, value):
        return Primitive(int(value))

    @v_args(inline=True)
    def float(self, value):
        return Primitive(float(value))

    true = lambda self, _: Primitive(True)
    false = lambda self, _: Primitive(False)
    none = lambda self, _: Primitive(None)

    @v_args(inline=True)
    def identifier(self, identifier):
        return str(identifier)


class HTMLSection(Section):
    parser = Lark(r'''
        start: _NL* stmt+
        
        ?stmt: simple | compound
        ?compound: ifstmt | forstmt | tag
        ?simple: (assignment | textline) _NL
        
        block: _NL _INDENT stmt+ _DEDENT 
        
        ifstmt: "if" expression ":" block [elsestmt | elifstmt]
        elifstmt: "elif" expression ":" block [elsestmt | elifstmt] -> ifstmt
        ?elsestmt: "else" ":" block
        
        forstmt: "for" identifier "in" value ":" block
        
        attr: identifier "=" value
        attrs_list: "(" [attr ("," attr)*] ")"
        tag: identifier [attrs_list] ":" block
        
        assignment: "var" identifier "=" expression
        
        text: /[^{}\r\n]+/
        ?textexpr: "{" expression "}"
        textline: "-" (text | textexpr)+
        
        ?expression: sum
        ?sum: product
            | sum "+" product -> add
            | sum "-" product -> sub
        ?product: value
            | product "*" value -> mul
            | product "/" value -> div
        
        ?value: dict
            | list
            | string
            | CNAME -> variable
            | SIGNED_INT -> integer
            | SIGNED_FLOAT -> float
            | "True" -> true
            | "False" -> false
            | "None" -> none
            | "(" expression ")"
        dict: "{" [pair ("," pair)*] "}"
        pair: value ":" value
        list: "[" [value ("," value)*] "]"
        string: ESCAPED_STRING
        
        identifier: CNAME

        %import common.CNAME
        %import common.ESCAPED_STRING
        %import common.SIGNED_FLOAT
        %import common.SIGNED_INT
        
        %declare _INDENT _DEDENT
        
        %ignore /[\t \f]+/
        
        _NL: /(\r?\n[\t ]*)+/
    ''', parser='lalr', transformer=HTMLSectionTransformer(), postlex=ParserIndenter())
