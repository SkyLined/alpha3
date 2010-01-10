import mixedcase, uppercase

encoders = mixedcase.encoders + uppercase.encoders
for encoder in encoders:
  encoder["character encoding"] = "utf-16"
