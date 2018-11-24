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
from icalendar import Calendar, Event

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
  
  return timedelta(seconds = parsed)

def isOverlapping(event1, event2):
  return ((event1["start"] < event2["end"] and event1["end"] > event2["end"]) 
  or (event2["start"] < event1["end" and event2["end"] > event1["end"]]))

# closestEvent takes in a list of events, a datetime object, and optional
#  keyworded arguments 'user' and 'allow_older'.
# The default behavior is to return the event that best corresponds to the given
#  select_time datetime object, given that this event ends later than
#  datetime.now().
# If the 'user' argument exists, it behaves the same way except it will have an
#  additional filter to check that event was created by the user.
# If the 'allow_older' argument exists, it will allow older events to be returned,
#  although it will prefer to bring events that haven't ended yet.
# For either case, if no event is found, it will return None.
# 
# Because closestEvent is never called before isAnEvent is called, event_list
#  is guaranteed to be non empty.
def closestEvent(event_list, select_time, **kwargs):
  sorted(
    iterable = event_list,
    key = lambda event : event["start-time"],
    reverse = True
  )
  ret_ind = -1
  min_delta = timedelta.max

  check_id = None
  allow_older = False
  if kwargs is not None:
    if "user" in kwargs:
      check_id = kwargs["user"]
    if "allow_older" in kwargs:
      allow_older = True

  for ind, event in enumerate(event_list):
    event_time = event["start-time"] + (event["end-time"] - event["start-time"]) / 2
    if((abs(select_time - event_time)) > min_delta):
      break
    
    if((event["end-time"] > datetime.now() or allow_older)
    and (check_id is None or check_id == event["maker"]["id"])):
      ret_ind = ind
    
  return event_list[ret_ind] if (len(event_list) >= ret_ind) else None

# Parses and returns datetime objects for start_time and end_time
# It will return a tuple containing two datetime objects,
#  start_time and end_time
# It will raise a TimeError given the following:
#  * any one of start_time and end_time could not be parsed
#  * start_time < end_time
#  * start_time < datetime.now()
def handle_time(sched_dic):
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

  if(start_time < end_time or start_time < datetime.now()):
      raise TimeError
  
  return (start_time, end_time)

class EventColl:
  def __init__(self, db_name):
    self.use_mongodb = lambda : _use_mongodb(db_name, "sched_coll")
    self.most_recent_event = ""
    self.most_recent_time = None
    self.admin_roles = [
      "schedule manager"
    ]


  def formatEvents (self):
    return_msg = ""
    with self.use_mongodb() as coll:
      events = coll.find(
        { "event"    : { "$exists" : True }},
        { "end-time" : { "$gte" : datetime.now()}}
        ).sort({ "start-time" : 1})
      if(len(events)):
        return_msg = "Upcoming Events are:\n" + " | ".join(events)
      else:
        return_msg = "There are no upcoming events"
    
    return return_msg
  

  def isAnEvent(self, event):
    isAnEvent = False
    with self.use_mongodb() as coll:
      isAnEvent = coll.find_one({"event" : event}) is not None
    
    return isAnEvent


  # returns a formatted string describing the specifications of the
  #  requested event
  def getEventInfo(self, event, select_time):
    select_time = format_time(select_time)
    return_msg = ""
    with self.use_mongodb as coll:
      event_obj_list = coll.find_one({"event" : event}) 
      event_obj = closestEvent(event_list, select_time, allow_older = True) # guaranteed to exist

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
      return self.getEventInfo(self.most_recent_event, self.most_recent_time)
    else:
      return "A 'recent event' does not exist"


