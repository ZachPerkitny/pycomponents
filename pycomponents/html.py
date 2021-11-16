from abc import ABC, abstractmethod

from lark import Lark, Transformer, v_args

from .base import Renderable, Section
from .indenter import ParserIndenter


class Value(ABC):
    def __init__(self, value):
        self.value = value

    @abstractmethod
    def resolve(self, context):
        pass


class Literal(Value):
    def resolve(self, context):
        return self.value


class Function(Value):
    def __init__(self, value, arguments):
        super().__init__(value)
        self.arguments = arguments

    def resolve(self, context):
        if self.value not in context:
            return None
        value = context[self.value]
        if not callable(value):
            return None
        arguments = [arg.resolve(context) for arg in self.arguments]
        return value(*arguments)


class Variable(Value):
    def resolve(self, context):
        return context[self.value] if self.value in context else None


class Tag(Renderable):
    def __init__(self, name, attrs):
        self.name = name
        self.attrs = attrs

    def render(self, output, context):
        output += f'<{self.name}>'
        for attr in self.attrs:
            attr.render(output, context)
        output += f'</{self.name}>'


class Attr(Renderable):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def render(self, output, context):
        output += f'{self.key}="{self.value.resolve(context)}"'


class ForLoop(Renderable):
    def __init__(self, identifier, iterable, body):
        self.identifier = identifier
        self.iterable = iterable
        self.body = body

    def render(self, output, context):
        try:
            iterable = context[self.iterable]
            for i in iterable:
                with context.push(i=i):
                    self.body.render(output, context)
        except KeyError:
            raise


class HTMLSectionTransformer(Transformer):
    def number(self, value):
        return Literal()

    def list(self, values):
        return Literal(list(values))

    pair = tuple

    def dict(self, pairs):
        return Literal(dict(pairs))

    true = lambda self, _: True
    false = lambda self, _: False
    none = lambda self, _: None

    @v_args(inline=True)
    def tag(self, name, *attrs):
        return Tag(name, attrs)

    @v_args(inline=True)
    def attr(self, key, value):
        return Attr(key, value)


class HTMLSection(Section):
    parser = Lark(r'''
        start: _NL* html
        html: forloop | tag | _NL
        
        tag: CNAME ["(" [attr ("," attr)*] ")"]
        attr: CNAME "=" value
        
        forloop: "for" CNAME "in" value ":" _NL _INDENT html+ _DEDENT [_NL]
        
        value: dict
            | list
            | string
            | CNAME -> variable
            | SIGNED_NUMBER -> number
            | "True" -> true
            | "False" -> false
            | "None" -> none
        dict: "{" [pair ("," pair)*] "]"
        pair: string ":" value
        list: "[" [value ("," value)*] "]"
        string: ESCAPED_STRING

        %import common.CNAME
        %import common.ESCAPED_STRING
        %import common.NEWLINE
        %import common.SIGNED_NUMBER
        %import common.WS_INLINE
        
        %declare _INDENT _DEDENT
        
        %ignore WS_INLINE
        
        _NL: /(\r?\n[\t ]*)+/
    ''', parser='lalr', transformer=HTMLSectionTransformer(), postlex=ParserIndenter())
