from custom_error import DuplicatesError

class Event:
  def __init__(self):
    self.properties = {
      "attendees" : []
    }
  
  def setDate(self, date):
    self.properties["date"] = date


  # Expected that the user will implement handling
  def addAttendee(self, attendee):
    if (attendee in self.properties["attendees"]):
      raise DuplicatesError
    else:
      self.properties["attendees"].append(attendee)

  # Expected that the user will implement handling
  def removeAttendee(self, attendee):
    self.properties.pop(self.properties["attendees"].index(attendee))

  # Will be implemented later to support iCalendar output
  def toICalEvent(self):
    pass