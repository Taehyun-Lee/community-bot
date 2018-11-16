import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(cur_dir, ".."))
from custom_error import InvalidChoicesError
from mongodb_access import use_mongodb as _use_mongodb
from datetime import datetime, timedelta
from time import time


class QuestionColl:
  def __init__(self, db_name):
    self.use_mongodb = lambda : _use_mongodb(db_name, "quest_coll")
    self.most_recent_question = ""
    self.admin_roles = [
      "question manager"
    ]
  

  def formatQuestions(self):
    return_msg = ""
    with self.use_mongodb() as coll:
      questions = coll.distinct("question")
      if(len(questions)):
        return_msg = "Available questions are:\n" + " | ".join(questions)
      else:
        return_msg = "There are no questions at the moment"
    
    return return_msg

  
  def isAQuestion(self, question):
    isAQuestion = False
    with self.use_mongodb() as coll:
      isAQuestion = question in coll.distinct("question")
    
    return isAQuestion
  

  def getQuestionInfo(self, question):
    return_msg = ""
    with self.use_mongodb() as coll:
      question_obj = coll.find_one({"question" : question}) # guaranteed to exist
      mult_chos = len(question_obj["results"]) > 1
      return_msg = f"Choice{'s' if mult_chos else ''} for **{question}**:\n"
      for ind, result in enumerate(question_obj["results"], 1):
        return_msg += f"{ind:>5}: {result[0]:<40} - {result[1]}\n"
    
    return return_msg
  

  def getMostRecentInfo(self):
    if(self.most_recent_question):
      return self.getQuestionInfo(self.most_recent_question)
    else:
      return "A 'recent question' does not exist"


  def makeNewQuestion(self, maker, quest_dic):
    question = quest_dic["new"]
    choices = quest_dic["choose"] if quest_dic["choose"] else []
    time = quest_dic["time"]
    num_picked = [0] * len(choices)
    pickers = [[]] * len(choices)

    self.most_recent_question = question

    with self.use_mongodb() as coll:
      coll.insert_one({
        "maker" : maker,
        "question" : question,
        "results"  : list(map(list, zip(choices, num_picked, pickers))),
        "start-time" : datetime.now(),
        "end-safe-time"   : datetime.now() + timedelta(minutes = time)
      })
    
    return ""


  def isAdmin(self, user):
    role_intersect = (set(user["roles"]).intersection(self.admin_roles))
    return len(role_intersect)

  def canDelete(self, user, question):
    if (self.isAdmin(user)):
      return True

    canDelete = False
    with self.use_mongodb() as coll:
      question_obj = coll.find_one({"question" : question})
      canDelete = (user["id"] == question_obj["maker"]["id"]
                  and (datetime.now() > question_obj["end-safe-time"]))
    
    return canDelete

  # calling changeEndTime will set self.start_time along with self.end_start_time
  def changeEndTime(self, user, question, new_time):
    if(self.canDelete(user, question) and (new_time <= 60 or self.isAdmin(user))):
      with self.use_mongodb() as coll:
        question_obj = coll.find_one({"question" : question})
        start_time = question_obj["start-time"]
        end_safe_time = question_obj["end-safe-time"]
        if (isinstance(end_safe_time, str)):
          end_safe_time = datetime.now()
        start_time = end_safe_time

        if (new_time > 60):
          end_safe_time = "infinite"
        else:
          end_safe_time += timedelta(minutes = new_time)

        coll.find_one_and_update(
          {
            "question" : question
          },
          {
            "$set" : 
            {
              "start-time" : start_time,
              "end-safe-time" : end_safe_time
            }
          },
        )
        

  def removeQuestion(self, user, question):
    if(self.canDelete(user, question)):
      with self.use_mongodb() as coll:
        coll.find_one_and_delete({"question" : question})
    else:
      raise ValueError
    


  def registerQuestionChoices(self, user, question, choices):
    if (not len(choices)):
      raise ValueError

    with self.use_mongodb() as coll:
      question_obj = coll.find_one({"question" : question})
      results = question_obj["results"]
      
      choices = list(set(choices))

      for res in results:
        if (res[0] in choices):
          if (not user["id"] in res[2]):
            res[1] += 1
            res[2].append(user["id"])
          else:
            res[1] -= 1
            res[2].remove(user["id"])
          
          choices.remove(res[0])
        
      if(len(choices)):
        for choice in choices:
          results.append([choice, 1, [user["id"]]])
      
      coll.find_one_and_update(
        {
          "question" : question
        },
        {
          "$set" : 
          {
            "results" : results
          }
        },
      )
      

  def registerMostRecentChoices(self, user, choices):
    if(self.most_recent_question):
      return self.registerQuestionChoices(user, self.most_recent_question, choices)
    else:
      return "A 'recent question' does not exist"
