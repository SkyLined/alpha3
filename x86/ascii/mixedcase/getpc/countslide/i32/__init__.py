import ALPHA3
import random, re

# Which instructions are used for the nopslide and the countslide?
NOP = chr(0x41)   # 41 = INC ECX
COUNT = chr(0x41) # 41 = INC ECX

LOCAL_PATH = __path__[0]
REG = "^countslide:(?P<I>(?:0x)?[0-9A-Fa-f]+)~(?P<V>(?:0x)?[0-9A-Fa-f]+)$"

def encodeShellcode(base_address, shellcode):
  base_address = re.match(REG, base_address, re.IGNORECASE)

  nopslide_size = ALPHA3.toInt(base_address.group("V"))
  base_address = ALPHA3.toInt(base_address.group("I"))

  patcher = ALPHA3.io.ReadFile("[i32] - ECX.bin", LOCAL_PATH)
  patch_address = base_address + nopslide_size + len(patcher)

  ALPHA3.PrintVerboseStatusLine("return address",  "%08X" % base_address)
  ALPHA3.PrintVerboseStatusLine("nopslide size",   "%X"   % nopslide_size)
  ALPHA3.PrintVerboseStatusLine("patcher size",    "%X"   % len(patcher))
  ALPHA3.PrintVerboseStatusLine("countslide size", "%X"   % nopslide_size)
  ALPHA3.PrintVerboseStatusLine("patch address",   "%08X" % patch_address)

  patch_address_encoded = ALPHA3.encode.dwx_IMUL_30_XOR_dwy(patch_address, 
      "encoded patch address",ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])
  patcher = ALPHA3.encode.injectCodes(patcher, patch_address_encoded)
  countslide = (NOP * nopslide_size + patcher + COUNT * nopslide_size)
  return countslide + ALPHA3.x86.ascii.mixedcase.rm32.encodeShellcode("ecx", shellcode);

base_address = 0x0D0D0D0D
# Shellcode can start anywhere in the first 0x100 bytes of the heap block:
shellcode_start_offset = random.randrange(0,0x100)
# Code execution can start anywhere in bytes 0x100-0x200 of the heap block:
code_execution_start_offset = random.randrange(0x100,0x200)
encoders = [{
    "base address": REG,
    "base address samples": ["countslide:address~uncertainty"],
    "name": r"AscMix Countslide (i32)",
    "function": encodeShellcode,
    "tests": {
      "countslide:0x%08X~0x200" % (base_address + code_execution_start_offset): [
          "--mem:address=%08X" % (base_address), 
          "[%08X]=ascii:%%shellcode%%" % (base_address + shellcode_start_offset), 
          "eip=%08X" % (base_address + code_execution_start_offset)
      ]
    }
}]
