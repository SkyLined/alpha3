# -*- coding: latin1 -*-
# http://en.wikipedia.org/wiki/Ascii
# http://en.wikipedia.org/wiki/Code_page_437
# http://en.wikipedia.org/wiki/ISO/IEC_8859-1
valid_character_encodings = ["ascii", "cp437", "latin-1", "utf-16"];
valid_character_casings   = ["lowercase", "mixedcase", "uppercase"];

numbers                 = "0123456789";
symbols                 = " !\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~";
symbols_cp437           = "›œž¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßìïðñòóôõö÷øùúûüýþÿ";
symbols_latin_1         = " ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿×÷";
uppercase_alpha         = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
uppercase_alpha_cp437   = "€Ž’š¥âãäèêíî";
uppercase_alpha_latin_1 = "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ";
lowercase_alpha         = "abcdefghijklmnopqrstuvwxyz";
lowercase_alpha_cp437   = "‚ƒ„…†‡ˆ‰Š‹Œ‘“”•–—˜Ÿ ¡¢£¤àáåæçéë";
lowercase_alpha_latin_1 = "ßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ";
uppercase               = numbers + uppercase_alpha;
uppercase_cp437         = uppercase + uppercase_alpha_cp437;
uppercase_latin_1       = uppercase + uppercase_alpha_latin_1;
lowercase               = numbers + lowercase_alpha;
lowercase_cp437         = lowercase + lowercase_alpha_cp437;
lowercase_latin_1       = lowercase + lowercase_alpha_latin_1;
mixedcase               = numbers + uppercase_alpha + lowercase_alpha;
mixedcase_cp437         = mixedcase + uppercase_alpha_cp437 + lowercase_alpha_cp437;
mixedcase_latin_1       = mixedcase + uppercase_alpha_latin_1 + lowercase_alpha_latin_1;
printable               = mixedcase + symbols;
printable_cp437         = mixedcase_cp437 + symbols + symbols_cp437;
printable_latin_1       = mixedcase_latin_1 + symbols + symbols_latin_1;

valid_chars = {
  "ascii": {
    "lowercase": lowercase,
    "mixedcase": mixedcase,
    "uppercase": uppercase,
  },
  "cp437": {
    "lowercase": lowercase_cp437,
    "mixedcase": mixedcase_cp437,
    "uppercase": uppercase_cp437,
  },
  "latin-1": {
    "lowercase": lowercase_latin_1,
    "mixedcase": mixedcase_latin_1,
    "uppercase": uppercase_latin_1,
  },
  "utf-16": {
    "lowercase": lowercase,
    "mixedcase": mixedcase,
    "uppercase": uppercase,
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

