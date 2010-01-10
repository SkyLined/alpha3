import ALPHA3

LOCAL_PATH = __path__[0]

def encodeShellcode(base_address, shellcode):
  decoder = ALPHA3.io.ReadFile("%s.bin" % base_address, LOCAL_PATH)
  return ALPHA3.encode.encodeData(decoder, shellcode,
      ALPHA3.encode.wyx_IMUL_30_SHR_8_XOR_bx, # Use this encoding function
     ALPHA3.charsets.valid_charcodes["ascii"]["lowercase"])  # And these characters to encode

encoders = [{
    "base address": "^(ECX|EDX|EBX)$",
    "base address samples": ["ECX", "EDX", "EBX"],
    "name": r"AscLow 0x30 (rm32)",
    "function": encodeShellcode,
    "tests": {
      "ecx": ["[$]=ascii:con", "ecx=$", "eip=$"],
      "edx": ["[$]=ascii:con", "edx=$", "eip=$"],
      "ebx": ["[$]=ascii:con", "ebx=$", "eip=$"]
    }
}]
