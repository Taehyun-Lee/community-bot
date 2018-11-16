import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(cur_dir, ".."))
from custom_error import DuplicatesError, TimeError
from mongodb_access import use_mongodb as _use_mongodb
from datetime import datetime, timedelta
from time import time
from dateparser import parse as time_parse
from pytimeparse import parse as delta_parse

def addToOutput(attr, attr_value):
  attr = attr.capitalize()
  return f"\n{attr}:\n{attr_value}\n"

def format_time(time_str):
  parsed = time_parse(time_str)
  if(not parsed):
    raise TimeError
  
  return parsed

def format_length(len_str):
  parsed = delta_parse(len_str)
  if(not parsed):
    raise TimeError
  
  return parsed

class EventColl:
  def __init__(self, db_name):
    self.use_mongodb = lambda : _use_mongodb(db_name, "sched_coll")
    self.most_recent_event = ""
    self.admin_roles = [
      "schedule manager"
    ]


  def formatEvents (self):
    return_msg = ""
    with self.use_mongodb() as coll:
      events = coll.distinct("event")
      if(len(events)):
        sorted(
          iterable = events, 
          key      = lambda event: event["start-time"], 
          reverse = True
        )
        return_msg = "Upcoming Events are:\n" + " | ".join(events)
      else:
        return_msg = "There are no upcoming events"
    
    return return_msg
  

  def isAnEvent(self, event):
    isAnEvent = False
    with self.use_mongodb() as coll:
      isAnEvent = event in coll.distinct("event")
    
    return isAnEvent


  def getEventInfo(self, event):
    return_msg = ""
    with self.use_mongodb as coll:
      event_obj = coll.find_one({"event" : event}) # guaranteed to exist

      return_msg = f"{event}:\n"

      return_msg += f"""{event_obj["start-time"]} ~ \
      {event_obj["end-time"]} \
      (length = {event_obj["end-time"] - event_obj["start-time"]})\n"""

      if (event_obj["description"]):
        return_msg += addToOutput("description", event_obj["description"])
      
      if (event_obj["place"]):
        return_msg += addToOutput("place", event_obj["place"])

      todo_msg = ""
      if (event_obj["todolist"]):
        mult_todos = len(event_obj["todolist"]) > 1
        todo_msg = f"\nTodo{'s' if mult_todos else ''}:\n"
        for ind, todo in enumerate(event_obj["todolist"], 1):
          todo_msg += f"{ind:>5}: {todo:<40}\n"
      else:
        todo_msg = "\nNo todos\n"
      
      return_msg += todo_msg

      item_msg = ""
      if (event_obj["itemlist"]):
        mult_todos = len(event_obj["itemlist"]) > 1
        item_msg = f"\nItem{'s' if mult_todos else ''} to bring:\n"
        for ind, item in enumerate(event_obj["itemlist"], 1):
          item_msg += f"{ind:>5}: {item:<40}\n"
      else:
        item_msg = "\nNo items to bring\n"
      return_msg += item_msg
    
    return return_msg

  
  def getMostRecentInfo(self):
    if(self.most_recent_event):
      return self.getEventInfo(self.most_recent_event)
    else:
      return "A 'recent event' does not exist"
  

  def makeNewEvent(self, maker, sched_dic):
    event = sched_dic["new"]
    todolist = sched_dic["todolist"] if sched_dic["todolist"] else []
    itemlist = sched_dic["itemlist"] if sched_dic["itemlist"] else []
    start_time = None
    end_time = None

    if (len(sched_dic["time"]) == 2):
      start_time, end_time = sched_dic["time"]
      start_time = format_time(start_time)
      end_time = format_time(end_time)

    else:
      start_time = sched_dic["time"]
      start_time = format_time(start_time)
      length = format_length(sched_dic["length"])
      end_time = start_time + length

    if(start_time < end_time):
        raise TimeError
    
    with self.use_mongodb() as coll:
      coll.insert_one({
        "maker"       : maker,
        "event"       : event,
        "description" : sched_dic["description"],
        "place"       : sched_dic["place"],
        "todolist"    : todolist,
        "itemlist"    : itemlist,
        "start-time"  : start_time,
        "end-time"    : end_time
      })
    
    return ""

    
    


    
    



  
  def doEventEdit(self, user, event, sched_dic):
    pass
  
  def doMostRecentEdit(self, user, sched_dic):
    pass


class Event:
  def __init__(self, event_name, start_time, duration):
    if (len(duration) < 1):
      duration = "1 hour"
    
    start_time = format_time(start_time)

    if(start_time < datetime.now()):
      raise ValueError

    self.event_name = event_name
    self.time = {
        "start"    : start_time,
        "duration" : format_dur(duration),
        "repeat"   : None,
    }
    self.attendees = []
    self.items = []
  
  def resetStartTime(self, new_start_time):
    new_start_time = format_time(new_start_time)

    if(new_start_time < datetime.now()):
      raise ValueError

    self.time["start"] = new_start_time

  def resetDuration(self, new_duration):
    duration = format_dur(new_duration)

    if (duration < timedelta(0)):
      raise ValueError
    
    self.time["duration"] = duration

  def setRepeat(self, repeat):
    repeat = format_repeat(repeat)

    if (repeat < timedelta(0)):
      raise ValueError

    self.time["repeat"] = repeat
    
  # Expected that the user will implement handling
  def addAttendee(self, attendee):
    if (attendee in self.attendees):
      raise DuplicatesError
    else:
      self.attendees.append(attendee)

  # Expected that the user will implement handling
  def removeAttendee(self, attendee):
    try:
      self.attendees.pop(self.attendees.index(attendee))
    except ValueError:
      # This is expected to happen if a user tries to not attend
      #  an event he/she didn't attend to begin with
      raise ValueError

  def addItems(self, item_list):
    self.items = list(set().union(self.items, item_list))

  def removeItems(self, item_list):
    self.items = [item for item in self.items if item not in item_list]
  
  def getName(self):
    return self.event_name

  def setName(self, new_event_name):
    self.event_name = new_event_name

  # Will be implemented later to support iCalendar output
  def toICalEvent(self):
    pass
