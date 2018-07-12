from functools import wraps
import asm_errors, warnings

def is_valid_data(f):
    @wraps(f)
    def wrapper(cls, name, _to_store):
        if type(_to_store) not in f.__annotations__['_to_store']:
            raise TypeError(f'data values can only be integers or lists, but got {type(_to_store).__name__}')
        cls._disassembled.append(f'declare {name}, {"int" if isinstance(_to_store, int) else "array"}({_to_store if isinstance(_to_store, int) else ", ".join(map(str, _to_store))})')
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
        if (dest.asm_type == 'variable' or dest.asm_type == 'stackvar') and (src.asm_type == 'variable' or src.asm_type == 'stackvar'):
            if dest.asm_type == 'variable' and not cls.value_exists(dest.name):
                cls.declare(dest.name, 0)
            cls.mov(cls.register.EAX, src)
            return f(cls, dest, cls.register.EAX)
        if dest.asm_type == 'stackvar' and src.asm_type == 'stackvar':
            cls.mov(cls.register.EAX, src)
            if stack_assign:
                cls._stack_count += 4
            return f(cls, cls.stackref, cls.register.EAX)
        if dest.asm_type == 'stackvar' and stack_assign:
            cls._stack_count += 4
            return f(cls, cls.stackref, src)
        if dest.asm_type == 'register' and dest._base == 'rsi':
            cls._instructions.append(f'movslq {str(src)}, {str(dest)}')
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
