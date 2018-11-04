import sys
sys.path.insert(0, './managers')
import discord
from managers import input_cases
from input_parser import parse_input_string


TOKEN = ""

client = discord.Client()

# TODO:
#  Use the clients' roles and permissions fields to give a
#   more personalized experience

@client.event
async def on_message(message):
  # we do not want the bot to reply to itself
  if message.author == client.user:
    return
  return_msg = ""


  # implement maximal munch for parsing survey questions, if they
  #  are not given in either quotes or seperated by comma
  try:
    parsed_inputs = parse_input_string(message.content)
    input_cases[parsed_inputs.pop(0)](parsed_inputs)

  except Exception:
    pass
  
  if (return_msg != ""):
    return
  
  return return_msg
  
  

    

@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')

client.run(TOKEN)
