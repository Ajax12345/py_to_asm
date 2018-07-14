import collections
import typing
import py_to_asm_wrappers
import asm_types
import py_asm_abstract, os
import contextlib, datetime

#TODO: depreciate valid label check and lookup?

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
        self._copies = {'inc':self.increment, 'dec':self.decrement, 'jmp':self.goto, 'jump':self.goto, 'asminteger':self.integer}
    def value_exists(self, name:str) -> bool:
        return any(i.name == name for i in self._data)

    def __contains__(self, _variable):
        return self.value_exists(_variable.name)

    @property
    def integer(self):
        @py_to_asm_wrappers.validate_asm_integer
        def __wrapper(_value:int):
            return asm_types.AsmInteger(_value)
        return __wrapper
    
    @property
    def asmfloat(self):
        @py_to_asm_wrappers.validate_asm_float
        def __wrapper(_value:float):
            return asm_types.AsmFloat(_value)
        return __wrapper

    
    def lea(self, dest, src) -> None:
        self._instructions.append(f'lea {str(src)}, {str(dest)}')
        self._disassembled.append(f'load {self.__class__.functionize(dest)}, {self.__class__.functionize(src)}')
   
    @property
    def stackref(self):
        return asm_types.StackVar(self._stack_count)

    @staticmethod
    def functionize(_type):
        return '{}({})'.format(_type.asm_type, _type._base)
    
    @py_to_asm_wrappers.is_valid_data
    def declare(self, _name:str, _to_store:[list, int, float]) -> None:
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

    @py_to_asm_wrappers.weak_operation_validate
    def add(self, dest, src) -> None:
        self._instructions.append(f'addl {str(src)}, {str(dest)}')
        self._disassembled.append(f'<left load: {self.__class__.functionize(dest)}')
        self._disassembled.append(f'<right load: {self.__class__.functionize(src)}')
        self._disassembled.append(f'add in_place=True')

    @py_to_asm_wrappers.validate_inplace
    def increment(self, _src) -> None:
        self._instructions.append(f'incl {str(_src)}')
        self._disassembled.append(f'increment {self.__class__.functionize(_src)}')
    
    @property
    def label(self):
        return asm_types._Label(self)
    
    def goto(self, _label, suppress_check=False):
        self._instructions.append(f'jmp {str(_label)}')
        self._disassembled.append(f'GOTO {str(_label)}')

    @py_to_asm_wrappers.validate_inplace
    def decrement(self, _src) -> None:
        self._instructions.append(f'decl {str(_src)}')
        self._disassembled.append(f'decrement {self.__class__.functionize(_src)}')

    @py_to_asm_wrappers.weak_operation_validate
    def sub(self, dest, src) -> None:
        self._instructions.append(f'subl {str(src)}, {str(dest)}')
        self._disassembled.append(f'<left load: {self.__class__.functionize(dest)}')
        self._disassembled.append(f'<right load: {self.__class__.functionize(src)}')
        self._disassembled.append(f'sub in_place=True')
    
    @py_to_asm_wrappers.mul_validate
    def mul(self, dest, src) -> None:
        self._instructions.append(f'imull {str(src)}, {str(dest)}')
        self._disassembled.append(f'multiply load: {self.__class__.functionize(dest)}')
        self._disassembled.append(f'<multiplier load: {self.__class__.functionize(src)}')
        self._disassembled.append(f'mul in_place=True')
    
    @py_to_asm_wrappers.div_validate
    def div(self, num, den, int_res = None, mod = None) -> None:
        self._instructions.append('idivl %ecx')
        self._disassembled.append('div')

    @py_to_asm_wrappers.compare_validate
    def cmp(self, left, right, operator, label):
        self._instructions.append(f'cmpl {str(right)}, {str(left)}')
        self._instructions.append(f'{str(operator)} {label}')
        self._disassembled.append(f'COMPARE {self.__class__.functionize(left)}, {self.__class__.functionize(right)}: {operator._rep} => {str(label)}')

    @property
    def operator(self):
        return asm_types._Comparision()

    @property
    def register(self):
        return asm_types._Register(self)

    def stackvalue(self, _val, increment=False):
        return asm_types.StackVar(_val*([1, 4][increment]))

    @py_to_asm_wrappers.check_value_exists
    def __getitem__(self, _name):
        return [i for i in self._data if i.name == _name][0]

    @property
    def variable(self):
        return asm_types._Variable(self)

    def label_exists(self, _name):
        print('in here')
        if self.label_name != _name:
            return getattr(self._next, 'label_exists', lambda _:False)(_name)
        return True

    def _get_dissassembled(self):
        return self._disassembled+getattr(self._next, '_get_dissassembled', lambda :[])()

    def dis(self) -> str:
        return '\n'.join(f'{i}  {a}' for i, a in enumerate(self._get_dissassembled(), 1))

    @contextlib.contextmanager
    @py_to_asm_wrappers.validate_filename
    def write(self, filename = None, run = False, compiler='gcc'):
        if not filename:
            d = datetime.datetime.now()
            filename = f'{__file__[:-3]}asm{"".join(str(getattr(d, i)) for i in ["month", "day", "year", "hour", "minute", "second"])}.s'
        with open(filename, 'w') as f:
            f.write(str(self))
        if run:
            os.system(f'{compiler} {filename}')
            os.system('./a.out')
        yield

        

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
    @py_to_asm_wrappers.validate_copy_lookup
    def __getattr__(self, _instruction):
        return self._copies[_instruction]

with Asm(_label_name = '_main', is_main = True) as asm:
    asm.declare('james', [16, 17, 18])
    asm.declare('joe', 15)
    asm.declare('lill', 30)
    asm.div(asm.variable.lill, asm.integer(2), int_res = asm.variable.result, mod=asm.variable.modulo)
    asm.mov(asm.register.EAX, asm.asmfloat(23.232))
    asm.mov(asm.stackref, asm.integer(20))
    asm.cmp(asm.integer(32), asm.variable.joe, asm.operator.eq, asm.label._james)
    with Asm(_label_name = '_james') as asm2:
        asm2.add(asm2.variable.joe, asm2.integer(2))

    asm.add_label(asm2)

  

print(asm)







