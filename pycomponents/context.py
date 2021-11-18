class ContextDict(dict):
    def __init__(self, context, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context.dicts.append(self)
        self.context = context

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.context.pop()


class Context:
    def __init__(self, context={}):
        self.dicts = [context]

    def push(self, *args, **kwargs):
        return ContextDict(self, *args, **kwargs)

    def pop(self):
        self.dicts.pop()

    def __contains__(self, item):
        for d in self.dicts:
            if item in d:
                return True
        return False

    def __getitem__(self, item):
        for d in self.dicts:
            if item in d:
                return d[item]
        return None

    def __setitem__(self, key, value):
        self.dicts[-1][key] = value
