import mixedcase

encoders = mixedcase.encoders
for encoder in encoders:
  encoder["character encoding"] = "ascii"
