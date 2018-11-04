from custom_error import InvalidOptionsError

class Survey:
  def __init__(self, survey_question, options):
    self.survey_question = survey_question
    
    # Remove duplicate options
    options = list(set(options))
    
    # The survey must have at least one option available
    if(len(options) < 1):
      raise InvalidOptionsError

    num_picked = [0] * len(options)
    self.results = list(zip(options, num_picked))
     
  def choose(self, option):
    num_option = 0
    for opt in self.results:
      if opt[0] == option:
        opt[1] += 1
        num_option += 1
    
    if(num_option == 0):
      self.results.append((option, 1))
  
  def getOptions(self):
    return [opt for opt, _ in self.results]

  def getResults(self):
    return self.results.copy()

  def getQuestion(self):
    return self.survey_question

  def getInfo(self):
    mult_opts = len(self.results) > 1
    return_msg = f"Choice{'s' if mult_opts else ''} for {self.survey_question}:\n"
    for ind, result in enumerate(self.results):
      return_msg += f"{ind:>5}: {result[0]} - {result[1]}\n"
    
    return return_msg

