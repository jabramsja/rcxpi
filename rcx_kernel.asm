; rcx_kernel.asm - Native x86-64 RCX-π Kernel
; Full implementation following the cookbook specifications
; Supports runtime rule loading and native gate execution

section .data
    ; Memory management
    mem_pool        times 1048576 db 0     ; 1MB memory pool
    mem_pos         dq 0                   ; Current allocation position
    
    ; Rule system - runtime loadable
    rule_count      dq 0                   ; Number of rules (set by loader)
    rule_mem        times 5120 db 0        ; 1024 rules * 5 bytes (loaded at runtime)
    
    ; Gate table for dynamic dispatch
    gate_table      times 1024 dq 0        ; Gate function pointers
    gate_code_pool  times 32768 db 0       ; Pool for generated gate code
    gate_code_pos   dq 0                   ; Current code generation position
    
    ; State tracking
    state_hash      times 64 db 0          ; Current state hash
    prev_hash       times 64 db 0          ; Previous state hash
    iter_count      dq 0                   ; Iteration counter
    fix_threshold   dq 3                   ; Convergence threshold
    max_iterations  dq 100000              ; Safety limit
    
    ; Divergence logging
    div_log         times 8192 db 0        ; Divergence log buffer
    div_pos         dq 0                   ; Log position
    
    ; I/O buffers
    seed_buffer     times 8192 db 0        ; Output seed buffer
    
    ; Scratch memory windows (for payload hydration)
    scratch_windows times 15*16 db 0       ; 15 windows * 16 bytes each

section .text
global _start

; ============================================================================
; Core memory management
; ============================================================================

; Allocate memory from pool
; Input: rdi = size in bytes
; Output: rax = pointer (or 0 if failed)
get_mem:
    mov rax, [mem_pos]
    mov rbx, rax
    add rbx, rdi
    cmp rbx, 1048576                       ; Check pool limit
    ja .overflow
    
    mov [mem_pos], rbx
    lea rax, [mem_pool + rax]
    ret
.overflow:
    xor rax, rax
    ret

; ============================================================================
; Hash computation for state tracking
; ============================================================================

; Compute BLAKE2b-like hash of memory state
; Input: none
; Output: stores hash in state_hash
hash_state:
    ; Simple hash of first 1KB of memory pool
    mov rsi, mem_pool
    mov rdi, state_hash
    mov rcx, 1024
    mov rax, 0x6A09E667F3BCC908           ; BLAKE2b IV
    
.hash_loop:
    test rcx, rcx
    jz .done
    
    movzx rbx, byte [rsi]
    xor rax, rbx
    rol rax, 7
    inc rsi
    dec rcx
    jmp .hash_loop
    
.done:
    mov [state_hash], rax
    
    ; Store additional hash words
    mov [state_hash + 8], rax
    ror rax, 13
    mov [state_hash + 16], rax
    rol rax, 23
    mov [state_hash + 24], rax
    ret

; Compare current hash with previous
; Output: ZF set if equal
compare_hashes:
    mov rsi, state_hash
    mov rdi, prev_hash
    mov rcx, 8                             ; Compare first 64 bytes
    repe cmpsq
    ret

; Copy current hash to previous
update_prev_hash:
    mov rsi, state_hash
    mov rdi, prev_hash
    mov rcx, 8
    rep movsq
    ret

; ============================================================================
; Dynamic gate code generation
; ============================================================================

; Generate executable code for a gate from 5-byte rule
; Input: rdi = rule index, rsi = pointer to 5-byte rule
; Output: installs handler in gate_table
build_gate_from_rule:
    ; Validate rule index
    cmp rdi, 1024
    jae .invalid
    
    ; Get code generation space (32 bytes per gate)
    mov rax, [gate_code_pos]
    mov rbx, rax
    add rbx, 32
    cmp rbx, 32768
    ja .no_space
    mov [gate_code_pos], rbx
    
    ; Calculate code address
    lea rdx, [gate_code_pool + rax]
    mov [gate_table + rdi*8], rdx
    
    ; Read rule components
    movzx rcx, byte [rsi]                  ; Operation type
    mov r8d, [rsi + 1]                     ; 32-bit parameter
    
    ; Generate code based on operation type
    cmp rcx, 0
    je .gen_nabla_r
    cmp rcx, 1
    je .gen_delta
    cmp rcx, 2
    je .gen_fix
    jmp .gen_nop
    
.gen_nabla_r:
    ; Generate: mov rax, param; mov byte [mem_pool + rax], al; ret
    mov byte [rdx], 0x48                   ; REX.W
    mov byte [rdx+1], 0xB8                 ; mov rax, imm64
    mov [rdx+2], r8                        ; parameter (32-bit, zero-extended)
    mov dword [rdx+6], 0                   ; high 32 bits
    
    ; mov byte [mem_pool + rax], al
    mov byte [rdx+10], 0x88                ; mov [rax+disp32], al
    mov byte [rdx+11], 0x80
    lea rax, [mem_pool]
    mov [rdx+12], eax                      ; disp32 = mem_pool address
    
    mov byte [rdx+16], 0xC3                ; ret
    ret
    
