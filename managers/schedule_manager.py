import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "survey_resources"))
from event import EventColl
import schedule_parser
from manager_basic import BasicManager
from custom_error import DuplicatesError, InvalidChoicesError, TimeError
from parser_handler import get_parser_output


class ScheduleManager(BasicManager):
  def __init__(self, mongodb_name):
    self.parser = schedule_parser.get_schedule_parser()
    self.collection = EventColl(mongodb_name)

  def manage_input(self, user,  input_string):
    parser_output = get_parser_output(self.parser, input_string)

    if(isinstance(parser_output, str)):
      return parser_output
    
    return_msg = ""

    sched_dic = parser_output

    if (sched_dic["event"]):
      sched_dic["event"] = " ".join(sched_dic["event"])
    
    if (sched_dic["place"]):
      sched_dic["place"] = " ".join(sched_dic["place"])
    
    if (sched_dic["description"]):
      sched_dic["description"] = " ".join(sched_dic["description"])

    if (sched_dic["todolist"]):
      sched_dic["todolist"] =  [" ".join(todo) for todo in sched_dic["todolist"]]

    if (sched_dic["itemlist"]):
      sched_dic["itemlist"] =  [" ".join(item) for item in sched_dic["itemlist"]]

    if (sched_dic["info"]):
      return_msg = self.schedule_info(sched_dic)
    elif (sched_dic["new"]):
      sched_dic["new"] = " ".join(sched_dic["new"])
      return_msg = self.schedule_make(user, sched_dic)
    #elif (sched_dic["delete"]):
      #return_msg = self.schedule_delete(user, sched_dic)
    else:
      return_msg = self.edit_event(user, sched_dic)
    
    return return_msg


  def schedule_info(self, sched_dic):
    return_msg = ""

    if (sched_dic["info"] == "all"):
      return_msg = self.collection.formatEvents()
    
    elif (sched_dic["event"]):
      get_event = sched_dic["event"]
      if(self.collection.isAnEvent(get_event)):
        return_msg = self.collection.getEventInfo(event = get_event)
      else:
        return_msg = f"{get_event} does not exist.\n"
        return_msg += self.schedule_info({"info" : "all"})
    
    else:
      return_msg  = self.collection.getMostRecentInfo()

    return return_msg
  
  def schedule_make(self, user, sched_dic):
    new_event = sched_dic["new"]
    if(not new_event):
      return "You must supply an event name to make an event."
    else:
      return self.collection.makeNewEvent(
          {
            "id"   : user["id"],
            "name" : user["name"], 
          },
          sched_dic
        )

  def edit_event(self, user, sched_dic):
    event = sched_dic["event"]
    return_msg = ""

    def try_edit(choosing_event):
      return_msg = ""
      try:
        return_msg = choosing_event()
      except:
        return_msg = """\
        If no special option is given with a event, then you must \
        specify your choices.
        If you are looking for information about the event, then include -i / --i \
        with your event of choice."""

      return return_msg

    if(not event):
      return_msg = try_edit(lambda : self.collection.doMostRecentEdit(user, sched_dic))
    elif (not self.collection.isAnEvent(event)):
      return_msg = "That event doesn't exist"
    else:
      return_msg = try_edit(lambda : self.collection.doEventEdit(user, event, sched_dic))

    return return_msg
    

  def getKeyword(self):
    return "!schedule"

Manager = ScheduleManager
