import sys, math;

g_output_screen_width = 76;
g_output_header_size = 28;
g_line_wrap_word_length = 20;
g_output_verbosity_level = 0;

# http://en.wikipedia.org/wiki/Newline
if sys.platform in ['win32', 'cygwin', 'os2', 'os2emx']:
  g_newline = "\r\n";
elif sys.platform in ['darwin']:
  g_newline = "\r";
else:
  # Assume *nix:
  g_newline = "\n";

def PrintVerboseStatus(header=None, message=""):
  global g_output_verbosity_level;
  if g_output_verbosity_level > 1:
    PrintStatus(header, message)
def PrintStatus(header=None, message=""):
  global g_output_header_size, g_output_screen_width;
  if header is None:
    Print("".ljust(g_output_screen_width) + "\r");
  status = ("%%%ds : %%s" % g_output_header_size) % (header, message)
  if len(status) >= g_output_screen_width:
    Print(status[:g_output_screen_width - 3] + "...\r");
  else:
    Print(status.ljust(g_output_screen_width) + "\r");

def PrintVerboseStatusLine(header=None, message=""):
  global g_output_verbosity_level;
  if g_output_verbosity_level:
    PrintStatusLine(header, message)
def PrintStatusLine(header=None, message=""):
  global g_output_header_size, g_output_screen_width;
  header = header.rjust(g_output_header_size) + " : "
  if message == "":
    PrintLine(header);
    return
  output_footer_size = g_output_screen_width - (g_output_header_size + 3)
  blocks = int(math.ceil(1.0 * (len(message) - len(header)) / (output_footer_size))) + 1
  block_size = int(math.ceil(len(message) / blocks))
  output_footer_size = g_output_screen_width - len(header)
  while len(message) > output_footer_size:
    for cut_index in range(block_size, output_footer_size):
      if message[cut_index] == " ":
        PrintLine(header + message[:cut_index]);
        message = message[cut_index + 1:]
        break
    else:
      PrintLine(header + message[:output_footer_size - 1] + "-");
      message = message[output_footer_size - 1:]
    header = "".rjust(g_output_header_size + 3)
    output_footer_size = g_output_screen_width - (g_output_header_size + 3)
  if len(message) > 0:
    PrintLine((header + message).ljust(g_output_screen_width));

def PrintVerboseSeparator():
  global g_output_verbosity_level;
  if g_output_verbosity_level:
    PrintSeparator()
def PrintSeparator():
  global g_output_screen_width;
  PrintLine("".center(g_output_screen_width, "_"));
  PrintLine();

def PrintVerboseCenteredLine(message="", pad_char=" "):
  global g_output_verbosity_level;
  if g_output_verbosity_level:
    PrintCenteredLine(message)
def PrintCenteredLine(message="", pad_char=" "):
  global g_output_header_size, g_output_screen_width;
  if message == "":
    PrintLine();
    return
  blocks = int(math.ceil(1.0 * len(message) / g_output_screen_width))
  block_size = int(math.ceil(len(message) / blocks))
  while len(message) > g_output_screen_width:
    for cut_index in range(block_size, g_output_screen_width):
      if message[cut_index] == " ":
        PrintLine(message[:cut_index].center(g_output_header_size * 2 + 3, pad_char));
        message = message[cut_index + 1:]
        break
    else:
      PrintLine(message[:g_output_screen_width - 1] + "-");
      message = message[g_output_screen_width - 1:]
  if len(message) > 0:
    PrintLine(message.center(g_output_header_size * 2 + 3, pad_char));

def PrintVerboseLine(message = ""):
  global g_output_verbosity_level;
  if g_output_verbosity_level:
    PrintLine(message)
def PrintLine(message = ""):
  global g_output_verbosity_level, g_newline;
#  if g_output_verbosity_level == 0 or message == "":
  Print(message + g_newline);
#  else:
#    PrintWrappedLine(message);

def PrintVerboseWrappedLine(message = ""):
  global g_output_verbosity_level;
  if g_output_verbosity_level:
    PrintWrappedLine(message)
def PrintWrappedLine(message = ""):
  global g_output_header_size, g_output_screen_width;
  while len(message) > g_output_screen_width:
    for cut_index in range(g_output_screen_width, g_output_header_size * 2 + 3, -1):
      if message[cut_index] == " ":
        PrintLine(message[:cut_index]);
        message = message[cut_index:]
        break
    else:
        PrintLine(message[:g_output_screen_width - 1] + "-");
        message = message[g_output_screen_width - 1:]
  if len(message) > 0:
    PrintLine(message);

def PrintInfo(info):
  global g_output_header_size;
  for header, line, in info:
    if header == "  ":
      PrintWrappedLine(line, header);
    elif header:
      if len(header) >= g_output_header_size:
        PrintWrappedLine(line, header + " ");
      else:
        PrintWrappedLine(line, header.ljust(g_output_header_size));
    else:
      PrintWrappedLine(line);

def PrintWrappedLine(line="", header=""):
  global g_output_screen_width;
  if line == "":
    PrintLine(header);
    return;
  # Calculate length of left and right blocks of output:
  left_output_length = len(header);
  right_output_length = g_output_screen_width - left_output_length;
  # Words up to 'g_line_wrap_word_length' characters long are moved to the next line if they cross a line-break. 
  # Longer words are broken up using dashes ('-').
  while len(line) > right_output_length:
    for cut_index_from_end in range(0, g_line_wrap_word_length):
      if line[right_output_length - cut_index_from_end] == " ":
        output = header + line[:right_output_length - cut_index_from_end];
        line = line[right_output_length - cut_index_from_end + 1:];
        break
    else:
      output = header + line[:right_output_length - 1] + "-";
      line = line[right_output_length - 1:];
    PrintLine(output);
    header = "".rjust(len(header));
  if len(line) > 0:
    PrintLine(header + line);

def Print(string):
  sys.stdout.write(string);

