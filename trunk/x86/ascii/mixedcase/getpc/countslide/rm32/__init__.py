import ALPHA3
import random, re

LOCAL_PATH = __path__[0]

NOP = {
  'eax': chr(0x43), # nop: 43 = INC EBX
  'ebx': chr(0x42), # nop: 42 = INC EDX
  'ecx': chr(0x43), # nop: 43 = INC EBX
  'edx': chr(0x43), # nop: 43 = INC EBX
  'esi': chr(0x43), # nop: 43 = INC EBX
  'edi': chr(0x43), # nop: 43 = INC EBX
};
COUNT = chr(0x42) # 42 = INC EDX
REG = r"^countslide:(?P<R>%s)\+(?P<I>(?:0x)?[0-9A-Fa-f]+)~(?P<V>(?:0x)?[0-9A-Fa-f]+)$"

def encodeShellcode(base_address, shellcode):
  base_address_parsed = re.match(REG % '|'.join(NOP.keys()), base_address, re.IGNORECASE)
  if base_address_parsed is None:
    raise Exception("Cannot parse \"%s\"." % base_address)

  base_address_register = base_address_parsed.group("R")
  nop = NOP[base_address_register.lower()];
  base_address_offset = ALPHA3.toInt(base_address_parsed.group("I"))
  nopslide_size = ALPHA3.toInt(base_address_parsed.group("V"))

  patcher = ALPHA3.io.ReadFile("[%s+i32] - EDX.bin" % base_address_register, LOCAL_PATH)
  patch_offset = nopslide_size + len(patcher)

  ALPHA3.PrintVerboseStatusLine("Return address",   "%s+%X"    % (base_address_register, base_address_offset))
  ALPHA3.PrintVerboseStatusLine("Nopslide size",    "%X"       % (nopslide_size,))
  ALPHA3.PrintVerboseStatusLine("Patcher size",     "%X"       % (len(patcher),))
  ALPHA3.PrintVerboseStatusLine("Countslide size",  "%X"       % (nopslide_size,))
  ALPHA3.PrintVerboseStatusLine("Patch address",    "%s+%X+%X" % (base_address_register, base_address_offset, patch_offset))

  base_address_offset_encoded = ALPHA3.encode.dwx_IMUL_30_XOR_dwy(
      base_address_offset, "encoded base address offset", 
     ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])
  patch_offset_encoded = ALPHA3.encode.dwx_IMUL_30_XOR_dwy(
      patch_offset, "encoded patch offset",ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])
  patcher = ALPHA3.encode.injectCodes(patcher, base_address_offset_encoded +
      patch_offset_encoded)
  countslide = (nop * nopslide_size + patcher + COUNT * nopslide_size)
  return countslide + ALPHA3.x86.ascii.mixedcase.rm32.encodeShellcode("edx", shellcode);

tests = {};
for reg in NOP.keys():
  # Shellcode can start anywhere in the first 0x100 bytes of the heap block:
  shellcode_start_offset = random.randrange(4,0x104)
  # Code execution can start anywhere in bytes 0x100-0x200 of the heap block:
  code_execution_start_offset = random.randrange(0x104,0x204)
  # register points 0-0x100 bytes before the start of our memory
  for offset in [0, 0x80, 0x100]:
    tests["countslide:%s+0x%X~0x200" % (reg, offset)] = [
        "[$+%X]=ascii:%%shellcode%%" % shellcode_start_offset, 
        "eip=$+%X" % code_execution_start_offset, 
        "[$]=value:$+%X" % code_execution_start_offset,
        "%s=$-%X" % (reg, offset) # [reg+X] = [$] = code_execution_start_offset
    ];
encoders = [{
  "base address": REG,
  "base address samples": [
    "countslide:EAX+offset~uncertainty",
    "countslide:EBX+offset~uncertainty",
    "countslide:ECX+offset~uncertainty",
    "countslide:EDX+offset~uncertainty",
    "countslide:ESI+offset~uncertainty",
    "countslide:EDI+offset~uncertainty",
  ],
  "name": r"AscMix Countslide (rm32)",
  "function": encodeShellcode,
  "tests": tests,
}]
