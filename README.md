# py_to_asm
Generate x86 GNU Assembly in a clean, concise format with Python.
```
import py_to_asm
with py_to_asm.Asm(_label_name = '_main', is_main = True) as asm:
    asm.declare('val', [16, 17, 18])
    asm.declare('val2', 15)
```