# Creates a new event
# If there already exists an event that overlaps with the new event
#  and that event is made by the same maker of the new event, the
#  old event gets deleted.
  def makeNewEvent(self, maker, sched_dic):
    event = sched_dic["new"]
    todolist = sched_dic["todolist"] if sched_dic["todolist"] else []
    itemlist = sched_dic["itemlist"] if sched_dic["itemlist"] else []

    start_time, end_time = [None, None]

    try:
      start_time, end_time = handle_time(sched_dic)
    except TimeError:
      return """\
      Either you didn't specify information regarding time, \
      or the time given could not be parsed"""

    with self.use_mongodb() as coll:
      same_name_events = coll.find({"event" : event})
      if (len(same_name_events)):
        for same_name_event in same_name_events:
          if (same_name_event["maker"]["id"] == maker["id"]
            and isOverlapping(
              { "start" : start_time, "end" : end_time },
              { "start" : same_name_event["start-time"], "end" : same_name_event["end-time"]}
            )):
            self.deleteEvent(
              user, 
              event, 
              same_name_event["start-time"] 
              + (same_name_event["start-time"]- same_name_event["end-time"]) / 2
            )

      coll.insert_one({
        "maker"       : maker,
        "event"       : event,
        "description" : sched_dic["description"],
        "place"       : sched_dic["place"],
        "todolist"    : todolist,
        "itemlist"    : itemlist,
        "start-time"  : start_time,
        "end-time"    : end_time,
        "uid"         : binascii.hexlify(urandom(16)).decode('utf-8')
      })
    
    self.most_recent_event = event
    self.most_recent_time  = start_time + (start_time - end_time) / 2

  def isAdmin(self, user):
    role_intersect = (set(user["roles"]).intersection(self.admin_roles))
    return len(role_intersect)
  

  def canAdvancedEdit(self, user, event, select_time):
    if (self.isAdmin(user)):
      return True
    
    select_time = format_time(select_time) if isinstance(select_time, str) else select_time

    canAdvancedEdit = False
    with self.use_mongodb() as coll:
      event_obj_list = coll.find({"event" : event})
      event_obj = closestEvent(event_obj_list, select_time, user = user)
      canAdvancedEdit = event_obj is not None
      
    return canAdvancedEdit


  def deleteEvent(self, user, event, select_time):
    select_time = format_time(select_time)
    if(not self.canAdvancedEdit(user, event, select_time)):
      return "You don't have the permission to edit this event."
    with self.use_mongodb() as coll:
      event_obj_list = coll.find({"event" : event})
      if(self.isAdmin(user)):
        event_obj = closestEvent(event_obj_list, select_time)
      else:
        event_obj = closestEvent(event_obj_list, select_time, user = user)

      if(event_obj is not None):
        coll.find_one_and_delete({ "uid" : event_obj["uid"]})
        return ""
      else:
        return f"""No upcoming event \"{event}\" that can be deleted.
        Make sure the specified event is made by you, or that the event \
        exists to begin with."""

    
  def doEventEdit(self, user, event, sched_dic, select_time):
    select_time = format_time(select_time)
    has_perm = self.canAdvancedEdit(user, event)
    no_perm_req = True

    with self.use_mongodb() as coll:
      event_obj_list = coll.find({"event", event})
      event_obj = closestEvent(event_obj_list, select_time)

      if(event_obj is None):
        return f"""\
        The specified event doesn't exist, or the event has already finished."""

      if (sched_dic["delete"]):

        deleteEvent = True

        def handle_single(attr, permission):
          if(sched_dic[attr] != None and bool):
            event_obj[attr] = None
            deleteEvent = False

        def handle_list(attr, bool):
          if(sched_dic[attr] != None and bool):
            event_obj[attr] = list(set(event_obj[attr]) - set(sched_dic[attr]))
            deleteEvent = False
        
        handle_single("description", has_perm)
        handle_single("place", has_perm)
        handle_list("todolist", no_perm_req)
        handle_list("itemlist", no_perm_req)

        if(deleteEvent and has_perm):
          coll.find_one_and_delete({"event", event})
          return ""
        elif (deleteEvent):
          return f"""\
          You don't have permission to delete this event."""
      else:
        
        def handle_single(attr, permission):
          if(sched_dic[attr] != None and bool):
            event_obj[attr] = sched_dic[attr]

        def handle_list(attr, bool):
          if(sched_dic[attr] != None and bool):
            event_obj[attr] = list(set(event_obj[attr]) | set(sched_dic[attr]))
        
          handle_single("description", has_perm)
          handle_single("place", no_perm_req)
          handle_list("todolist", no_perm_req)
          handle_list("itemlist", no_perm_req)

          start_time, end_time = [None, None]
          
          try:
            start_time, end_time = handle_time(sched_dic)
          except TimeError:
            return """\
            Either you didn't specify information regarding time, \
            or the time given could not be parsed"""
          
          if(start_time != None and end_time != None):
            event_obj["start-time"] = start_time
            event_obj["end-time"] = end_time

      coll.find_one_and_update(
        {
          "event" : event
        },
        {
          "$set": event_obj
        }
      )


  def doMostRecentEdit(self, user, sched_dic):
    doEventEdit(user, self.most_recent_event, sched_dic, self.most_recent_time)

  
  def getICalFormatted(self, event):
    cal = Calendar()
    cal["dtstart"] = "20160131T080000"
    cal["summary"] = "community-bot generated calendar"

    with self.use_mongodb() as coll:
      events = coll.distinct("event")
      for event in events:
        cal_event = Event()
        cal_event["uid"] = f"{event['uid']}@community-bot"
        cal_event.add("dtstart", event["start-time"])
        cal_event.add("duration", event["end-time"] - event["start-time"])
        cal_event.add("summary", event["event"])
        if(event["place"]):
          cal_event.add("location", event["place"])
        if(event["description"]):
          cal_event.add("description", event["description"])
        
        cal_event.add("organizer", event["maker"]["name"])
      cal.add_component(cal_event)


    return cal.to_ical().replace("\r\n", "\n").strip()



