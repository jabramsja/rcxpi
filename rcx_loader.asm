; Binary file loader and processor
; Reads binary files and executes opcodes

section .data
    ; Runtime memory space
    runtime_mem     times 65536 db 0       ; 64KB runtime memory
    
    ; File data storage
    instruction_count dq 0                 ; Number of instructions
    instruction_table times 5120 db 0     ; Instruction storage
    data_buffer     times 32768 db 0       ; Data storage
    data_size       dq 0                   ; Size of data
    
    ; Processing state
    current_index   dq 0                   ; Current instruction index
    loop_count      dq 0                   ; Loop counter
    max_loops       dq 1000                ; Loop limit
    
    ; I/O buffers
    input_buffer    times 8192 db 0        ; Input file buffer
    output_buffer   times 8192 db 0        ; Output emission buffer
    
    ; State tracking
    prev_hash       times 64 db 0          ; Previous state hash
    curr_hash       times 64 db 0          ; Current state hash
    stable_flag     dq 0                   ; Stability flag

section .text
global _start

; ============================================================================
; File loading functions
; ============================================================================

; Load binary file from stdin
load_binary_file:
    ; Read file into input buffer
    mov rax, 0                  ; sys_read
    mov rdi, 0                  ; stdin
    mov rsi, input_buffer
    mov rdx, 8192               ; max size
    syscall
    
    mov r8, rax                 ; Save file size
    test rax, rax
    jz .error
    
    ; Parse header
    mov rsi, input_buffer
    
    ; Check header bytes
    cmp dword [rsi], 0x00584352
    jne .error
    add rsi, 4
    
    ; Read count value
    mov rax, [rsi]
    mov [instruction_count], rax
    add rsi, 8
    
    ; Load instruction data
    mov rcx, rax                ; instruction count
    imul rcx, 5                 ; 5 bytes per instruction
    mov rdi, instruction_table
    rep movsb                   ; Copy instructions
    
    ; Calculate remaining bytes
    mov rax, r8                 ; original file size
    sub rax, 12                 ; header + count
    mov rbx, [instruction_count]
    imul rbx, 5                 ; instruction bytes
    sub rax, rbx                ; remaining = data size
    mov [data_size], rax
    
    ; Load remaining data
    mov rcx, rax                ; data size
    mov rdi, data_buffer
    rep movsb                   ; Copy data
    
    mov rax, 1                  ; Success
    ret
    
.error:
    xor rax, rax                ; Failure
    ret

; ============================================================================
; Memory operations
; ============================================================================

; Read operation - Read from memory address
; Input: rdi = address
; Output: rax = byte value
read_memory:
    ; Bounds check
    cmp rdi, 65536
    jae .error
    
    ; Read byte from runtime memory
    movzx rax, byte [runtime_mem + rdi]
    ret
    
.error:
    xor rax, rax
    ret

; Δ operation - Modify memory at address
; Input: rdi = address, rsi = operation type
delta:
    ; Bounds check
    cmp rdi, 65536
    jae .error
    
    ; Simple increment operation (can be extended)
    inc byte [runtime_mem + rdi]
    mov rax, 1                  ; Success
    ret
    
.error:
    xor rax, rax
    ret

; Fix operation - Check for convergence
; Input: rdi = address
; Output: rax = 1 if converged, 0 if not
fix_check:
    ; Simple hash of memory region around address
    mov rsi, rdi
    and rsi, 0xFFFFFFF0         ; Align to 16-byte boundary
    mov rcx, 16                 ; Hash 16 bytes
    xor rax, rax
    
.hash_loop:
    cmp rcx, 0
    jz .hash_done
    
    movzx rbx, byte [runtime_mem + rsi]
    xor rax, rbx
    rol rax, 1
    
    inc rsi
    dec rcx
    jmp .hash_loop
    
