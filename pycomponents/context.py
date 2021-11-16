class ContextDict(dict):
    def __init__(self, context, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context.dicts.append(self)
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self):
        self.context.pop()


class Context:
    def __init__(self):
        self.dicts = []

    def push(self, *args, **kwargs):
        return ContextDict(self, *args, **kwargs)

    def pop(self):
        self.dicts.pop()

    def __getitem__(self, item):
        for d in self.dicts:
            if item in d:
                return d[item]
        return None

    def __setitem__(self, key, value):
        self.dicts[-1][key] = value
