import collections
import typing
import py_to_asm_wrappers
import asm_types, abc

class PyToAssembly(abc.ABC):
    @abc.abstractmethod
    def value_exists(self, name:str) -> bool:
        '''
        checks if a static value has been created
        '''
        return 
    @abc.abstractmethod
    def dis(self) -> str:
        '''
        returns the full assembly translated to the dissassembly
        '''
        return
        
    @abc.abstractmethod
    @py_to_asm_wrappers.is_valid_data
    def declare(self, _name:str, _to_store:[list, int]) -> None:
        '''
        equivalent to:
        {.data}
            ...
            _name:.int {_to_store}
        '''
        return
    @abc.abstractmethod
    @py_to_asm_wrappers.validate_mov
    def mov(self, dest, src, stack_assign=False) -> None:
        '''
        equivalent to 
        movl stc, dest
        --------------
        however, performs background moves, checks, and validations
        --------------
        :stack_assign => if a stackref variable is passed, the stackref counter will be incremented
        '''
        return
