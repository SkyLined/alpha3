import ALPHA3
import math

# A generic encoding routine used by various decoders:
def encodeData(decoder, data, encoding_function, valid_values, pre_xor=True, terminating_char=""):
  assert decoder, "Decoder is missing or empty"
  assert data.find("\0") == -1, "Shellcode must be NULL free"
  # Older encoders use a terminating char:
  if terminating_char != "":
    terminating_value = ord(terminating_char)
    if terminating_value in valid_values:
      valid_values.remove(terminating_value)
  data += "\0" # A NULL will mark the end of the shellcode.
  # The shellcode is encoded after the decoder. But because the last byte of the
  # decoder is the negative offset of a jump that restarts the decoder loop and
  # negative offsets translate into non-alphanumeric chars, this byte is also
  # encoded (and will be the first to be decoded, so the jump will be decoded
  # when the codepath hits it). All this means that the last two bytes of the
  # decoder are part of the encoded data:
  encoded_data = decoder[-2:]
  decoder = decoder[:-2]
  destination_index = 1
  for c in data:
    data_byte = ord(c);
    # pre-xor A with B and encode the result into two bytes:
    status = "encoding data (%d%%)" % int(100 * destination_index / len(data))
    if pre_xor:
      # The decoder stores decoded data using the XOR instruction. Originally, the
      # decoder would pre-xor each data byte (A) with the value of the byte where it
      # should be stored (B) before storing the byte. This meant that A would become
      # A ^ B before the decoder stores it B ^= A ^ B (== A). However, this can be
      # done while encoding, as well, saving a few bytes in the decoder:
      pre_xor_byte = ord(encoded_data[destination_index])
      bx, by = encoding_function(data_byte ^ pre_xor_byte, status, valid_values)
    else:
      bx, by = encoding_function(data_byte, status, valid_values)
    encoded_data += chr(bx) + chr(by)
    destination_index += 1
  return decoder + encoded_data + terminating_char

# An encoding using in x86 ascii mixedcase decoders
def bx_IMUL_30_XOR_by(value, status, valid_values): 
  for bx in valid_values:
    bx_IMUL_30 = (bx * 0x30) & 0xFF
    for by in valid_values:
      bx_IMUL_30_XOR_by = bx_IMUL_30 ^ by
      if bx_IMUL_30_XOR_by == value:
        ALPHA3.PrintVerboseStatus()
        return [bx, by]
      ALPHA3.PrintVerboseStatus(status, "%02X * 30 ^ %02X == %02X" % (
          bx, by, bx_IMUL_30_XOR_by))
  raise AssertionError("Cannot encode %02X" % (value,))

# An encoding used by old x86 unicode decoders:
def bx_IMUL_10_ADD_by(value, status, valid_values):
  for bx in valid_values:
    bx_IMUL_10 = (bx * 0x10) & 0xFF
    for by in valid_values:
      bx_IMUL_10_ADD_by = (bx_IMUL_10 + by) & 0xFF
      if bx_IMUL_10_ADD_by == value:
        ALPHA3.PrintVerboseStatus()
        return [bx, by]
      ALPHA3.PrintVerboseStatus(status, "%02X * 10 + %02X == %02X" % (
          bx, by, bx_IMUL_10_ADD_by))
  raise AssertionError("Cannot encode %02X" % (value,))

def wyx_IMUL_30_SHR_8_XOR_bx(value, status, valid_values):
  for bx in valid_values:
    for by in valid_values:
      wyx = (by << 8) + bx
      wyx_IMUL_30 = (wyx * 0x30) & 0xFFFF
      wyx_IMUL_30_SHR_8 = wyx_IMUL_30 >> 8
      wyx_IMUL_30_SHR_8_XOR_bx = wyx_IMUL_30_SHR_8 ^ bx
      if wyx_IMUL_30_SHR_8_XOR_bx == value:
        ALPHA3.PrintVerboseStatus()
        return [bx, by]
      ALPHA3.PrintVerboseStatus(status, "%02X %02X: ((%04X * 30) >> 8) ^ %02X == %02X" % (
          bx, by, wyx, bx, wyx_IMUL_30_SHR_8_XOR_bx))
  raise AssertionError("Cannot encode %02X" % (value,))

