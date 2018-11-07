import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "survey_resources"))
from survey import Survey
from manager_basic import BasicManager
from custom_error import DuplicatesError, InvalidOptionsError
import argparse

class SurveyManager(BasicManager):
  def __init__(self):
    # TODO:
    #  Change the survey_questions and survey_list to come from
    #   mongodb to preserve all the questions, as well as to build
    #   on to it later on
    self.survey_questions = []
    self.survey_list = []
    self.survey_commands = {
      "info" : self.survey_info,
      "make" : self.survey_make,
    }

  def manage_input(self, user,  survey_input):
    self.survey_questions = [survey.getQuestion() for survey in self.survey_list]
    return_msg = ""

    try:
      survey_opt = survey_input.pop(0)
      return_msg = self.survey_commands[survey_opt](survey_input)
    except KeyError:
      return_msg = self.survey_opt_choose(survey_opt, survey_input)
    except IndexError:
      return_msg = "You need to specify an option or survey name"
    
    return return_msg
    
  def survey_info(self, survey_input):
    
    return_msg = ""
    
    if (len(survey_input) > 0):
      return_msg = "Survey Infos:\n"
      for survey_question in survey_input:
          
        try:
          requested_survey = self.survey_list[self.survey_questions.index(survey_question)]
          return_msg += requested_survey.getInfo()

        except:
          return_msg += "*** No question called {survey_question}\n"
        
        return_msg += "\n"
    else:
      if (len(self.survey_questions) > 0):
        return_msg = "Available questions are:\n" + "\n".join(self.survey_questions)
      else:
        return_msg = "There are no questions right now"

    return return_msg



  def survey_make(self, survey_input):
    try:
      [survey_question, *options] = survey_input
      if ((survey_question in self.survey_commands) or (survey_question in self.survey_questions)):
        raise DuplicatesError
      else:
        self.survey_list.append(Survey(survey_question, options))
    except ValueError:
      return "You must give a survey name"
    except InvalidOptionsError:
      return "A new survey must have at least one option"
    except DuplicatesError:
      return "Your question is either a duplicate or not valid"
      

  def survey_opt_choose(self, survey_question, survey_input):
    try:
      [*choices] = survey_input
      if (len(choices) < 1):
        raise ValueError
      
      for survey in self.survey_list:
        if (survey.getQuestion() == survey_question):
          for option in choices:
            survey.choose(option)
          break

    except ValueError:
      return " A survey title must be followed either by at least one choices for the survey "
    
    return ""

  def getKeyword(self):
    return "!survey"
  

Manager = SurveyManager

def get_parser():
  survey_parser = argparse.ArgumentParser(
    prog = "survey!",
    description = "Survey Parser",
    conflict_handler = "resolve",
  )

  survey_parser.add_argument(
    "-n", "--new",
    action = "store_true",
    help = """If you supply -n or --new, the specified question\
     will be created, given that it doesn't exist""",
  )

  survey_parser.add_argument(
    "-d", "--delete",
    action = "store_true",
    help = """If only a question name is supplied, adding this flag will \
    delete the specified question, given that either no one has voted for \
    the question, or if the only person that voted for the question is \
    the caller.
    If no question name is supplied, it defaults to the most recently created \
    question.
    
    If a choice is supplied along with the flag, the given choice will be \
    deleted from the survey (which is chosen according to above), given \
    that the choice has no votes or if the caller is the only one who has \
    voted for the choice.""",
  )

  survey_parser.add_argument(
    "-i", "--info",
    action = "store_true",
    help = """ """,
  )

  survey_parser.add_argument(
    "-q", "--question",
    nargs = "+",
    type = str,
    help = """Specifies which question to be interacted with.""",

  )

  survey_parser.add_argument(
    "-c", "--choose",
    action = "append",
    nargs = "+",
    type = str,
    help = """Increments counter of the specified choice if it \
    exists, and creates the choice if it doesn't. The question that the \
    number will increment for will either be the supplied question, or \
    the most recently made question.
    
    You can supply -c or --choose multiple times to choose more than \
    one choice. If you supply the same choice multiple times in one call, \
    it will not deselect the option.
    
    """,
  )

  return survey_parser





# For testing
if (__name__) == "__main__":
  test_survey = SurveyManager()
  print (test_survey.manage_input(None, ["info"]))
  test_survey.manage_input(None, ["make", "What is your favorite colour?", "Blue", "Red"])
  test_survey.manage_input(None, ["What is your favorite colour?", "Orange"])
  
  print(test_survey.manage_input(None, ["info", "What is your favorite colour?"]))
  print (test_survey.manage_input(None, ["info"]))
