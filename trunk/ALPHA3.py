# Copyright (c) 2003-2010, Berend-Jan "SkyLined" Wever <berendjanwever@gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of the
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import charsets, encode, io
import x86, x64, test
import os, re, sys

#_______________________________________________________________________________________________________________________
#                                                                                                                       
#                     ,sSSs,,s,  ,sSSSs,   : ALPHA3 - Alphanumeric shellcode encoder.                                   
#                    dS"  Y$P"  YS"  ,SY   : Version 1.0 alpha                                                          
#                   iS'   dY       ssS"    : Copyright (C) 2003-2009 by SkyLined.                                       
#                   YS,  dSb   SP,  ;SP    : <berendjanwever@gmail.com>                                                 
#                   `"YSS'"S'  "YSSSY"     : http://skypher.com/wiki/index.php/ALPHA3                                   
#_______________________________________________________________________________________________________________________
#                                                                                                                       

_settings = {
  "architecture": None,
  "character encoding": None,
  "case": None
}
_default_settings = {
  "architecture": "x86",
  "character encoding": "ascii",
  "case": "mixedcase"
}
_valid_settings = {
  "case": charsets.valid_character_casings,
  "character encoding": charsets.valid_character_encodings,
  "architecture": ["x86", "x64"]
}
_arguments = {
  "base address": None
}
_switches = {
  "input": None,
  "output": None
}
_flags = {
  "verbose": 0,
  "help": 0,
  "test": 0,
  "int3": 0
}

encoders = [];

import print_functions;
from print_functions import *

def ParseCommandLine():
  global _settings, _arguments, _switches, _flags;
  # Parse settings, arguments, switches and flags from the command line:
  if len(sys.argv) == 1:
    _flags["help"] = 1;
  else:
    for i in range(1, len(sys.argv)):
      arg = sys.argv[i];
      if arg[:2] == "--":
        end_switch_name = arg.find("=");
        if end_switch_name != -1:
          switch_name = arg[2:end_switch_name];
          switch_value = arg[end_switch_name + 1:];
          for valid_switch_name in _switches:
            if switch_name == valid_switch_name:
              _switches[switch_name] = switch_value;
              break;
          else:
            print >>sys.stderr, "Unknown switch '%s'!" % arg[2:];
            return False;
        else:
          flag_name = arg[2:]
          for valid_flag_name in _flags:
            if flag_name == valid_flag_name:
              _flags[flag_name] += 1;
              break
          else:
            print >>sys.stderr, "Unknown flag '%s'!" % valid_flag_name;
            return False;
      else:
        for setting_name in _valid_settings:
          if arg in _valid_settings[setting_name]:
            _settings[setting_name] = arg;
            break;
        else:
          for argument_name in _arguments:
            if _arguments[argument_name] == None:
              _arguments[argument_name] = arg;
              break;
          else:
            print >>sys.stderr, "Unknown _arguments: %s." % repr(arg);
            return False;
  return True;

def PrintLogo():
  PrintInfo([
    (None, "____________________________________________________________________________"),
    (None, """      ,sSSs,,s,  ,sSSSs,    ALPHA3 - Alphanumeric shellcode encoder."""),
    (None, """     dS"  Y$P"  YS"  ,SY    """),
    (None, """    iS'   dY       ssS"     Copyright (C) 2003-2009 by SkyLined."""),
    (None, """    YS,  dSb   SP,  ;SP     <berendjanwever@gmail.com>"""),
    (None, """    `"YSS'"S'  "YSSSY"      http://skypher.com/wiki/index.php/ALPHA3"""),
    (None, "____________________________________________________________________________"),
  ]);

def PrintHelp():
  PrintInfo([
    (None, "[Usage]"),
    ("  ", "ALPHA3.py  [ encoder settings | I/O settings | flags ]"),
    (None, ""),
    (None, "[Encoder setting]"),
    ("  architecture ",     "Which processor architecture to target (x86, x64)."),
    ("  character encoding ", "Which character encoding to use (ascii, cp437, latin-1, utf-16)."),
    ("  casing ",           "Which character casing to use (uppercase, mixedcase, lowercase)."),
    ("  base address ",     "How to determine the base address in the decoder code (each encoder has its own set of "
                            "valid values)."),
    (None, ""),
    (None, "[I/O Setting]"),
    ("  --input=\"file\"",  "Path to a file that contains the shellcode to be encoded (Optional, default is to read "
                            "input from stdin)."),
    ("  --output=\"file\"", "Path to a file that will receive the encoded shellcode (Optional, default is to write "
                            "output to stdout)."),
    (None, ""),
    (None, "[Flags]"),
    ("  --verbose",         "Display verbose information while executing. Use this flag twice to output progress "
                            "during encoding."),
    ("  --help",            "Display this message and quit."),
    ("  --test",            "Run all available tests for all encoders. (Useful while developing/testing new "
                            "encoders)."),
    ("  --int3",            "Trigger a breakpoint before executing the result of a test. (Use in combination with "
                            "--test)."),
    (None, ""),
    (None, "[Notes]"),
    ("  ", "You can provide encoder settings in combination with the --help and --test switches to filter which "
           "encoders you get help information for and which get tested, respectively.")
  ]);