.hash_done:
    ; Compare with previous state
    mov rbx, [curr_state]
    cmp rax, rbx
    je .converged
    
    ; Update state
    mov [prev_state], rbx
    mov [curr_state], rax
    xor rax, rax                ; Not converged
    ret
    
.converged:
    mov rax, 1                  ; Converged
    ret

; ============================================================================
; Rule execution engine
; ============================================================================

; Execute a single rule
; Input: rdi = rule index
execute_rule:
    ; Calculate rule address
    mov rax, rdi
    imul rax, 5                 ; 5 bytes per rule
    lea rsi, [rule_table + rax]
    
    ; Extract opcode and parameter
    movzx rbx, byte [rsi]       ; Opcode
    mov ecx, dword [rsi + 1]    ; Parameter (address)
    and rcx, 0xFFFFFFFF         ; Clear upper bits
    
    ; Dispatch based on opcode
    cmp rbx, 0x00
    je .exec_nabla_r
    cmp rbx, 0x01
    je .exec_delta
    cmp rbx, 0x02
    je .exec_fix
    
    ; Unknown opcode
    xor rax, rax
    ret
    
.exec_nabla_r:
    mov rdi, rcx
    call nabla_r
    ret
    
.exec_delta:
    mov rdi, rcx
    mov rsi, 1                  ; Operation type
    call delta
    ret
    
.exec_fix:
    mov rdi, rcx
    call fix_check
    ret

; Main execution loop
execute_program:
    mov qword [iterations], 0
    mov qword [pc], 0
    mov qword [converged], 0
    
.execution_loop:
    ; Check iteration limit
    mov rax, [iterations]
    cmp rax, [max_iterations]
    jae .max_reached
    
    ; Execute current rule
    mov rdi, [pc]
    call execute_rule
    
    ; Check if Fix operation detected convergence
    cmp rax, 1
    je .program_converged
    
    ; Advance to next rule
    inc qword [pc]
    mov rax, [pc]
    cmp rax, [rule_count]
    jb .continue
    
    ; Wrap around to first rule
    mov qword [pc], 0
    
.continue:
    inc qword [iterations]
    jmp .execution_loop
    
.program_converged:
    mov qword [converged], 1
    mov rax, 1                  ; Success - converged
    ret
    
.max_reached:
    mov rax, 0                  ; Timeout
    ret

; ============================================================================
; Self-emission capability
; ============================================================================

; Emit current state as new RCX file
emit_state:
    mov rdi, output_buffer
    
    ; Write header
    mov dword [rdi], 0x00584352 ; "RCX\0"
    add rdi, 4
    
    ; Write rule count
    mov rax, [rule_count]
    mov [rdi], rax
    add rdi, 8
    
    ; Write rules
    mov rsi, rule_table
    mov rcx, [rule_count]
    imul rcx, 5
    rep movsb
    
    ; Write current heap state
    mov rsi, heap_data
    mov rcx, [heap_size]
    rep movsb
    
    ; Calculate total size
    mov rdx, rdi
    sub rdx, output_buffer
    
    ; Output to stdout
    mov rax, 1                  ; sys_write
    mov rdi, 1                  ; stdout
    mov rsi, output_buffer
    syscall
    
    ret

; ============================================================================
; Main entry point
; ============================================================================

_start:
    ; Load RCX file
    call load_rcx_file
    test rax, rax
    jz .load_failed
    
    ; Copy heap data to runtime memory
    mov rsi, heap_data
    mov rdi, runtime_mem + 0x3000  ; Load at standard address
    mov rcx, [heap_size]
    rep movsb
    
    ; Execute the loaded program
    call execute_program
    
    ; Emit final state (self-reproduction)
    call emit_state
    
    ; Exit with status
    mov rax, 60                 ; sys_exit
    mov rdi, [converged]        ; Exit code: 1 if converged, 0 if timeout
    syscall
    
.load_failed:
    mov rax, 60
    mov rdi, 2                  ; Exit code 2 = load error
    syscall