
class Sign:
    class Lt:
        def __init__(self):
            self.asm_type = 'comparsion_sign'
            self._rep = 'lt'
        def __str__(self):
            return 'jl'
        def __repr__(self):
            return f'{Sign}({self._rep})'
    class Gt:
        def __init__(self):
            self.asm_type = 'comparsion_sign'
            self._rep = 'gt'
        def __str__(self):
            return 'jg'
        def __repr__(self):
            return f'{Sign}({self._rep})'
    class Ge:
        def __init__(self):
            self.asm_type = 'comparsion_sign'
            self._rep = 'ge'
        def __str__(self):
            return 'jge'
        def __repr__(self):
            return f'{Sign}({self._rep})'

    class Le:
        def __init__(self):
            self.asm_type = 'comparsion_sign'
            self._rep = 'le'
        def __str__(self):
            return 'jle'
        def __repr__(self):
            return f'{Sign}({self._rep})'

    class Eq:
        def __init__(self):
            self.asm_type = 'comparsion_sign'
            self._rep = 'eq'
        def __str__(self):
            return 'je'
        def __repr__(self):
            return f'{Sign}({self._rep})'

    class Ne:
        def __init__(self):
            self.asm_type = 'comparsion_sign'
            self._rep = 'ne'
        def __str__(self):
            return 'jne'
        def __repr__(self):
            return f'{Sign}({self._rep})'