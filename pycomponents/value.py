from abc import ABC, abstractmethod
import html


class Value(ABC):
    @abstractmethod
    def resolve(self, context):
        pass


class Primitive(Value):
    def __init__(self, value):
        self.value = value

    def resolve(self, context):
        return self.value


class Array(Primitive):
    def resolve(self, context):
        res = []
        for item in self.value:
            res.append(item.resolve(context))
        return res


class Dictionary(Primitive):
    def resolve(self, context):
        res = {}
        for key, value in self.value.items():
            res[key.resolve(context)] = value.resolve(context)
        return res


class Variable(Primitive):
    def resolve(self, context):
        return html.escape(context[self.value]) if self.value in context else None


class BinaryExpression(Value):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def resolve(self, context):
        return eval(f'{self.left.resolve(context)} {self.op} {self.right.resolve(context)}')

    @property
    @abstractmethod
    def op(self):
        pass


class AddExpression(BinaryExpression):
    op = '+'


class SubExpression(BinaryExpression):
    op = '-'


class MulExpression(BinaryExpression):
    op = '*'


class DivExpression(BinaryExpression):
    op = '/'
