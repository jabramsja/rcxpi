; Assembly substrate implementation
; Graph manipulation using operations:
; Motif (μ), Projection (→), Closure ([→]), Activation (*)

section .data
    ; Graph memory - motifs and projections stored as linked structures
    graph_memory    times 4096 db 0       ; Graph storage space
    
    ; Motif table - each motif is an ID and optional label
    motif_table     times 512 dq 0        ; 64 motifs max (8 bytes each)
    motif_count     dq 0                   ; Current number of motifs
    
    ; Projection table - source motif, target motif pairs
    proj_table      times 1024 dq 0       ; 128 projections max (8 bytes each)
    proj_count      dq 0                   ; Current number of projections
    
    ; Closure table - reusable projection structures
    closure_table   times 256 dq 0        ; 32 closures max (8 bytes each)
    closure_count   dq 0                   ; Current number of closures
    
    ; Execution state
    active_motif    dq 0                   ; Currently active motif
    match_found     dq 0                   ; 1 if projection matched, 0 if not

section .text
global _start

; ============================================================================
; Motif function: Create or reference atomic unit μ
; Input: rdi = motif label/ID
; Output: rax = motif index
; ============================================================================
create_motif:
    ; Check if motif already exists
    mov rcx, 0
.check_existing:
    cmp rcx, [motif_count]
    jae .create_new
    
    cmp rdi, [motif_table + rcx * 8]
    je .found_existing
    
    inc rcx
    jmp .check_existing
    
.found_existing:
    mov rax, rcx                           ; Return existing motif index
    ret
    
.create_new:
    ; Check capacity
    cmp qword [motif_count], 64
    jae .error
    
    ; Add new motif
    mov rax, [motif_count]
    mov [motif_table + rax * 8], rdi       ; Store motif label
    inc qword [motif_count]
    ret
    
.error:
    mov rax, -1                            ; Error: table full
    ret

; ============================================================================
; Projection function: Create mapping μ1 → μ2
; Input: rdi = source motif index, rsi = target motif index
; Output: rax = projection index
; ============================================================================
create_projection:
    ; Check capacity
    cmp qword [proj_count], 128
    jae .error
    
    ; Store projection as 64-bit value: high 32 bits = source, low 32 bits = target
    mov rax, rdi
    shl rax, 32                            ; Move source to high 32 bits
    or rax, rsi                            ; Add target to low 32 bits
    
    mov rbx, [proj_count]
    mov [proj_table + rbx * 8], rax       ; Store projection
    
    mov rax, rbx                           ; Return projection index
    inc qword [proj_count]
    ret
    
.error:
    mov rax, -1
    ret

; ============================================================================
; Closure function: Create reusable projection structure [→]
; Input: rdi = projection index
; Output: rax = closure index
; ============================================================================
create_closure:
    ; Check capacity
    cmp qword [closure_count], 32
    jae .error
    
    ; Store closure
    mov rax, [closure_count]
    mov [closure_table + rax * 8], rdi    ; Store projection index
    inc qword [closure_count]
    ret
    
.error:
    mov rax, -1
    ret

; ============================================================================
; Activation function: Apply closure to motif (*)
; Input: rdi = closure index, rsi = motif index
; Output: rax = result motif index, rbx = 1 if changed, 0 if no match
; ============================================================================
activate_closure:
    ; Get the projection from the closure
    cmp rdi, [closure_count]
    jae .error
    
    mov rcx, [closure_table + rdi * 8]    ; Get projection index
    
    ; Get the projection details
    cmp rcx, [proj_count]
    jae .error
    
    mov rdx, [proj_table + rcx * 8]       ; Get projection (source|target)
    
    ; Extract source and target motifs
    mov rax, rdx
    shr rax, 32                            ; Source motif = high 32 bits
    mov rbx, rdx
    and rbx, 0xFFFFFFFF                    ; Target motif = low 32 bits
    
    ; Check if input motif matches source
    cmp rsi, rax
    je .match_found
    
    ; No match - return original motif
    mov rax, rsi                           ; Return input motif unchanged
    mov rbx, 0                             ; No change flag
    ret
    
.match_found:
    ; Match found - return target motif
    mov rax, rbx                           ; Return target motif
    mov rbx, 1                             ; Change flag
    ret
    
.error:
    mov rax, rsi                           ; Return input motif on error
    mov rbx, 0                             ; No change
    ret

; ============================================================================
; Graph evolution: Apply all closures until no more changes
; Input: rdi = starting motif index
; Output: rax = final motif index
; ============================================================================
evolve_graph:
    mov rax, rdi                           ; Current motif
    
.evolution_loop:
    mov r8, 0                              ; Any changes flag
    mov rcx, 0                             ; Closure index
    
.try_closure:
    cmp rcx, [closure_count]
    jae .check_changes
    
    ; Try activating current closure
    mov rdi, rcx                           ; Closure index
    mov rsi, rax                           ; Current motif
    call activate_closure
    
    ; Check if anything changed
    test rbx, rbx
    jz .next_closure
    
    ; Change occurred - update current motif and set change flag
    ; rax already contains the new motif
    mov r8, 1                              ; Set change flag
    
.next_closure:
    inc rcx
    jmp .try_closure
    
.check_changes:
    ; If any changes occurred, continue evolution
    test r8, r8
    jnz .evolution_loop
    
    ; No more changes - evolution complete
    ret

_start:
    ; Test graph manipulation operations
    
    ; Create motifs: μ(A), μ(B), μ(C)
    mov rdi, 0x41                          ; 'A'
    call create_motif
    mov r8, rax                            ; Save motif A index
    
    mov rdi, 0x42                          ; 'B'  
    call create_motif
    mov r9, rax                            ; Save motif B index
    
    mov rdi, 0x43                          ; 'C'
    call create_motif
    mov r10, rax                           ; Save motif C index
    
    ; Create projection: μ(A) → μ(B)
    mov rdi, r8                            ; Source: motif A
    mov rsi, r9                            ; Target: motif B
    call create_projection
    mov r11, rax                           ; Save projection index
    
    ; Create closure: [μ(A) → μ(B)]
    mov rdi, r11                           ; Projection index
    call create_closure
    mov r12, rax                           ; Save closure index
    
    ; Test 1: Activate closure with matching motif A
    mov rdi, r12                           ; Closure index
    mov rsi, r8                            ; Input: motif A
    call activate_closure
    ; Result should be motif B (r9) with change flag (rbx = 1)
    
    ; Test 2: Activate closure with non-matching motif C  
    mov rdi, r12                           ; Closure index
    mov rsi, r10                           ; Input: motif C
    call activate_closure
    ; Result should be motif C (r10) with no change flag (rbx = 0)
    
    ; Test 3: Graph evolution starting from motif A
    mov rdi, r8                            ; Start with motif A
    call evolve_graph
    ; Result should be motif B (final evolved state)
    
    ; Output the final evolved motif index as single byte
    mov rdi, 1                             ; stdout
    mov rdx, 1                             ; 1 byte
    push rax                               ; Save result on stack
    mov rsi, rsp                           ; Point to result on stack
    mov rax, 1                             ; sys_write
    syscall
    pop rax                                ; Clean stack
    
    ; Exit successfully
    mov rax, 60                            ; sys_exit
    xor rdi, rdi                           ; exit code 0
    syscall