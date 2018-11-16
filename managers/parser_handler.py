from contextlib import contextmanager
from io import StringIO
import sys

@contextmanager
def redirect_stdout_stderr(stream):
  old_stdout = sys.stdout
  old_stderr = sys.stderr
  sys.stdout = stream
  sys.stderr = stream
  try:
    yield
  finally:
    sys.stdout = old_stdout
    sys.stderr = old_stderr

def get_parser_output(parser, inputs):
  quest_dic = {}
  msg = StringIO()

  with redirect_stdout_stderr(msg):
      try:
        quest_dic = vars(parser.parse_args(inputs.split()))
      except:
        return msg.getvalue()
  
  return quest_dic