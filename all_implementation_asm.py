

import py_to_asm

with py_to_asm.Asm(_label_name = '_main', is_main=True) as asm:
    asm.declare('input', [6, 4, 2, 8, 10])
    asm.declare('length', 5)
    asm.declare('success', 0)
    asm.mov(asm.stackref, asm.integer(0))
    asm.goto(asm.label.start_loop)
    with py_to_asm.Asm(_label_name = 'start_loop', stack_count = asm._stack_count, _parent_data = asm._data) as asm2:
        asm2.cmp(asm2.variable.length, asm2.stackref, asm2.operator.le, asm2.label.end_loop)
        asm2.div(asm2.variable.input[asm2.stackref], asm2.integer(2), mod = asm2.variable.mod)
        asm2.cmp(asm2.variable.mod, asm.integer(0), asm2.operator.ne, asm2.label.failed_all)
        asm2.inc(asm2.stackref)
        asm2.goto(asm2.label.start_loop)
        with py_to_asm.Asm(_label_name='end_loop') as asm3:
            asm3.mov(asm3.variable.success, asm3.integer(1))
            asm3.mov(asm3.register.EAX, asm3.variable.success)
        with py_to_asm.Asm(_label_name='failed_all') as asm4:
            asm4.mov(asm4.register.EAX, asm4.variable.success)
        
        asm2.add_label(asm3)
        asm2.add_label(asm4)
    asm.add_label(asm2)
    

with asm.write('generated_all_check.s', run=True) as _:
    pass

print(asm)

