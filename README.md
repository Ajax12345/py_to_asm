# py_to_asm
Generate x86 GNU Assembly in a clean, concise format with Python.
```
import py_to_asm

with py_to_asm.Asm(_label_name = '_main', is_main=True) as asm:
    asm.declare('input', [6, 4, 2, 8, 10])
    asm.declare('length', 5)
    asm.declare('success', 0)
    asm.mov(asm.stackref, asm.integer(0))
    asm.mov(asm.variable.length, asm.variable.success)
    asm.add(asm.variable.length, asm.integer(10))
    asm.cmp(asm.variable.length, asm.integer(18), asm.operator.eq, asm.label.end_resuls)
    with py_to_asm.Asm(_label_name = 'end_results', stack_count=asm._stack_count) as asm2:
        asm2.inc(asm2.stackref)
    asm.add_label(asm2)    
```


###result
```
.data
	input:.int 6, 4, 2, 8, 10
	length:.int 5
	success:.int 0

.text
.globl _main
_main:
	pushq %rbp
	movq %rsp, %rbp
	subq $16, %rsp
	movl $0, -4(%rbp)
	movl success(%rip), %eax
	movl %eax, length(%rip)
	addl $10, length(%rip)
	cmpl $18, length(%rip)
	je end_resuls
	leave
	ret




end_results:
	incl -4(%rbp)
	leave
	ret
```
