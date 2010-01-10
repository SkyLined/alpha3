import ALPHA3

LOCAL_PATH = __path__[0]

def encodeShellcode(base_address, shellcode):
  decoder = ALPHA3.io.ReadFile("%s.bin" % base_address.upper(), LOCAL_PATH)
  return ALPHA3.encode.encodeData(decoder, shellcode,
     ALPHA3.encode.bx_IMUL_30_XOR_by, # Use this encoding function
     ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])  # And these characters to encode

encoders = [{
    "base address": "^(EAX|ECX|EDX|EBX|ESP|EBP|ESI|EDI|" +
          r"\[EAX\]|\[ECX\]|\[EDX\]|\[EBX\]|\[ESP\]|\[EBP\]|\[ESI\]|\[EDI\]|" +
          r"\[ESP-4\]|ECX\+2|ESI\+4|ESI\+8)$",
    "base address samples": ["EAX", "ECX", "EDX", "EBX", "ESP", "EBP", "ESI", 
          "EDI", "[EAX]", "[ECX]", "[EDX]", "[EBX]", "[ESP]", "[EBP]", "[ESI]", 
          "[EDI]", "[ESP-4]", "ECX+2", "ESI+4", "ESI+8"],
    "name": r"AscMix 0x30 (rm32)",
    "function": encodeShellcode,
    "tests": {
      "eax": ["[$]=ascii:con", "eax=$", "eip=$"],
      "ecx": ["[$]=ascii:con", "ecx=$", "eip=$"],
      "edx": ["[$]=ascii:con", "edx=$", "eip=$"],
      "ebx": ["[$]=ascii:con", "ebx=$", "eip=$"],
      "esp": ["[$+800]=ascii:con", "esp=$+800", "eip=$+800"], # leave some room for stack
      "ebp": ["[$]=ascii:con", "ebp=$", "eip=$"],
      "esi": ["[$]=ascii:con", "esi=$", "eip=$"],
      "edi": ["[$]=ascii:con", "edi=$", "eip=$"],
      "[eax]": ["[$]=value:$+4", "[$+4]=ascii:con", "eax=$", "eip=$+4"],
      "[ecx]": ["[$]=value:$+4", "[$+4]=ascii:con", "ecx=$", "eip=$+4"],
      "[edx]": ["[$]=value:$+4", "[$+4]=ascii:con", "edx=$", "eip=$+4"],
      "[ebx]": ["[$]=value:$+4", "[$+4]=ascii:con", "ebx=$", "eip=$+4"],
      "[esp]": ["[$+800]=value:$+804", "[$+804]=ascii:con", "esp=$+800", "eip=$+804"], # leave some room for stack
      "[ebp]": ["[$]=value:$+4", "[$+4]=ascii:con", "ebp=$", "eip=$+4"],
      "[esi]": ["[$]=value:$+4", "[$+4]=ascii:con", "esi=$", "eip=$+4"],
      "[edi]": ["[$]=value:$+4", "[$+4]=ascii:con", "edi=$", "eip=$+4"],
      "[esp-4]": ["[$]=ascii:con", "eip=$"], # ret makes sure [esp-4] == $
      "ecx+2": ["[$]=ascii:con", "ecx=$-2", "eip=$"],
      "esi+4": ["[$]=ascii:con", "esi=$-4", "eip=$"],
      "esi+8": ["[$]=ascii:con", "esi=$-8", "eip=$"]
    }
}]

