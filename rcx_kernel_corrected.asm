; minimal_correct_rcx_kernel.asm
; Minimal RCX-π substrate with ONLY the three correct primitives
; No fancy features, no examples - just the core operations

section .data
    ; Memory pool - RCX-π memory space
    mem_pool        times 65536 db 0       ; 64KB memory space
    
    ; Execution state
    last_read_addr  dq 0                   ; Last address read by ∇R
    last_read_value db 0                   ; Last value read by ∇R
    
    ; Fix state tracking (minimal)
    fix_addr        dq 0                   ; Address being checked for fix
    fix_hash_prev   dq 0                   ; Previous hash for convergence
    fix_hash_curr   dq 0                   ; Current hash for convergence
    fix_stable      db 0                   ; 1 if converged, 0 if not

section .text
global _start
global nabla_r_op
global delta_op  
global fix_op

; ============================================================================
; ∇R Primitive: Memory Read/Traverse
; Input: rdi = memory address to read from
; Output: rax = value read (0-255)
; ============================================================================
nabla_r_op:
    ; Bounds check
    cmp rdi, 65536
    jae .out_of_bounds
    
    ; Read byte from memory pool
    movzx rax, byte [mem_pool + rdi]
    
    ; Store read state (for potential structural traversal)
    mov [last_read_addr], rdi
    mov [last_read_value], al
    
    ret

.out_of_bounds:
    xor rax, rax                           ; Return 0 for out of bounds
    ret

; ============================================================================ 
; Δ Primitive: Structural Modification/Descent
; Input: rdi = memory address to modify
; Output: none
; ============================================================================
delta_op:
    ; Bounds check
    cmp rdi, 65536
    jae .out_of_bounds
    
    ; Read current value
    movzx rax, byte [mem_pool + rdi]
    
    ; Simple modification: XOR with pattern based on address
    ; This creates address-dependent transformation
    mov rbx, rdi
    and rbx, 0xFF                          ; Use low byte of address as pattern
    xor al, bl                             ; XOR current value with address pattern
    
    ; Store modified value
    mov [mem_pool + rdi], al
    
    ret

.out_of_bounds:
    ret

; ============================================================================
; Fix Primitive: Convergence Detection
; Input: rdi = memory address to check for convergence
; Output: rax = 1 if converged, 0 if not converged
; ============================================================================
fix_op:
    ; Bounds check
    cmp rdi, 65536
    jae .out_of_bounds
    
    ; Store the address we're checking
    mov [fix_addr], rdi
    
    ; Simple hash: sum of 8 bytes starting at address
    xor rax, rax                           ; Clear accumulator
    mov rcx, 8                             ; Check 8 bytes
    mov rsi, rdi                           ; Start address
    
.hash_loop:
    cmp rsi, 65536                         ; Bounds check
    jae .hash_done
    
    movzx rbx, byte [mem_pool + rsi]       ; Read byte
    add rax, rbx                           ; Add to hash
    inc rsi                                ; Next byte
    dec rcx                                ; Decrement counter
    jnz .hash_loop
    
.hash_done:
    ; Store current hash
    mov [fix_hash_curr], rax
    
    ; Compare with previous hash
    mov rbx, [fix_hash_prev]
    cmp rax, rbx
    je .converged
    
    ; Not converged - update previous hash
    mov [fix_hash_prev], rax
    mov byte [fix_stable], 0
    xor rax, rax                           ; Return 0 (not converged)
    ret
    
.converged:
    ; Converged - hash unchanged
    mov byte [fix_stable], 1
    mov rax, 1                             ; Return 1 (converged)
    ret

.out_of_bounds:
    xor rax, rax
    ret

; ============================================================================
; Minimal test/demo entry point
; ============================================================================
_start:
    ; Initialize some test data
    mov byte [mem_pool + 0], 0x42
    mov byte [mem_pool + 1], 0x43
    mov byte [mem_pool + 2], 0x44
    
    ; Test ∇R: read from address 0
    mov rdi, 0
    call nabla_r_op                        ; Should return 0x42
    
    ; Test Δ: modify address 0
    mov rdi, 0  
    call delta_op                          ; Should XOR 0x42 with 0x00 = 0x42
    
    ; Test Fix: check convergence at address 0
    mov rdi, 0
    call fix_op                            ; Should return 0 (first time)
    
    ; Test Fix again (should converge since nothing changed)
    mov rdi, 0
    call fix_op                            ; Should return 1 (converged)
    
    ; Exit cleanly
    mov rax, 60                            ; sys_exit
    xor rdi, rdi                           ; exit code 0
    syscall

; ============================================================================
; Rule loading interface (for external injection)
; ============================================================================

; Load rule at runtime
; Input: rdi = rule index, rsi = pointer to 5-byte rule
load_rule:
    ; This would be called by external loader
    ; For now, just a placeholder
    ret

; Execute single rule
; Input: rdi = rule index  
execute_rule:
    ; This would dispatch to the appropriate primitive
    ; For now, just a placeholder
    ret