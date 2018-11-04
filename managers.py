import glob
import sys

sys.path.insert(0, './managers')

# imports all modules that end with _manager.py
# This allows for any number of additional commands to be supported
managers = [__import__(module[9:-3]) for module in glob.glob("managers/*_manager.py")]
# input_cases is a dictionary that has all the input handling functions
input_cases = {}

# As can be seen below, all managers must implement:
#  getKeyword() and
#  manage_func()

# TODO: 
#  Make sure to assert that the modules have the two
#  required functions.
for manager in managers:
  manager = manager.Manager()
  input_cases[manager.getKeyword()] = manager.manage_input


