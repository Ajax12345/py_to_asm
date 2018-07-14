from functools import wraps
import asm_errors, warnings
import re


def is_valid_data(f):
    @wraps(f)
    def wrapper(cls, name, _to_store):
        if type(_to_store) not in f.__annotations__['_to_store']:
            raise TypeError(f'data values can only be integers or lists, but got {type(_to_store).__name__}')
        cls._disassembled.append(f'declare {name}, {type(_to_store).__name__ if not isinstance(_to_store, list) else "array"}({_to_store if not isinstance(_to_store, list) else ", ".join(map(str, _to_store))})')
        return f(cls, name, _to_store)
    return wrapper

def setup_created(tear_down = False):
    def outer(f):
        def wrapper(cls, *args):
            setattr(cls, '_valid_label_setup', not tear_down)
            return f(cls, *args)
        return wrapper
    return outer

def check_warning(f):
    def wrapper(cls, *args, **kwargs):
        if not cls.suppress_warnings:
            if not getattr(cls, '_valid_label_setup'):
                warnings.warn('instruction created outside label')
        return f(cls, *args, **kwargs)
    return wrapper

def validate_register(f):
    def wrapper(cls, _name):
        if _name.upper() not in cls.__class__.registers:
            print('Use this table for reference:')
            print(cls.__class__.__doc__)
            raise asm_errors.InvalidRegister(f"'{_name}' not a valid register")
        return f(cls, _name)
    return wrapper

def validate_asm_integer(f):
    @wraps(f)
    def wrapper(_val):
        if not isinstance(_val, int):
            raise TypeError("'Asminteger' must be an integer")
        return f(_val)
    return wrapper


def validate_mov_params(f):
    def __wrapper(cls, _dest, _src, stack_assign=False):
        if _dest.asm_type == 'integer':
            raise asm_errors.InvalidMovDestination(f"Destination of {str(_src)} cannot be an integer")
        return f(cls, _dest, _src, stack_assign)
    return __wrapper

def validate_mov(f):
    @validate_mov_params
    def wrapper(cls, dest, src, stack_assign = False):
        if src.asm_type == 'arrayindex' and dest.asm_type not in ['register', 'integer']:
            cls.mov(cls.register.EAX, src)
            cls.mov(dest, cls.register.EAX)
            return 
        if dest.asm_type == 'arrayindex' and getattr(src, '_base', '') != 'esi':
            cls.mov(cls.register.ESI, src)
            cls.mov(dest, cls.register.ESI)
            return
        if dest.asm_type == 'stackvar' and src.asm_type == 'stackvar':
            cls.mov(cls.register.EAX, src)
            if stack_assign:
                cls._stack_count += 4
            return f(cls, cls.stackref, cls.register.EAX)
        if (dest.asm_type == 'variable' or dest.asm_type == 'stackvar') and (src.asm_type == 'variable' or src.asm_type == 'stackvar'):
            print('here 1', stack_assign)
            if dest.asm_type == 'variable' and not cls.value_exists(dest.name):
                cls.declare(dest.name, 0)
            cls.mov(cls.register.EAX, src)
            if stack_assign:
                cls._stack_count += 4
            return f(cls, dest if dest.asm_type != 'stackvar' else cls.stackref, cls.register.EAX)
        if dest.asm_type == 'stackvar' and stack_assign:
            cls._stack_count += 4
            return f(cls, cls.stackref, src)
        if (src.asm_type == 'register' or src.asm_type == 'variable' or src.asm_type == 'stackvar') and dest.asm_type == 'register' and dest._base == 'rsi':
            cls._instructions.append(f'movslq {str(src)}, {str(dest)}')
            cls._disassembled.append('set {}, {}'.format(cls.__class__.functionize(dest), cls.__class__.functionize(src)))
            return
        if dest.asm_type == 'register' and dest._base == 'rsi':
            cls._instructions.append(f'mov {str(src)}, {str(dest)}')
            cls._disassembled.append('set {}, {}'.format(cls.__class__.functionize(dest), cls.__class__.functionize(src)))
            return
        return f(cls, dest, src)
        
    return wrapper


def validate_variable(f):
    def wrapper(cls, _name, supress = True):
        if not supress:
            if not cls.ref.value_exists(_name):
                raise asm_errors.VariableNotDeclared(f"'{_name} not declared'")
        return f(cls, _name)
    return wrapper

def validate_index_array(f):
    @wraps(f)
    def wrapper(cls, _):
        if not isinstance(cls.home[cls.name]._data, list):
            raise asm_errors.InvalidIndexAccess(f"array index operations must be performed on an array.")
        return f(cls, _)
    return wrapper

