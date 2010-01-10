BITS 32
; See http://skypher.com/wiki/index.php/Hacking/Shellcode/GetPC
    CALL      INC_EBX                   ; $+0 = E8 FFFFFFFF   PUSH  $+5
INC_EBX equ $-1                         ; $+4 = FFC3          INC EBX
    RETN                                ; $+5 = C3
    POP       ECX                       ; $+6 = 58            POP ECX