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
    def render(self, output, context):
        pass
