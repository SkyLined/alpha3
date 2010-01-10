import getpc

encoders = getpc.encoders
for encoder in encoders:
  encoder["case"] = "mixedcase"
