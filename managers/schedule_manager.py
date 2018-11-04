from manager_basic import BasicManager
from event import Event

class ScheduleManager(BasicManager):
  def __init__(self):
    self.scheduled_events = []
    self.event_names = []
    self.schedule_commands = {
      "info" : self.schedule_info,
      "make" : self.schedule_make,
    }

  def manage_input(self, schedule_input):
    
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
  
  def schedule_make(self, args, *kwargs):
    pass

  def event_options(self, event_name, schedule_input):
    
    return ""

  def getKeyword(self):
    return "!schedule"

Manager = ScheduleManager