def dwx_IMUL_by(value, status, valid_values):
  for by in valid_values:
    dwx, carry = makeValid(0, 4, valid_values)
    while not carry:
      dwx_IMUL_by = (dwx * by) & 0xFFFFFFFF
      if dwx_IMUL_by == value:
        ALPHA3.PrintVerboseStatus()
        return [dwx, by]
      ALPHA3.PrintVerboseStatus(status, "%08X * %02X == %08X" % (
          dwx, by, dwx_IMUL_by))
      # How far off the desired value is the result now?
      diff = value - dwx_IMUL_by
      if diff < 0:
        # the result is too small:
        if diff % by == 0:
          # It is a whole number of times by smaller: increase dwxX to get
          # the right result:
          dwx -= int(diff / by)
        else:
          # It is a off by an ammount that cannot lead to the solution easily.
          # Cause another integer overflow to try another solution:
          dwx += int(math.floor((diff + 0x100000000) / by))
      else:
        # It is too large, cause an integer overflow to resolve that:
        dwx += int(math.floor((0x100000000 - diff) / by))
      # Whatever modifications have been made to dwx may have caused it to
      # become non-alphanumeric. If so, find the smallest alphanumeric number 
      # that is larger than dwx and use that:
      dwx, carry = makeValid(int(dwx), 4, valid_values)

def dwx_IMUL_30_XOR_dwy(value, status, valid_values):
  dwx, carry = makeValid(0, 4, valid_values)
  dwy, carry = makeValid(0, 4, valid_values)
  for byte in range(0, 4):
    byte_mask = 0xFF << (byte * 8)
    while 1:
      dwx_IMUL_30_XOR_dwy = ((dwx * 0x30) ^ dwy) & 0xFFFFFFFF
      ALPHA3.PrintVerboseStatus(status, "%08X * 30 ^ %08X == %08X" % (
          dwx, dwy, dwx_IMUL_30_XOR_dwy))
      if (dwx_IMUL_30_XOR_dwy & byte_mask) == (value & byte_mask):
        break # OK: next byte
      x_byte = (dwx & byte_mask) >> (byte * 8)
      next_x_byte, carry = makeValid(x_byte + 1, 1, valid_values)
      dwx = (dwx & (0xFFFFFFFF ^ byte_mask)) ^ (next_x_byte << (byte * 8))
      if carry:
        y_byte = (dwy & byte_mask) >> (byte * 8)
        next_y_byte, carry = makeValid(y_byte + 1, 1, valid_values)
        dwy = (dwy & (0xFFFFFFFF ^ byte_mask)) ^ (next_y_byte << (byte * 8))
        assert carry == 0, "Cannot encode value!" # Should never happen!
  ALPHA3.PrintVerboseStatus()
  return [dwx, dwy]

def isValid(value, bytes, valid_values):
  for i in range(0, bytes):
    byte = (value >> (i * 8)) & 0xFF
    if byte not in valid_values:
      return False
  return True

def makeValid(value, bytes, valid_values):
  carry = 0
  result = 0
  for i in range(0, bytes):
    byte = ((value >> (i * 8)) & 0xFF) + carry
    carry = 0
    if byte not in valid_values:
      for valid_byte in valid_values:
        if valid_byte > byte:
          byte = valid_byte
          break
      else:
        byte = 0x30
        carry = 1
    result += byte << (i * 8)
  if (value >> (bytes * 8)) > 0:
    carry = 1
  return result, carry

def toString(value, bytes):
  s = ""
  for i in range(0, bytes):
    byte = (value >> (i * 8)) & 0xFF
    s += chr(byte)
  return s

def injectCodes(data, codes):
  for code in codes:
    start_code = data.find("@")
    assert start_code != -1, "More codes than places to store them!"
    end_code = start_code + 1
    while data[end_code] == "@":
      end_code += 1
    encoded_code = toString(code, end_code - start_code)
    data = data[:start_code] + encoded_code + data[end_code:]
  assert data.find("@") == -1, "Not enough codes to satisfy decoder!"
  return data
