class Error(Exception):
  """ Default error class for custom errors """
  pass

class InvalidChoicesError(Error):
  """ Error for when the passed in list of options is empty"""
  pass

class DuplicatesError(Error):
  """ Error for when the user attempts to make a new entry for
      some list, but the list doesn't take any duplicates """
  pass

class TimeError(Error):
  pass
  