from abc import ABC, abstractmethod


class Section(ABC):
    def __init__(self, source):
        self.source = source
        self.parser_result = self.parser.parse(self.source)

    @property
    @abstractmethod
    def parser(self):
        pass

    def render(self, context):
        return self.parser_result.render(context)


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
