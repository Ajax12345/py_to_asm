import collections
import typing
import py_to_asm_wrappers
import asm_types
import py_asm_abstract


class Asm(py_asm_abstract.PyToAssembly):
    def __init__(self, _label_name = None, is_main=False, suppress_warnings = False, stack_count = 4):
        self._data = []
        self._next = None
        self._setup = []
        self.label_name = _label_name
        self.is_main = is_main
        self._instructions = []
        self._disassembled = ['scope:None' if self.label_name is None else f'scope<{self.label_name}>' if not self.is_main else f'scope<{self.label_name}, globl=True>']
        self.suppress_warnings = suppress_warnings
        self._stack_count = stack_count

    def value_exists(self, name:str) -> bool:
        return any(i.name == name for i in self._data)

    @property
    def integer(self):
        @py_to_asm_wrappers.validate_asm_integer
        def __wrapper(_value:int):
            return asm_types.AsmInteger(_value)
        return __wrapper
    @property
    def stackref(self):
        return asm_types.StackVar(self._stack_count)

    @staticmethod
    def functionize(_type):
        return '{}({})'.format(_type.asm_type, _type._base)
    
    @py_to_asm_wrappers.is_valid_data
    def declare(self, _name:str, _to_store:[list, int]) -> None:
        self._data.append(asm_types.StaticStorage(_name, _to_store))

    @py_to_asm_wrappers.validate_mov
    def mov(self, dest, src, stack_assign=False) -> None:
        self._instructions.append(f'movl {str(src)}, {str(dest)}')
        self._disassembled.append('set {}, {}'.format(self.__class__.functionize(dest), self.__class__.functionize(src)))

    @py_to_asm_wrappers.setup_created()
    def __enter__(self):
        if self.is_main:
            self._setup.extend(['.text', f'.globl {self.label_name}'])
            self._instructions.extend(['pushq %rbp', 'movq %rsp, %rbp', 'subq $16, %rsp'])
            self._disassembled.append(f'<setup {self.label_name}>')
        return self

    @property
    def register(self):
        return asm_types._Register(self)

    def stackvalue(self, _val):
        return asm_types.StackVar(_val)


    @property
    def variable(self):
        return asm_types._Variable(self)

    def _get_dissassembled(self):
        return self._disassembled+getattr(self._next, '_get_dissassembled', lambda :[])()

    def dis(self) -> str:
        return '\n'.join(self._get_dissassembled())

    @py_to_asm_wrappers.setup_created(tear_down = True)
    def __exit__(self, *args):
        self._instructions.extend(['leave', 'ret'])
        self._disassembled.append(f'<exit {self.label_name}>')
    def __bool__(self):
        #tells if instance is global main
        return self.is_main
    def __repr__(self):
        return f'<{self.__class__.__name__.lower()}: label={self.label_name}, length:{len(self._instructions)}>'
    def add_label(self, _label):
        getattr(self._next, 'add_label', lambda x:setattr(self, '_next', x))(_label)
    def get_data(self):
        return self._data + getattr(self._next, 'get_data', lambda :[])()

    def __str__(self) -> str:
        _data_formatted = '.data\n{}'.format('\n'.join('\t{}'.format(str(i)) for i in self.get_data())) if self.is_main else ''
        _setup_formatted = '\n'.join(self._setup)
        _body = '{}:\n{}'.format(self.label_name, '\n'.join('\t{}'.format(i) for i in self._instructions))+'\n\n'+str(self._next if self._next is not None else '')
        return f'{_data_formatted}\n\n{_setup_formatted}\n{_body}'
    

with Asm(_label_name = '_main', is_main = True) as asm:
    asm.declare('james', [16, 17, 18])
    asm.declare('joe', 15)
    asm.mov(asm.stackref, asm.integer(5))
    asm.mov(asm.stackref, asm.integer(10), stack_assign = True)
    asm.mov(asm.stackref, asm.integer(200))
    asm.mov(asm.stackref, asm.stackvalue(4), stack_assign=True)
    with Asm(_label_name = 'loop', stack_count = asm._stack_count) as asm1:
        asm1.mov(asm1.stackref, asm.integer(10), stack_assign = True)
        asm1.declare('lilly', 12)
        asm1.mov(asm1.variable.mom, asm1.variable.lilly)
    
    with Asm(_label_name = 'check_results', stack_count = asm1._stack_count) as asm2:
        asm2.mov(asm2.stackref, asm2.integer(4), stack_assign=True)
    
    
    asm.add_label(asm1)
    asm.add_label(asm2)

print(asm)





