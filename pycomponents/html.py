from abc import ABC, abstractmethod
import html

from lark import Lark, Transformer, v_args

from .base import Renderable, RenderableList, Section
from .indenter import ParserIndenter


class Value(ABC):
    def __init__(self, value):
        self.value = value

    @abstractmethod
    def resolve(self, context):
        pass


class Primitive(Value):
    def resolve(self, context):
        return self.value


class Array(Value):
    def resolve(self, context):
        res = []
        for item in self.value:
            res.append(item.resolve(context))
        return res


class Dictionary(Value):
    def resolve(self, context):
        res = {}
        for key, value in self.value.items():
            res[key.resolve(context)] = value.resolve(context)
        return res


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
        return context[self.value] if html.escape(self.value) in context else None


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


class TextLine(Renderable):
    def __init__(self, parts):
        self.parts = parts

    def render(self, context):
        output = ''
        for part in self.parts:
            output += part.resolve(context)
        if output[0] == ' ':
            output = output[1:]
        return output


class ForLoop(Renderable):
    def __init__(self, identifier, iterable, body):
        self.identifier = identifier
        self.iterable = iterable
        self.body = body

    def render(self, context):
        output = ''
        iterable = self.iterable.resolve(context)
        for i in iterable:
            with context.push(i=i):
                output += self.body.render(context)
        return output


class HTMLSectionTransformer(Transformer):
    @v_args(inline=True)
    def block(self, *blocks):
        return RenderableList(blocks)

    @v_args(inline=True)
    def attr(self, key, value):
        return Attr(str(key), value)

    def attrs_list(self, attrs):
        return attrs

    @v_args(inline=True)
    def tag(self, identifier, attrs, body):
        return Tag(identifier, attrs, body)

    @v_args(inline=True)
    def text(self, text):
        return Primitive(str(text))

    def textline(self, parts):
        return TextLine(parts)

    @v_args(inline=True)
    def forloop(self, identifier, iterable, body):
        return ForLoop(identifier, iterable, body)

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
    def number(self, value):
        return Primitive(float(value))

    true = lambda self, _: Primitive(True)
    false = lambda self, _: Primitive(False)
    none = lambda self, _: Primitive(None)

    @v_args(inline=True)
    def identifier(self, identifier):
        return str(identifier)


class HTMLSection(Section):
    parser = Lark(r'''
        ?start: _NL* compound
        
        ?compound: tag | forloop
        ?simple: textline _NL
        
        block: _NL _INDENT (compound | simple)+ _DEDENT
        
        attr: identifier "=" value
        attrs_list: "(" [attr ("," attr)*] ")"
        tag: identifier [attrs_list] ":" block
        
        text: /[^{\r\n]+/
        ?textexpr: "{" value "}"
        textline: "-" (text | textexpr)+
        
        forloop: "for" identifier "in" value ":" block
        
        ?value: dict
            | list
            | string
            | CNAME -> variable
            | SIGNED_NUMBER -> number
            | "True" -> true
            | "False" -> false
            | "None" -> none
        dict: "{" [pair ("," pair)*] "}"
        pair: value ":" value
        list: "[" [value ("," value)*] "]"
        string: ESCAPED_STRING
        
        identifier: CNAME

        %import common.CNAME
        %import common.ESCAPED_STRING
        %import common.SIGNED_NUMBER
        
        %declare _INDENT _DEDENT
        
        %ignore /[\t \f]+/
        
        _NL: /(\r?\n[\t ]*)+/
    ''', parser='lalr', transformer=HTMLSectionTransformer(), postlex=ParserIndenter())
