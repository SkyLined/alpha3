import os, sys;

def LongPath(path = None, *sub_paths):
  if not path or path == ".":
    path = os.getcwdu()
  for sub_path in sub_paths:
    path = os.path.join(path, sub_path)
  # Turn relative paths into absolute paths and normalize the path
  path = os.path.abspath(path)
  # Win32 has issues with paths > MAX_PATH. The string '\\?\' allows us to work
  # around MAX_PATH limitations in most cases. One example for which this does 
  # not work is os.chdir(). No other limitations are currently known.
  # http://msdn.microsoft.com/en-us/gozerlib.ary/aa365247.aspx
  if (sys.platform == "win32") and not path.startswith(u"\\\\?\\"):
    path = u"\\\\?\\" + path
    if not path.endswith(os.sep) and os.path.isdir(path):
      # os.listdir does not work if the path is not terminated with a slash:
      path += os.sep
  return path

def ShortPath(path = None, *sub_paths):
  # Untested with paths > MAX_PATH
  path = LongPath(path, *sub_paths)
  if path.startswith("\\\\?\\"):
    path = path[4:]
  return os.path.relpath(path, os.getcwd())

def ReadFile(file_name, path=None):
  if path == None:
    path = os.getcwd()
  fd = open(os.path.join(path, file_name), "rb")
  try:
    return fd.read()
  finally:
    fd.close()

def WriteFile(file_name, contents, path=None):
  if path == None:
    path = os.getcwd()
  fd = open(os.path.join(path, file_name), "wb")
  try:
    return fd.write(contents)
  finally:
    fd.close()
