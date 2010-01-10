import ALPHA3

LOCAL_PATH = __path__[0]

def encodeShellcode(seh_getpc, shellcode):
  call_getpc = ALPHA3.io.ReadFile("ECX+2.bin", LOCAL_PATH)
  return call_getpc + ALPHA3.x86.ascii.mixedcase.rm32.encodeShellcode("ECX+2", shellcode)

encoders = [{
    "base address": "^(call)$",
    "base address samples": ["call"],
    "name": r"Latin1Mix CALL GetPC",
    "function": encodeShellcode,
    "tests": {
      "call": ["[$]=ascii:%shellcode%", "eip=$"]
    }
}]
