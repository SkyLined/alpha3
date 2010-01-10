import os, sys

# Add root ALPHA3 node to the module search path:
def parent_path(path, parents):
  while parents > 0:
    parents -= 1
    path = os.path.split(path)[0]
  return path
sys.path.append(parent_path(__file__, 5))
import ALPHA3


def XX_IMUL_30_XOR_YY_XOR_XX(result, valid_values): # Find a way to encode a byte
  for XX in valid_values:
    XX_IMUL_30 = (XX * 0x30) & 0xFF
    for YY in valid_values:
      XX_IMUL_30_XOR_YY_XOR_XX = XX_IMUL_30 ^ YY ^ XX
      if XX_IMUL_30_XOR_YY_XOR_XX == result:
        return XX, YY
  raise AssertionError("Cannot encode %02X" % (result,))

def PrintValues(i):
  XX, YY = XX_IMUL_30_XOR_YY_XOR_XX(i, ALPHA3.ascii.mixedcase.VALUES)
  print "%02X %02X: %02X * 30 ^ %02X ^ %02X == %02X" % (XX, YY, XX, YY, XX, i)

if __name__ == "__main__":
  if len(sys.argv) == 2:
    i = ALPHA3.toInt(sys.argv[1])
    PrintValues(i)
  else:
    for i in range(0xFF):
      PrintValues(i)
  
