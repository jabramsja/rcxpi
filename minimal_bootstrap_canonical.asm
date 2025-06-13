; Creates data structures in memory and outputs binary file

section .data
    motif_table     times 512 dq 0
    motif_count     dq 0
    proj_table      times 1024 dq 0
    proj_count      dq 0
    closure_table   times 256 dq 0
    closure_count   dq 0
    
    output_buffer   times 1024 db 0

section .text
global _start

create_motif:
    mov rax, [motif_count]
    mov [motif_table + rax * 8], rdi
    inc qword [motif_count]
    ret

create_projection:
    mov rax, rdi
    shl rax, 32
    or rax, rsi
    mov rbx, [proj_count]
    mov [proj_table + rbx * 8], rax
    mov rax, rbx
    inc qword [proj_count]
    ret

create_closure:
    mov rax, [closure_count]
    mov [closure_table + rax * 8], rdi
    inc qword [closure_count]
    ret

build_data_structures:
    ; Store 3 values in table
    mov rdi, 0x50415253
    call create_motif
    
    mov rdi, 0x434F4D50
    call create_motif
    
    mov rdi, 0x4556414C
    call create_motif
    
    ; Store index pair
    mov rdi, 0
    mov rsi, 1
    call create_projection
    
    ; Store reference
    mov rdi, 0
    call create_closure
    
    ret

write_binary:
    mov rdi, output_buffer
    
    ; Write header bytes
    mov dword [rdi], 0x00584352
    add rdi, 4
    
    ; Write count
    mov qword [rdi], 2
    add rdi, 8
    
    ; Write opcodes and addresses
    mov byte [rdi], 0x01
    mov dword [rdi+1], 0x3000
    add rdi, 5
    
    mov byte [rdi], 0x02
    mov dword [rdi+1], 0x3000
    add rdi, 5
    
    ; Write padding
    mov rcx, 32
    xor rax, rax
    rep stosb
    
    ; Calculate size
    mov rdx, rdi
    sub rdx, output_buffer
    
    ; Write to stdout
    mov rax, 1
    mov rdi, 1
    mov rsi, output_buffer
    syscall
    
    ret

_start:
    mov qword [motif_count], 0
    mov qword [proj_count], 0
    mov qword [closure_count], 0
    
    call build_data_structures
    call write_binary
    
    mov rax, 60
    xor rdi, rdi
    syscall