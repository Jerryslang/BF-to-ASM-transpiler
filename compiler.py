import subprocess, time

def transpile(bf_code):
    asm = ['section .bss', 'tape: resb 30000', 'section .text', 'global _start', '_start:', '    mov rsi, tape          ; data pointer']
    loop_stack = []
    loop_count = 0

    i = 0
    while i < len(bf_code):
        c = bf_code[i]

        # optimize exec of same command
        count = 1
        while i + 1 < len(bf_code) and bf_code[i + 1] == c and c in '+-<>':
            count += 1
            i += 1

        if c == '>':
            asm.append(f'    add rsi, {count}          ; pointer right')
        elif c == '<':
            asm.append(f'    sub rsi, {count}          ; pointer left')
        elif c == '+':
            asm.append(f'    add byte [rsi], {count}  ; increment cell')
        elif c == '-':
            asm.append(f'    sub byte [rsi], {count}  ; decrement cell')
        elif c == '.':
            for _ in range(count):
                asm += [
                    '    mov rax, 1              ; sys_write',
                    '    mov rdi, 1              ; stdout',
                    '    mov rdx, 1              ; write 1 byte',
                    '    syscall'
                ]
        elif c == ',':
            for _ in range(count):
                asm += [
                    '    mov rax, 0              ; sys_read',
                    '    mov rdi, 0              ; stdin',
                    '    mov rdx, 1              ; read 1 byte',
                    '    syscall'
                ]
        elif c == '[':
            start_label = f'loop_start_{loop_count}'
            end_label = f'loop_end_{loop_count}'
            loop_stack.append((start_label, end_label))
            loop_count += 1

            asm.append(f'{start_label}:')
            asm.append('    cmp byte [rsi], 0')
            asm.append(f'    je {end_label}')
        elif c == ']':
            start_label, end_label = loop_stack.pop()
            asm.append('    cmp byte [rsi], 0')
            asm.append(f'    jne {start_label}')
            asm.append(f'{end_label}:')
        i += 1

    # exit syscall
    asm.append('    mov rax, 60                  ; sys_exit')
    asm.append('    xor rdi, rdi                 ; status 0')
    asm.append('    syscall')

    return '\n'.join(asm)

def compile(asm_file='out.asm', obj_file='out.o', exe_file='out'):
    subprocess.run(['nasm', '-f', 'elf64', asm_file, '-o', obj_file], check=True) # compile to object
    subprocess.run(['ld', obj_file, '-o', exe_file], check=True) # link / make executable
    print(f'compiled / linked: {exe_file}')

brainfuck_file = 'test.b'
out_file = 'out'

start_time = time.time()
asm_code = transpile(open(brainfuck_file).read())

with open(f'{out_file}.asm', 'w') as f:
    f.write(asm_code)

print(f"Assembly code written to {out_file}.asm")
compile(f'{out_file}.asm', f'{out_file}.o', out_file)

end_time = time.time()
elapsed = end_time - start_time

print(f"Took {elapsed:.4f} seconds")
