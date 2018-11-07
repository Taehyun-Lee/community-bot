import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(cur_dir, ".."))
from custom_error import DuplicatesError
from datetime import datetime, timedelta
from time import time

# TODO:
 # Implement a way of interpretting time, so that more general things like
  #  "next friday at 4 pm" would create an event.
def format_time(time):
  return time

def format_dur(duration):
  return duration

def format_repeat(repeat):
  return repeat

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
