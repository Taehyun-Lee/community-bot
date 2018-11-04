from manager_basic import BasicManager

class HelpManager(BasicManager):
  def manage_input(self, help_input):
    pass
  
  def getKeyword(self):
    return "!help"

Manager = HelpManager