import ALPHA3

LOCAL_PATH = __path__[0]

def encodeShellcode(base_address, shellcode):
  unicode_decoder = ALPHA3.io.ReadFile("%s.bin" % base_address.upper(), LOCAL_PATH)
  assert len(unicode_decoder) % 2 == 0, "Unicode decoder stub is not an even number of bytes"
  ascii_decoder = ""
  for i in range(0, len(unicode_decoder), 2):
    assert ord(unicode_decoder[i + 1]) == 0, "Unicode decoder stub char %d is not \\u00XX: \\u%02X%02X" % (
        i, ord(unicode_decoder[i + 1]), ord(unicode_decoder[i]))
    ascii_decoder += unicode_decoder[i]
  return ALPHA3.encode.encodeData(ascii_decoder, shellcode,
     ALPHA3.encode.bx_IMUL_10_ADD_by, # Use this encoding function
     ALPHA3.charsets.valid_charcodes["ascii"]["uppercase"],  # And these characters to encode
     pre_xor=False, terminating_char="A") # No pre-xoring, "A" character terminates encoding.

encoders = [{
    "base address": "^(EAX|ECX|EDX|EBX|ESP|EBP|ESI|EDI|" +
          r"\[EAX\]|\[ECX\]|\[EDX\]|\[EBX\]|\[ESP\]|\[EBP\]|\[ESI\]|\[EDI\])$",
    "base address samples": ["EAX", "ECX", "EDX", "EBX", "ESP", "EBP", "ESI", 
          "EDI", "[EAX]", "[ECX]", "[EDX]", "[EBX]", "[ESP]", "[EBP]", "[ESI]", 
          "[EDI]"],
    "name": r"UniUpper 0x10 (rm32)",
    "function": encodeShellcode,
    "tests": {
      "eax": ["[$]=unicode:con", "eax=$", "eip=$"],
      "ecx": ["[$]=unicode:con", "ecx=$", "eip=$"],
      "edx": ["[$]=unicode:con", "edx=$", "eip=$"],
      "ebx": ["[$]=unicode:con", "ebx=$", "eip=$"],
#      "esp": ["[$+800]=unicode:con", "esp=$+800", "eip=$+800"], # leave some room for stack
      "ebp": ["[$]=unicode:con", "ebp=$", "eip=$"],
      "esi": ["[$]=unicode:con", "esi=$", "eip=$"],
      "edi": ["[$]=unicode:con", "edi=$", "eip=$"],
#      "[eax]": ["[$]=value:$+4", "[$+4]=unicode:con", "eax=$", "eip=$+4"],
#      "[ecx]": ["[$]=value:$+4", "[$+4]=unicode:con", "ecx=$", "eip=$+4"],
#      "[edx]": ["[$]=value:$+4", "[$+4]=unicode:con", "edx=$", "eip=$+4"],
#      "[ebx]": ["[$]=value:$+4", "[$+4]=unicode:con", "ebx=$", "eip=$+4"],
#      "[esp]": ["[$+800]=value:$+804", "[$+804]=unicode:con", "esp=$+800", "eip=$+804"], # leave some room for stack
#      "[ebp]": ["[$]=value:$+4", "[$+4]=unicode:con", "ebp=$", "eip=$+4"],
#      "[esi]": ["[$]=value:$+4", "[$+4]=unicode:con", "esi=$", "eip=$+4"],
#      "[edi]": ["[$]=value:$+4", "[$+4]=unicode:con", "edi=$", "eip=$+4"]
    }
}]

