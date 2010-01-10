# -*- coding: latin1 -*-
# http://en.wikipedia.org/wiki/Ascii
# http://en.wikipedia.org/wiki/Code_page_437
# http://en.wikipedia.org/wiki/ISO/IEC_8859-1
valid_character_encodings = ["ascii", "cp437", "latin-1", "utf-16"];
valid_character_casings   = ["lowercase", "mixedcase", "uppercase"];

numeric                   = "0123456789";
uppercase_ascii           = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
lowercase_ascii           = "abcdefghijklmnopqrstuvwxyz";
mixedcase_ascii           = uppercase_ascii + lowercase_ascii;
uppercase_cp437           = "€Ž’š¥âãäèêíî";
lowercase_cp437           = "‚ƒ„…†‡ˆ‰Š‹Œ‘“”•–—˜Ÿ ¡¢£¤àáåæçéë";
mixedcase_cp437           = uppercase_cp437 + lowercase_cp437;
uppercase_latin_1         = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ";
lowercase_latin_1         = "ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ";
mixedcase_latin_1         = uppercase_latin_1 + lowercase_latin_1;

valid_chars = {
  "ascii": {
    "lowercase": numeric + lowercase_ascii,
    "mixedcase": numeric + mixedcase_ascii,
    "uppercase": numeric + uppercase_ascii
  },
  "cp437": {
    "lowercase": numeric + lowercase_ascii + lowercase_cp437,
    "mixedcase": numeric + mixedcase_ascii + mixedcase_cp437,
    "uppercase": numeric + uppercase_ascii + uppercase_cp437
  },
  "latin-1": {
    "lowercase": numeric + lowercase_ascii + lowercase_latin_1,
    "mixedcase": numeric + mixedcase_ascii + mixedcase_latin_1,
    "uppercase": numeric + uppercase_ascii + uppercase_latin_1
  },
  "utf-16": {
    "lowercase": numeric + lowercase_ascii + lowercase_latin_1,
    "mixedcase": numeric + mixedcase_ascii + mixedcase_latin_1,
    "uppercase": numeric + uppercase_ascii + uppercase_latin_1
  },
}

# Automatically generate a similar table with arrays of integer character codes:
valid_charcodes = {}
for char_encoding in valid_chars:
  valid_charcodes[char_encoding] = {}
  for case, chars in valid_chars[char_encoding].items():
    valid_charcodes[char_encoding][case] = []
    for char in chars:
      valid_charcodes[char_encoding][case] += [ord(char)]


charcode_fmtstr = {
  "ascii":    "%02X",
  "cp437":    "%02X",
  "latin-1":  "%02X",
  "utf-16":   "%04X"
}

