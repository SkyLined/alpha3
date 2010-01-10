 BITS 32
 
; This decoder requires EAX to point to its base ("start")
code        equ 0x31     ; magic value, MUST be ascii
code2       equ 0x41     ; magic value, MUST be ascii
eax_value   equ -0xC     ; magic value, must be set to a value that makes the
                         ; code 100% uppercase alphanumeric

start:
    XOR     [EBX], ESI                  ; [ESI] = base address ^ ESI
    XOR     ESI, [EBX]                  ; ESI = base address ^ ESI ^ ESI = base address
    PUSH    ESI                         ; [ESP0] = base address 
    POP     ECX                         ; ECX = base address
    PUSH    ESI                         ; [ESP0] = ESI
    PUSH    ESP                         ; [ESP1] = ESP0
    POP     EAX                         ; EAX = [ESP1] = ESP0
    XOR     [EAX], ESI                  ; [ESP0] = [ESP0] ^ ESI = ESI ^ ESI = 0
    POP     EAX                         ; EAX = [ESP0] = 0
    XOR     AL, code                    ; EAX = 0x31
    PUSH    EAX                         ; [ESP0] = 0x31
    POP     EDX                         ; EDX = [ESP0] = 0x31
    XOR     AL, code                    ; EAX = 0x31 ^ 0x31 = 0
    DEC     EAX                         ; EAX = -1
    XOR     AL, code2                   ; EAX = -1 ^ code2
al_value    equ 0xFF ^ (eax_value & 0xFF) ^ code2
    XOR     AL, al_value                ; EAX = -1 ^ code2 ^ al_value = eax_value
; DECODE 0x6B FOR IMUL INSTRUCTION
    XOR     [BYTE ECX+EAX*2 - eax_value*2 + imul_offset], EDX
; DECODE 0x75 FOR JNE INSTRUCTION
    XOR     [BYTE ECX+EAX*2 - eax_value*2 + jnz_offset], EDX

    PUSH    ESI                         ; [ESP0] = ESI
    PUSH    ESP                         ; [ESP1] = ESP0
    POP     EDX                         ; EDX = [ESP1] = ESP0
    XOR     ESI, [EDX]                  ; ESI = ESI ^ [ESP0] = ESI ^ ESI = 0
    PUSH    EAX
    POP     EDX
    DEC     ESI                         ; ESI = -1
esi_value   equ -1

loop:
; Some of these instructions can not be encoded using 100% uppercase
; alphanumeric characters. So I have replaced those bytes that were not 
; uppercase alphanumeric with bytes that are uppercase alphanumeric. These
; bytes will be "patched" before the loop runs to re-create the right bytes.
    INC     EDX                         ; EAX is used as an input index
    INC     ESI                         ; ESI is used as an output index
    ;IMUL EAX, [ECX+EDX*2 - (eax_value+1)*2 + data_offset], 30         ; JNZ offset EF ; Terminating 00
imul: db 0x6B^code, 0x44, 0x51, - (eax_value+1)*2 + data_offset, 0x30  ; 4A * 30 -> E0 ; 30 * 30 -> 00
imul_offset equ imul - start
    XOR     AL, [BYTE ECX+EDX*2 - (eax_value+1)*2 + data_offset + 1]   ; E0 ^ 45 -> A5 ; 00 ^ 45 -> 45
    XOR     [BYTE ECX+ESI - (esi_value+1) + data_offset], AL           ; 4A ^ A5 -> EF ; 45 ^ 45 -> 00 
jnz:  db 0x75^code                     ; JNZ loop
jnz_offset  equ jnz - start

; There is probably a way to calculate these, but it's easier to manually do it.
data:
data_offset equ data - start
    db 0x4A, 0x45 ; This decodes to EF
;   db 0x30, 0x45 ; This decodes to 00 can be used for testing
