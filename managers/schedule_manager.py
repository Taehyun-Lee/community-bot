from manager_basic import BasicManager
import sys
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "survey_resources"))
from event import Event
from custom_error import DuplicatesError, InvalidOptionsError

class ScheduleManager(BasicManager):
  def __init__(self):
    self.scheduled_events = []
    self.event_names = []
    self.schedule_commands = {
      "info" : self.schedule_info,
      "make" : self.schedule_make,
    }

  def manage_input(self, user,  schedule_input):
    self.event_names = [event.getName() for event in self.scheduled_events]
    return_msg = ""

    try:
      schedule_opt = schedule_input.pop(0)
      return_msg = self.schedule_commands[schedule_opt](schedule_input)
    except KeyError:
      return_msg = self.event_options(schedule_opt, schedule_input)
    except IndexError:
      return_msg = "You need to specify an option or event name"

    return return_msg

  def schedule_info(self, args, *kwargs):
    pass
  
  def schedule_make(self, schedule_input):
    try:
      [event_name, start_time, *end_time] = schedule_input
      if ((event_name in self.schedule_commands) or (event_name in self.event_names)):
        raise DuplicatesError
      else:
        self.scheduled_events.append(Event(event_name, start_time, end_time))
    except ValueError:
      return "You must supply an event name followed by the time it will occur"
    except DuplicatesError:
      return "Please choose a different event name, or set the specified event to repeat"

  def event_options(self, event_name, schedule_input):
    try:
      [option, *extras] = schedule_input
    except:


    return ""

  def getKeyword(self):
    return "!schedule"

Manager = ScheduleManager
