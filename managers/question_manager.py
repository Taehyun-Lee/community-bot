import sys
import os
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "question_resources"))
from question import QuestionColl
import question_parser
from manager_basic import BasicManager
from custom_error import DuplicatesError, InvalidChoicesError
from parser_handler import get_parser_output

# TODO:
#  * Change the survey module entirely to allow for data storage
#    on mongodb. (need a complete overhaul)




# QuestionManager class
class QuestionManager(BasicManager):
  def __init__(self, mongodb_name):
    # TODO:
    #  Change the survey_questions and survey_list to come from
    #   mongodb to preserve all the questions, as well as to build
    #   on to it later on
    self.parser = question_parser.get_question_parser()
    self.collection = QuestionColl(mongodb_name)

  # Main function for text interaction with survey module
  def manage_input(self, user, input_string):
    parser_output = get_parser_output(self.parser, input_string)

    if(isinstance(parser_output, str)):
      return parser_output

    return_msg = ""
    
    quest_dic = parser_output

    if (quest_dic["question"]):
      quest_dic["question"] = " ".join(quest_dic["question"])
    
    if (quest_dic["choose"]):
      quest_dic["choose"] =  [" ".join(choice) for choice in quest_dic["choose"]]

    if (quest_dic["info"]):
      return_msg = self.question_info(quest_dic)
    elif (quest_dic["new"]):
      quest_dic["new"] = " ".join(quest_dic["new"])
      return_msg = self.question_make(user, quest_dic)
    elif (quest_dic["delete"]):
      return_msg = self.question_delete(user, quest_dic)
    else:
      return_msg = self.question_choose(user, quest_dic)
    
    return return_msg

    
  
  def question_info(self, quest_dic):
    return_msg = ""

    if (quest_dic["info"] == "all"):
      return_msg = self.collection.formatQuestions()
    
    elif (quest_dic["question"]):
      get_question = quest_dic["question"]
      if(self.collection.isAQuestion(get_question)):
        return_msg = self.collection.getQuestionInfo(question = get_question)
      else:
        return_msg = f"{get_question} does not exist.\n"
        return_msg += self.question_info({"info" : "all"})
    
    else:
      return_msg  = self.collection.getMostRecentInfo()

    return return_msg


  def question_make(self, user, quest_dic):
    new_question = quest_dic["new"]
    if(not new_question):
      return "You must supply a question name to make a question"
    elif(self.collection.isAQuestion(new_question)):
      return "You can't make a duplicate question."
    else:
      self.collection.makeNewQuestion(
          {
            "id"   : user["id"],
            "name" : user["name"], 
          },
          quest_dic
        )
      return ""

  def question_delete(self, user, quest_dic):
    question = quest_dic["question"]
    return_msg = ""
    if(self.collection.isAQuestion(question)):
      try:
        self.collection.removeQuestion(user, question)
      except:
        return_msg = f"No permission to delete question **{question}**"
      
    else:
      return_msg = f"{question} does not exist.\n"
      return_msg += self.question_info({"info" : "all"})
    return return_msg


  def question_choose(self, user, quest_dic):
    question = quest_dic["question"]
    return_msg = ""

    def try_choosing(choosing_question):
      return_msg = ""
      try:
        return_msg = choosing_question()
      except:
        return_msg = """\
        If no special option is given with a question, then you must \
        specify your choices.
        If you are looking for information about the question, then include -i / --i \
        with your question of choice."""

      return return_msg

    if(not question):
      return_msg = try_choosing(lambda : self.collection.registerMostRecentChoices(user, quest_dic["choose"]))
    elif (not self.collection.isAQuestion(question)):
      return_msg = "That question doesn't exist"
    else:
      return_msg = try_choosing(lambda : self.collection.registerQuestionChoices(user, question, quest_dic["choose"]))
    
    return return_msg



  def getKeyword(self):
    return "!survey"

  

Manager = QuestionManager


# For testing
if (__name__) == "__main__":
  test_survey = Manager("community-bot")

  def handle_input(account, inputs):
    return test_survey.manage_input(account, inputs)

  test_accounts = [{"id" : i, "name" : f"test account {i}", "roles" : ["question manager"]} for i in range(1, 5)]

  test_inputs = []
  test_inputs.append("-n What is your favorite food? -e Liquid Water -e Liquid Gas -e Solid -e Plasma")
  test_inputs.append("-m What is your favorite food? -e Ramen -e Liquid Water")
  test_inputs.append("-i")
  test_inputs.append("-i all")
  test_inputs.append("-i -m What is your favorite food?")
  test_inputs.append("-m What is your favorite food? -e Ramen -e Liquid Water")
  test_inputs.append("-i")
  test_inputs.append("-h")
  test_inputs.append("-x -m What is your favorite food?")
  test_inputs.append("-i all")


  for test_input in test_inputs:
    print(handle_input(test_accounts[0], test_input))


