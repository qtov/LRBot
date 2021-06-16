from dataclasses import dataclass

@dataclass
class Command:
    def __init__(self, func, description):
        self.func = func
        self.description = description
        self.aliases = []

    def call(self, *args, **kargs):
        return self.func(*args, **kargs)
