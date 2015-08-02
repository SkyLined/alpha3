
```
#_______________________________________________________________________________________________________________________
#                                                                                                                       
#                     ,sSSs,,s,  ,sSSSs,   : ALPHA3 - Alphanumeric shellcode encoder.                                   
#                    dS"  Y$P"  YS"  ,SY   :                                                                            
#                   iS'   dY       ssS"    : Copyright (C) 2003-2010 by SkyLined.                                       
#                   YS,  dSb   SP,  ;SP    : <berendjanwever@gmail.com>                                                 
#                   `"YSS'"S'  "YSSSY"     : http://skypher.com/wiki/index.php/ALPHA3                                   
#_______________________________________________________________________________________________________________________
#                                                                                                                       
```
ALPHA3 is a tool for transforming any x86 machine code into 100% alphanumeric code with similar functionality. It works by encoding the original code into alphanumeric data and combining this data with a decoder, which is a piece of x86 machine code written specifically to be 100% alphanumeric. When run, the decoder converts the data back to the original code, after which it is executed.

ALPHA3 is an updated and expanded version of [ALPHA2](http://skypher.com/wiki/index.php/Hacking/Shellcode/Alphanumeric/ALPHA2). The improvements over ALPHA2 include new encodings (x86 lowercase ascii and x64 mixedcase ascii) and smaller decoders for various other encodings.

For more information, have a look at [this wiki page](http://skypher.com/wiki/index.php/Hacking/Shellcode/Alphanumeric/ALPHA3).

ALPHA3 uses [SkyBuild](http://code.google.com/p/skybuild/) to generate shellcodes from source.

ALPHA3 uses [Testival](http://code.google.com/p/testival/) to test encoders.

```
[Usage]
  ALPHA3.py  [ encoder settings | I/O settings | flags ]

[Encoder setting]
  architecture              Which processor architecture to target (x86,
                            x64).
  character encoding        Which character encoding to use (ascii, cp437,
                            latin-1, utf-16).
  casing                    Which character casing to use (uppercase,
                            mixedcase, lowercase).
  base address              How to determine the base address in the decoder
                            code (each encoder has its own set of valid
                            values).

[I/O Setting]
  --input="file"            Path to a file that contains the shellcode to be
                            encoded (Optional, default is to read input from
                            stdin).
  --output="file"           Path to a file that will receive the encoded
                            shellcode (Optional, default is to write output
                            to stdout).

[Flags]
  --verbose                 Display verbose information while executing. Use
                            this flag twice to output progress during
                            encoding.
  --help                    Display this message and quit.
  --test                    Run all available tests for all encoders.
                            (Useful while developing/testing new encoders).
  --int3                    Trigger a breakpoint before executing the result
                            of a test. (Use in combination with --test).

[Notes]
  You can provide encoder settings in combination with the --help and --test
  switches to filter which encoders you get help information for and which
  get tested, respectively.

Valid base address examples for each encoder, ordered by encoder settings,
are:

[x64 ascii mixedcase]
  AscMix (r64)              RAX RCX RDX RBX RSP RBP RSI RDI

[x86 ascii lowercase]
  AscLow 0x30 (rm32)        ECX EDX EBX

[x86 ascii mixedcase]
  AscMix 0x30 (rm32)        EAX ECX EDX EBX ESP EBP ESI EDI [EAX] [ECX]
                            [EDX] [EBX] [ESP] [EBP] [ESI] [EDI] [ESP-4]
                            ECX+2 ESI+4 ESI+8
  AscMix 0x30 (i32)         (address)
  AscMix Countslide (rm32)  countslide:EAX+offset~uncertainty
                            countslide:EBX+offset~uncertainty
                            countslide:ECX+offset~uncertainty
                            countslide:EDX+offset~uncertainty
                            countslide:ESI+offset~uncertainty
                            countslide:EDI+offset~uncertainty
  AscMix Countslide (i32)   countslide:address~uncertainty
  AscMix SEH GetPC (XPsp3)  seh_getpc_xpsp3

[x86 ascii uppercase]
  AscUpp 0x30 (rm32)        EAX ECX EDX EBX ESP EBP ESI EDI [EAX] [ECX]
                            [EDX] [EBX] [ESP] [EBP] [ESI] [EDI]

[x86 latin-1 mixedcase]
  Latin1Mix CALL GetPC      call

[x86 utf-16 uppercase]
  UniUpper 0x10 (rm32)      EAX ECX EDX EBX ESP EBP ESI EDI [EAX] [ECX]
                            [EDX] [EBX] [ESP] [EBP] [ESI] [EDI]
```