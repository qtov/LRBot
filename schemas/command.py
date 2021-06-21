from dataclasses import dataclass

@dataclass
class Command:
    def __init__(self, func, description, args=None):
        self.func = func
        self.description = description
        self.aliases = []
        # Used only for help message
        self.args = args

    def call(self, *args, **kargs):
        return self.func(*args, **kargs)
