import ALPHA3

LOCAL_PATH = __path__[0]

def encodeShellcode(seh_getpc, shellcode):
  seh_getpc = ALPHA3.io.ReadFile("ESI+4.bin", LOCAL_PATH)
  return seh_getpc + ALPHA3.x86.ascii.mixedcase.rm32.encodeShellcode("ESI+4", shellcode);

encoders = [{
    "base address": "^(seh_getpc_xpsp3)$",
    "base address samples": ["seh_getpc_xpsp3"],
    "name": r"AscMix SEH GetPC (XPsp3)",
    "function": encodeShellcode,
    "tests": {
      "seh_getpc_xpsp3": ["[$]=ascii:%shellcode%", "eip=$"]
    }
}]