.gen_delta:
    ; Generate: mov rax, param; xor byte [mem_pool + rax], 0xFF; ret
    mov byte [rdx], 0x48                   ; REX.W
    mov byte [rdx+1], 0xB8                 ; mov rax, imm64
    mov [rdx+2], r8                        ; parameter
    mov dword [rdx+6], 0
    
    ; xor byte [mem_pool + rax], 0xFF
    mov byte [rdx+10], 0x80                ; xor [rax+disp32], imm8
    mov byte [rdx+11], 0xB0
    lea rax, [mem_pool]
    mov [rdx+12], eax                      ; disp32
    mov byte [rdx+16], 0xFF                ; immediate 0xFF
    
    mov byte [rdx+17], 0xC3                ; ret
    ret
    
.gen_fix:
    ; Generate: call hash_state; ret (simplified)
    mov byte [rdx], 0xE8                   ; call rel32
    lea rax, [hash_state]
    sub rax, rdx
    sub rax, 5                             ; relative to end of call instruction
    mov [rdx+1], eax                       ; rel32 offset
    mov byte [rdx+5], 0xC3                 ; ret
    ret
    
.gen_nop:
    ; Generate: ret
    mov byte [rdx], 0xC3
    ret
    
.invalid:
.no_space:
    ret

; ============================================================================
; Gate dispatch system
; ============================================================================

; Execute gate by index
; Input: rdi = gate index
gate_dispatch:
    cmp rdi, 1024
    jae .invalid
    
    mov rax, [gate_table + rdi*8]
    test rax, rax
    jz .no_handler
    
    ; Call the generated gate code
    call rax
    ret
    
.invalid:
.no_handler:
    ret

; ============================================================================
; Rule mutation and divergence logging
; ============================================================================

; Log rule change for divergence tracking
; Input: rdi = rule index, rsi = new rule data
log_divergence:
    mov rax, [div_pos]
    cmp rax, 8192
    jae .overflow
    
    ; Simple log entry: timestamp + rule_index + rule_data
    lea rbx, [div_log + rax]
    
    ; Get timestamp (iteration count as proxy)
    mov rcx, [iter_count]
    mov [rbx], rcx                         ; 8 bytes: timestamp
    mov [rbx + 8], rdi                     ; 8 bytes: rule index
    
    ; Copy 5-byte rule
    mov rcx, 5
    lea rdi, [rbx + 16]
    rep movsb
    
    add qword [div_pos], 32                ; Advance log position
.overflow:
    ret

; Mutate rule and rebuild gate
; Input: rdi = rule index, rsi = new 5-byte rule
mutate_rule:
    ; Bounds check
    cmp rdi, 1024
    jae .invalid
    
    ; Calculate rule memory location
    mov rax, rdi
    imul rax, 5
    lea rdx, [rule_mem + rax]
    
    ; Log the divergence
    push rdi
    push rsi
    call log_divergence
    pop rsi
    pop rdi
    
    ; Copy new rule to memory
    mov rcx, 5
    rep movsb
    
    ; Rebuild gate
    call build_gate_from_rule
    
.invalid:
    ret

; ============================================================================
; Seed emission
; ============================================================================

; Emit full system seed to stdout
emit_full_seed:
    mov rdi, seed_buffer
    
    ; Write seed header: "RCX\0"
    mov dword [rdi], 0x00584352
    add rdi, 4
    
    ; Write rule count
    mov rax, [rule_count]
    mov [rdi], rax
    add rdi, 8
    
    ; Write rules
    mov rax, [rule_count]
    imul rax, 5                            ; Total rule bytes
    mov rsi, rule_mem
    mov rcx, rax
    rep movsb
    
    ; Calculate total seed size
    mov rdx, rdi
    sub rdx, seed_buffer
    
    ; Write to stdout
    mov rax, 1                             ; sys_write
    mov rdi, 1                             ; stdout
    mov rsi, seed_buffer
    syscall
    
    ret

; ============================================================================
; Main iteration engine
; ============================================================================

; Main RCX-π iteration loop
main_loop:
    mov qword [iter_count], 0
    
.iteration:
    ; Apply all gates in sequence
    mov rdi, 0
.gate_loop:
    cmp rdi, [rule_count]
    jae .gates_done
    
    call gate_dispatch
    inc rdi
    jmp .gate_loop
    
.gates_done:
    ; Hash state and check convergence
    call hash_state
    call compare_hashes
    jz .check_convergence
    
    ; State changed - update previous hash and continue
    call update_prev_hash
    inc qword [iter_count]
    
    ; Check iteration limit
    mov rax, [iter_count]
    cmp rax, [max_iterations]
    jb .iteration
    
    ; Max iterations reached
    jmp .converged
    
.check_convergence:
    ; State unchanged - we've converged
.converged:
    ret

; ============================================================================
; Initialization and entry point
; ============================================================================

; Initialize gate table from loaded rules
init_gates:
    mov rdi, 0
.loop:
    cmp rdi, [rule_count]
    jae .done
    
    ; Calculate rule address
    mov rax, rdi
    imul rax, 5
    lea rsi, [rule_mem + rax]
    
    ; Build gate
    call build_gate_from_rule
    
    inc rdi
    jmp .loop
.done:
    ret

; Entry point - expects rule_count and rule_mem to be loaded
_start:
    ; Initialize the system
    call init_gates
    
    ; Run main iteration
    call main_loop
    
    ; Emit final seed
    call emit_full_seed
    
    ; Exit cleanly
    mov rax, 60                            ; sys_exit
    xor rdi, rdi                           ; exit code 0
    syscall

; ============================================================================
; Runtime loader interface (for external tools)
; ============================================================================

; Entry point for runtime rule loading
; Expects: rule data already copied to rule_mem, rule_count set
load_and_run:
    jmp _start