def Main():
  # Print header
  if _flags["help"]:
    # Print the main help body before displaying encoder specific help:
    PrintLogo();
    PrintWrappedLine();
    PrintHelp();
    PrintWrappedLine();
    encoding = False;
  elif not _flags["test"]:
    if _flags["verbose"]:
      PrintLogo();
    encoding = True;
  else:
    if _flags["verbose"]:
      PrintLogo();
      PrintWrappedLine();
    # We're testing our encoders
    encoding = False;
  # Print the _settings provided by the user and if we're encoding shellcode, set and print the default _settings
  # for anything not provided:
  if _flags["verbose"]:
    for name in _settings:
      if _settings[name] is not None:
        PrintInfo([(name, _settings[name])]);
      elif encoding:
        _settings[name] = _default_settings[name];
        PrintInfo([(name, _settings[name] + " (default)")]);
    for name in _arguments:
      if _arguments[name] is not None:
        PrintInfo([(name, _arguments[name])]);
  # If the user wants to encode shellcode, it needs to be read from stdin or a file:
  if encoding:
    if _switches["input"] is not None:
      shellcode = io.ReadFile(_switches["input"]);
    else:
      shellcode = sys.stdin.read();
  # Scan all encoders to see which match the given _settings/_arguments and take action:
  results = [];
  errors = False;
  help_results = {};
  at_least_one_encoder_found = False;
  for encoder_settings in encoders:
    for name in _settings:
      if not name in encoder_settings:
        raise AssertionError("One of the encoders is missing the '%s' setting: %s" % (name, encoder_settings["name"]));
      if _settings[name] != None and _settings[name] != encoder_settings[name]:
        # This _settings is specified but does not match this encoders _settings: skip the encoder.
        break;
    else: # All _settings match
      # Check "base address" argument:
      if (_arguments["base address"] is None or 
          re.match(encoder_settings["base address"], _arguments["base address"], re.IGNORECASE)):
        at_least_one_encoder_found = True;
        if _flags["test"]:
          problems = test.TestEncoder(encoder_settings, _arguments["base address"], _flags["int3"] > 0);
          if problems is not None: # None => No test was found for the given base address
            at_least_one_encoder_found = True;
            results.extend(problems);
            errors = True;
        elif _flags["help"]:
          encoder_settings_string = "%s %s %s" % (encoder_settings["architecture"], 
              encoder_settings["character encoding"], encoder_settings["case"]);
          if encoder_settings_string not in help_results:
            help_results[encoder_settings_string] = [];
          help_results[encoder_settings_string].append((
              encoder_settings["name"], " ".join(encoder_settings["base address samples"])));
        else:
          encoder_function = encoder_settings["function"];
          if "function args" in encoder_settings:
            encoder_function_args = encoder_settings["function args"];
          else:
            encoder_function_args = {};
          if _switches["output"] is not None:
            io.WriteFile(_settings["output file"], result);
          else:
            encoded_shellcode = encoder_function(_arguments["base address"], shellcode, *encoder_function_args);
            results += test.CheckEncodedShellcode(encoded_shellcode, encoder_settings);
            sys.stdout.write(encoded_shellcode);
  if _flags["help"]:
    if not help_results:
      PrintWrappedLine("No encoder found that can encode using the given settings and arguments.");
      errors = True;
    else:
      PrintWrappedLine("Valid base address examples for each encoder, ordered by encoder settings, are:");
      help_results_encoder_settings = help_results.keys();
      help_results_encoder_settings.sort();
      for encoder_settings_string in help_results_encoder_settings:
        PrintWrappedLine("");
        PrintWrappedLine("[%s]" % encoder_settings_string);
        for encoder_name, valid_base_address_samples in help_results[encoder_settings_string]:
          PrintInfo([('  ' + encoder_name, valid_base_address_samples)]);
  else:
    if not at_least_one_encoder_found:
      results.append("No encoder exists for the given settings.");
      errors = True;
    if results:
      PrintWrappedLine("");
      PrintWrappedLine("The following problems were found:");
      for result in results:
        PrintWrappedLine(result);
  return not errors;

def toInt(s):
  if s[:2] == "0x":
    return int(s[2:], 16);
  return int(s);

if __name__ == "__main__":
  encoders.extend(x86.encoders);
  encoders.extend(x64.encoders);
  success = ParseCommandLine();
  if success:
    print_functions.g_output_verbosity_level = _flags["verbose"];
    success = Main();
  exit_code = {True:0, False:1}[success];
  exit(exit_code);
