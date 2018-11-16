import argparse

def get_question_parser():
  question_parser = argparse.ArgumentParser(
    prog = "question!",
    description = "Question Parser",
    conflict_handler = "resolve",
  )

  question_parser.add_argument(
    "-n", "--new",
    nargs = "+",
    type = str,
    help = """\
    An arugment to specify the name of the new question.
    Creates the specified question.
    
    Specifying -n / --new will omit -m / --question.
    """,
  )

  question_parser.add_argument(
    "-x", "--delete",
    action = "store_true",
    help = """\
    If only a question name is supplied, adding this flag will \
    delete the specified question, given that either no one has voted for \
    the question, or if the only person that voted for the question is \
    the caller.
    If no question name is supplied, it defaults to the most recently created \
    question.
    
    If a choice is supplied along with the flag, the given choice will be \
    deleted from the question (which is chosen according to above), given \
    that the choice has no votes or if the caller is the only one who has \
    voted for the choice.""",
  )

  question_parser.add_argument(
    "-i", "--info",
    nargs = "?",
    const = True,
    default = False,
    choices = ["all"],
    help = """\
    Gives information depending on supplied parameters. \
    If you supply just -i / --info without -m / --question, it will give \
    all the questions available. 
    If you specify a question, it will \
    give the choices for that question along with the tally of each \
    choice.
    
    **Specifying -i / --info will make it ignore your -c / --choose \
    inputs.**""",
  )

  question_parser.add_argument(
    "-m", "--question",
    nargs = "+",
    type = str,
    help = """Specifies which question to be interacted with.""",

  )

  question_parser.add_argument(
    "-e", "--choose",
    action = "append",
    nargs = "+",
    type = str,
    help = """\
    Increments counter of the specified choice if it \
    exists, and creates the choice if it doesn't. 
    The question that the \
    number will increment for will either be the supplied question, or \
    the most recently made question.
    
    You can supply -c or --choose multiple times to choose more than \
    one choice. 
    If you supply the same choice multiple times in one call, \
    it will not deselect the option.
    """,
  )

  question_parser.add_argument(
    "-t", "--time",
    default = 10,
    type = int,
    help = """\
    This parameter specifies the amount of time that the question will be alive for.
    
    A question cannot be deleted for the specified amount of minutes (max being 60).
    A question that has passed this time may be deleted by the owner, but a question \
    moderator may delete it at any time.
    
    A question moderator may change the time parameter of any question. \
    For a question moderator, setting the value above 60 will make it last forever.
    """
  )

  return question_parser

