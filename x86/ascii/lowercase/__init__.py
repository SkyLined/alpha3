import rm32;

encoders = rm32.encoders;
#encoders.extend(ascii_art.encoders)
for encoder in encoders:
  encoder["case"] = "lowercase"