def check_value_exists(f):
    def wrapper(cls, _name):
        if not cls.value_exists(_name):
            raise asm_errors.VariableNotDeclared(f"variable '{_name}' not declared")
        return f(cls, _name)
    return wrapper

def validate_filename(f):
    def wrapper(cls, filename=None, run=False, compiler='gcc'):
        if filename:
            if not re.findall('\.s$', filename):
                raise IOError('Invalid filename')
        return f(cls, filename=filename, run=run, compiler=compiler)
    return wrapper

def weak_operation_validate(f):
    def wrapper(cls, _dest, _src):
        if all(i.asm_type in ['stackvar', 'variable', 'arrayindex'] for i in [_dest, _src]):
            if _dest.asm_type == 'variable' and _dest not in cls:
                cls.declare(_dest.name, 0)
            cls.mov(cls.register.EAX, _src)
            return f(cls, _dest, cls.register.EAX)
        if _dest.asm_type == 'register' and _dest._base.lower() == 'rsi' and _src.asm_type=='integer':
            cls._instructions.append(f'{f.__name__} {str(_src)}, {str(_dest)}')
            cls._disassembled.append(f'<left load: {cls.__class__.functionize(_dest)}')
            cls._disassembled.append(f'<right load: {cls.__class__.functionize(_src)}')
            cls._disassembled.append(f'{f.__name__} in_place=True')
            return
        return f(cls, _dest, _src)
    return wrapper

def compare_validate(f):
    def wrapper(cls, left, right, operator, label):
        if left.asm_type in ['integer', 'float']:
            cls.mov(cls.register.EAX, left)
            return f(cls, cls.register.EAX, right, operator, label)
        if all(i.asm_type in ['variable', 'stackvar', 'arrayindex'] for i in [left, right]):
            cls.mov(cls.register.EAX, right)
            f(cls, left, cls.register.EAX, operator, label)
            return
        return f(cls, left, right, operator, label)
    return wrapper

def mul_validate(f):
    def wrapper(cls, _dest, _src):
        if _dest.asm_type != 'register':
            cls.mov(cls.register.EAX, _dest)
            f(cls, cls.register.EAX, _src)
            cls.mov(_dest, cls.register.EAX)
            return
        return f(cls, _dest, _src)
    return wrapper


def div_validate(f):
    def wrapper(cls, _num, _den, int_res = None, mod = None):
        cls.mov(cls.register.EAX, _num)
        cls.mov(cls.register.ECX, _den)
        cls.mov(cls.register.EDX, cls.integer(0))
        f(cls, _num, _den, int_res = int_res, mod = mod)
        if int_res is not None:
            if int_res.asm_type == 'variable' and int_res not in cls:
                cls.declare(int_res.name, 0)
            cls.mov(int_res, cls.register.EAX)
        if mod is not None:
            if mod.asm_type == 'variable' and mod not in cls:
                cls.declare(mod.name, 0)
            cls.mov(mod, cls.register.EDX)
    return wrapper


def validate_asm_float(f):
    def wrapper(_val:float):
        if not isinstance(_val, float):
            raise TypeError("'AsmFloat' object must be passed a float value")
        return f(_val)
    return wrapper

def validate_inplace(f):
    def wrapper(cls, src):
        if src.asm_type in ['integer', 'float']:
            raise TypeError(f"'{src.asm_type}' data reference cannot be {f.__name__}ed")
        if src.asm_type == 'register' and src._base.lower() == 'rsi':
            cls._instructions.append(f'{f.__name__[:3]} {str(src)}')
            cls._disassembled.append(f'{f.__name__} {cls.__class__.functionize(src)}')
            return
        return f(cls, src)
    return wrapper


def validate_copy_lookup(f):
    def wrapper(cls, _instruc):
        if _instruc not in cls._copies:
            raise AttributeError(f"'{cls.__class__.__name__}' has no attribute '{_instruc}'")
        return f(cls, _instruc)
    return wrapper

def validate_label_name(f):
    def wrapper(cls, _name):
        if not cls._ref.label_exists(_name):
            raise asm_errors.InvalidLabelName(f"Label '{_name}' not created")
        return f(cls, _name)
    return wrapper

def validate_comparison_sign(f):
    def wrapper(cls, _sign):
        if _sign.lower() not in cls._convert:
            raise asm_errors.InvalidComparisonSign(f"'{_sign}' is not a valid comparison sign.")
        return f(cls, _sign)
    return wrapper
