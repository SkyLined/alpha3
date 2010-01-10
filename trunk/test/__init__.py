import ALPHA3
import os, re, subprocess, sys

LOCAL_PATH = __path__[0]

if (sys.platform == 'win32'):
  TEST_X86 = ALPHA3.io.LongPath(os.path.join(LOCAL_PATH, "w32-testival.exe"))
  if not os.path.isfile(TEST_X86):
    raise IOError("Test application not found: \"%s\"." % TEST_X86)
  TEST_X86_SHELLCODE_FILE = ALPHA3.io.LongPath(os.path.join(LOCAL_PATH, "w32-writeconsole-shellcode.bin"))
  if not os.path.isfile(TEST_X86_SHELLCODE_FILE):
    raise IOError("Test shellcode not found: \"%s\"." % TEST_X86_SHELLCODE_FILE)
  TEST_X86_SHELLCODE = ALPHA3.io.ReadFile(TEST_X86_SHELLCODE_FILE);

  TEST_X64 = ALPHA3.io.LongPath(os.path.join(LOCAL_PATH, "w64-testival.exe"))
  if not os.path.isfile(TEST_X64):
    raise IOError("Test application not found: \"%s\"." % TEST_X64)
  TEST_X64_SHELLCODE_FILE = ALPHA3.io.LongPath(os.path.join(LOCAL_PATH, "w64-writeconsole-shellcode.bin"))
  if not os.path.isfile(TEST_X64_SHELLCODE_FILE):
    raise IOError("Test shellcode not found: \"%s\"." % TEST_X64_SHELLCODE_FILE)
  TEST_X64_SHELLCODE = ALPHA3.io.ReadFile(TEST_X64_SHELLCODE_FILE);
  
  TEST_SHELLCODE_OUTPUT = "Hello, world!\r\n"
else:
  raise OSError("Unsupported platform for testing.");

def TestEncoder(encoder_settings, base_address, int3):
  assert "tests" in encoder_settings and encoder_settings["tests"], (
      "No tests found in [%s] encoder." % (encoder_settings["name"]))
  problems = []
  test_count = 0
  error_count = 0
  for test_base_address, test_args in encoder_settings["tests"].items():
    if base_address is None or test_base_address.lower() == base_address.lower():
      if test_count == 0:
        ALPHA3.PrintVerboseSeparator()
        base_address_test_found = True
      else:
        ALPHA3.PrintVerboseLine()
      if ALPHA3.g_output_verbosity_level == 0:
        ALPHA3.PrintStatus("[%s]" % encoder_settings["name"], "Test %d" % test_count)
      ALPHA3.PrintVerboseCenteredLine("Testing encoder [%s] with base address \"%s\"" % (
          encoder_settings["name"], test_base_address))
      # Run test
      test_count += 1
      test_errors = RunEncoderTest(encoder_settings, test_base_address, test_args, int3)
      if test_errors:
        error_count += 1
        problems += test_errors
  if test_count == 0:
    if base_address is None: # No filter, there are no tests!
      problems += ["Encoder [%s] has no tests." % encoder_settings["name"]]
  else:
    ALPHA3.PrintVerboseLine()
    # Create a result message:
    if error_count:
      passed_tests_message = "%d/%d tests." % (test_count - error_count, test_count)
    else:
      passed_tests_message = "all %d tests." % (test_count)
    if ALPHA3.g_output_verbosity_level == 0:
      ALPHA3.PrintStatusLine("[%s]" % encoder_settings["name"], "Passed %s" % passed_tests_message)
    else:
      ALPHA3.PrintVerboseCenteredLine("Encoder [%s] passed %s" % (
          encoder_settings["name"], passed_tests_message))
  return problems

def RunEncoderTest(encoder_settings, base_address, test_args, int3):
  for i in range(len(test_args)):
    test_args[i] = test_args[i].replace("%shellcode%", "con")
  if (encoder_settings["architecture"] == "x86"):
    shellcode_file = TEST_X86_SHELLCODE_FILE
    shellcode = TEST_X86_SHELLCODE
    test_command = TEST_X86
  elif (encoder_settings["architecture"] == "x64"):
    shellcode_file = TEST_X64_SHELLCODE_FILE
    shellcode = TEST_X64_SHELLCODE
    test_command = TEST_X64
  else:
    ALPHA3.PrintVerboseStatusLine("Problem", "Encoder uses untestable architecture.")
    return ["[%s] Has an untestable architecture \"%s\"" % (encoder_settings["name"], architecture)]
  # Encode shellcode
  if "function args" in encoder_settings:
    encoder_function_args = encoder_settings["function args"];
  else:
    encoder_function_args = {};
  encoded_shellcode = encoder_settings["function"](base_address, shellcode, *encoder_function_args)
  encoding_errors = CheckEncodedShellcode(encoded_shellcode, encoder_settings)
  if encoding_errors:
    ALPHA3.PrintVerboseStatusLine("Problem", "Encoder failed to encode correctly.")
    return ["[%s] created encoded shellcode with bad characters for base address \"%s\":" % (
        encoder_settings["name"], base_address)] + encoding_errors
  # Create test command line:
  if int3 and "--int3" not in test_args:
    test_args += ["--int3"]
  test_args += ["--EH"]
  command = "\"%s\" %s" % (test_command, " ".join(test_args))
  # Output encoder and test command lines:
  ALPHA3.PrintVerboseStatusLine("Encode command", "ALPHA3.py %s %s %s %s --input=\"%s\"" % (
      encoder_settings["architecture"], encoder_settings["character encoding"], encoder_settings["case"], 
      base_address, ALPHA3.io.ShortPath(shellcode_file)))
  ALPHA3.PrintVerboseStatusLine("Test command", "\"%s\" %s" % (
      ALPHA3.io.ShortPath(test_command), " ".join(test_args)))
  # Print test command line:
  try:
    popen = subprocess.Popen(command, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  except WindowsError, e:
    if e.winerror == 193: # not a valid Win32 application
      ALPHA3.PrintVerboseStatusLine("Problem", "Encoder cannot be tested on your platform (ignored).")
      return None
    raise
  stdout_data, stderr_data = popen.communicate(encoded_shellcode)
  if (stdout_data == TEST_SHELLCODE_OUTPUT and stderr_data == ""):
    ALPHA3.PrintVerboseStatusLine("Result", "Success")
    return None
  ALPHA3.PrintVerboseStatusLine("Result", "Failed")
  return ["[%s] failed test for base address \"%s\"" % (encoder_settings["name"], base_address),
      "  stdout: %s" % repr(stdout_data),
      "  stderr: %s" % repr(stderr_data)]

def CheckEncodedShellcode(encoded_shellcode, encoder_settings):
  valid_chars = ALPHA3.charsets.valid_chars[encoder_settings["character encoding"]][encoder_settings["case"]]
  errors = []
  index = 0
  for char in encoded_shellcode:
    if char not in valid_chars:
      charcode_str = ALPHA3.charsets.charcode_fmtstr[encoder_settings["character encoding"]] % ord(char)
      errors += ["  Byte %d @0x%02X: %s (%s)" % (index, index, char, charcode_str)]
    index += 1
  return errors