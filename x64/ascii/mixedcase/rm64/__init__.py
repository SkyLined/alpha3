import ALPHA3

LOCAL_PATH = __path__[0]

def encodeShellcode(base_address, shellcode):
  decoder = ALPHA3.io.ReadFile("%s.bin" % base_address.upper(), LOCAL_PATH)
  return ALPHA3.encode.encodeData(decoder, shellcode,
     ALPHA3.encode.bx_IMUL_30_XOR_by, # Use this encoding function
     ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])  # And these characters to encode

encoders = [{
    "base address": "^(RAX|RCX|RDX|RBX|RSP|RBP|RSI|RDI)$",
    "base address samples": ["RAX", "RCX", "RDX", "RBX", "RSP", "RBP", "RSI", "RDI"],
    "name": r"AscMix (r64)",
    "function": encodeShellcode,
    "tests": {
      "rax": ["[$]=ascii:con", "rax=$", "rip=$"],
      "rcx": ["[$]=ascii:con", "rcx=$", "rip=$"],
      "rdx": ["[$]=ascii:con", "rdx=$", "rip=$"],
      "rbx": ["[$]=ascii:con", "rbx=$", "rip=$"],
      "rsp": ["[$+800]=ascii:con", "rsp=$+800", "rip=$+800"], # leave some room for stack
      "rbp": ["[$]=ascii:con", "rbp=$", "rip=$"],
      "rsi": ["[$]=ascii:con", "rsi=$", "rip=$"],
      "rdi": ["[$]=ascii:con", "rdi=$", "rip=$"]
    }
}]

