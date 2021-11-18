from abc import ABC, abstractmethod


class Section(ABC):
    @property
    @abstractmethod
    def parser(self):
        pass

    def parse(self, text):
        return self.parser.parse(text)


class Renderable(ABC):
    @abstractmethod
    def render(self, context):
        pass


class RenderableList(Renderable):
    def __init__(self, renderables):
        self.renderables = renderables

    def render(self, context):
        output = ''
        for renderable in self.renderables:
            output += renderable.render(context)
        return output
