import py_to_asm_wrappers
import typing

class AsmInteger:
    def __init__(self, _val:int) -> None:
        self.name = _val
        self.asm_type = 'integer'
        self._base = _val
    def __repr__(self):
        return f'{self.__class__.__name__}({self.name})'
    def __str__(self):
        return f'${self.name}'
    
class StackVar:
    def __init__(self, _loc:int):
        self.loc = _loc
        self.asm_type = 'stackvar'
        self._base = _loc
    def __str__(self):
        return f'-{self.loc}(%rbp)'
    


class StaticStorage:
    def __init__(self, _name, _data):
        self.name = _name
        self._data = _data
    def __str__(self):
        return f'{self.name}:.int {", ".join(map(str, self._data)) if isinstance(self._data, list) else self._data}'
    def __repr__(self):
        return f"<variable '{self.name}':{'array' if isinstance(self._data, list) else 'int'}({self._data if isinstance(self._data, int) else ', '.join(map(str, self._data))})"

class Register:
    converter = {'RAX': 64, 'RCX': 64, 'RDX': 64, 'RBX': 64, 'RSP': 64, 'RBP': 64, 'RSI': 64, 'RDI': 64, 'EAX': 32, 'ECX': 32, 'EDX': 32, 'EBX': 32, 'ESP': 32, 'EBP': 32, 'ESI': 32, 'EDI': 32, 'AX': 16, 'CX': 16, 'DX': 16, 'BX': 16, 'SP': 16, 'BP': 16, 'SI': 16, 'DI': 16, 'AH': 8, 'AL': 8, 'CH': 8, 'CL': 8, 'DH': 8, 'DL': 8, 'BH': 8, 'BL': 8}
    def __init__(self, name:str) -> None:
        self.name = name
        self.bits = self.__class__.converter[name]
        self.asm_type = 'register'
        self._base = name.lower()
    def __str__(self):
        return f'%{self.name.lower()}'
    def __repr__(self):
        return f'<{self.__class__.__name__} "{self.name.lower()}"'

class _Register:
    '''
    Register, Accumulator, Counter, Data, Base, Stack Pointer, Stack Base Pointer, Source, Destination
    64 Bit: RAX, RCX, RDX, RBX, RSP, RBP, RSI, RDI
    32 Bit: EAX, ECX, EDX, EBX, ESP, EBP, ESI, EDI
    16 Bit: AX, CX, DX, BX, SP, BP, SI, DI
    8 Bit: AH, AL, CH, CL, DH, DL, BH, BL
    '''
    registers = ['RAX', 'RCX', 'RDX', 'RBX', 'RSP', 'RBP', 'RSI', 'RDI', 'EAX', 'ECX', 'EDX', 'EBX', 'ESP', 'EBP', 'ESI', 'EDI', 'AX', 'CX', 'DX', 'BX', 'SP', 'BP', 'SI', 'DI', 'AH', 'AL', 'CH', 'CL', 'DH', 'DL', 'BH', 'BL']
    def __init__(self, _ref:typing.Callable[[str, bool], None]):
        self._main = _ref
    @py_to_asm_wrappers.validate_register
    def __getattr__(self, _register):
        return Register(_register.upper())

class Variable:
    def __init__(self, name:str, _home):
        self.name = name
        self.home = _home
        self.asm_type = 'variable'
        self._base = name
    def __str__(self):
        return f'{self.name}(%rip)'
    

class _Variable:
    def __init__(self, _main):
        self.ref = _main

    @py_to_asm_wrappers.validate_variable
    def __getattr__(self, _variable):
        return Variable(_variable, self.ref)
    