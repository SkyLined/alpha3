import ALPHA3
import math, os, sys

LOCAL_PATH = __path__[0]

def encodeShellcode(base_address, shellcode):
  base_address = ALPHA3.toInt(base_address)
  encoded_base_address = ALPHA3.encode.dwx_IMUL_by(base_address, 
      "encoded base address", ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])
  if encoded_base_address is not None:
    decoder = ALPHA3.io.ReadFile("dwx_IMUL_by.bin", LOCAL_PATH)
  else:
    encoded_base_address = ALPHA3.encode.dwx_IMUL_30_XOR_dwy(base_address,
        "encoded base address", ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])
    decoder = ALPHA3.io.ReadFile("dwx_IMUL_30_XOR_dwy.bin", LOCAL_PATH)
  decoder = ALPHA3.encode.injectCodes(decoder, encoded_base_address)
  return ALPHA3.encode.encodeData(decoder, shellcode,
     ALPHA3.encode.bx_IMUL_30_XOR_by, # Use this encoding function
     ALPHA3.charsets.valid_charcodes["ascii"]["mixedcase"])  # And these characters to encode


encoders = [{
    "base address": "^((?:0x)?[0-9A-Fa-f]+)$",
    "base address samples": ["(address)"],
    "name": r"AscMix 0x30 (i32)",
    "function": encodeShellcode,
    "tests": {
      "0x09090900": ["--mem:address=09090900", "[09090900]=ascii:%shellcode%", "eip=09090900"], # dwx_IMUL_by
      "0x0D0D0D0D": ["--mem:address=0D0D0D0D", "[0D0D0D0D]=ascii:%shellcode%", "eip=0D0D0D0D"]  # dwx_IMUL_30_XOR_dwy
    }
}]
