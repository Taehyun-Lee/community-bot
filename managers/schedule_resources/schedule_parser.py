import argparse

# from https://stackoverflow.com/questions/4194948/python-argparse-is-there-a-way-to-specify-a-range-in-nargs
def required_length(nmin,nmax):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin<=len(values)<=nmax:
                msg='argument "{f}" requires between {nmin} and {nmax} arguments'.format(
                    f=self.dest,nmin=nmin,nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            if (not len(values)):
              values = [self.default]
            print(self.default)
            print(values)
            setattr(args, self.dest, values)
    return RequiredLength

def get_schedule_parser():
  schedule_parser = argparse.ArgumentParser(
    prog = "schedule!",
    description = "Schedule Parser",
    conflict_handler = "resolve",
  )

  schedule_parser.add_argument(
    "-n", "--new",
    nargs = "+",
    type = str,
    help = """\
    An arugment to specify the name of the new event.
    Creates the specified event.
    
    Specifying -n / --new will omit -m / --event
    """,
  )

  schedule_parser.add_argument(
    "-x", "--delete",
    action = "store_true",
    help = """\
    If only an event name is supplied, adding this flag will \
    delete the specified event, given that it is specified by \
    the event maker or a schedule admin.
    If no event name is supplied, it defaults to the most recently created \
    event.
    
    If any additional information is given, all of the additional \
    information specified will be deleted from the event, but the \
    event will not be deleted.
    """,
  )

  schedule_parser.add_argument(
    "-i", "--info",
    nargs = "?",
    const = True,
    default = False,
    choices = ["all"],
    help = """\
    Gives information depending on supplied parameters. \
    If you supply just -i / --info without -m / --event, it will give \
    all the upcoming events. 
    If you specify an event, it will \
    give further information regarding the event.
    
    **Specifying -i / --info will make it ignore your -e / --todolist \
    and -u / --itemlist inputs.**
    """,
  )

  schedule_parser.add_argument(
    "-m", "--event",
    nargs = "+",
    type = str,
    help = """\
    An argument for to specify the event to be interacted with.
    """,
  )

  schedule_parser.add_argument(
    "-s", "--select_time",
    default = "now",
    nargs = 1,
    type = str,
    help = """\
    The selector lets you to select a specific event, given that there are multiple \
    events with the same name.
    It will try to find the event that is closest to the specified time.
    It prefers an earlier event, but it won't match with an event that already ended.

    Default is "now".
    """,

  )

  schedule_parser.add_argument(
    "-p", "--place",
    nargs = "+",
    type = str,
    help = """\
    An argument for where the event will occur.
    """,

  )

  schedule_parser.add_argument(
    "-d", "--description",
    nargs = "+",
    type = str,
    help = """An argument for more detailed specifics of the event.""",

  )

  schedule_parser.add_argument(
    "-e", "--todolist",
    action = "append",
    nargs = "+",
    type = str,
    help = """\
    Adds an entry to the todo list.
    You can specify multiple entries by repeatedly entering \
    -e / --todolist.
    """,
  )

  schedule_parser.add_argument(
    "-u", "--itemlist",
    action = "append",
    nargs = "+",
    type = str,
    help = """\
    Adds an item to the item list for the event.
    You can specify multiple items by repeatedly entering \
    -u / --itemlist.
    """,
  )



  schedule_parser.add_argument(
    "-t", "--time",
    default = ["now"],
    nargs = "*",
    action = required_length(0,2),
    type = str,
    help = """\
    Sets the time of the event.

    The time parsing is done using dateparser, so it will parse \
    things like "Tomorrow at 6".

    If you specify one time, that time is set to the start time \
    of the event.
    If you specify two times, the first is still set to the start time, \
    but the second time is set to the end time for the event and \
    the argument specified for -l / --length will be ignored.

    The default is 'now', which will auto set the time to the closest \
    quarter of the current hour that is coming up.
    """
  )

  schedule_parser.add_argument(
    "-l", "--length",
    default = "1h",
    nargs= "*",
    type = str,
    help = """\
    Sets the length of the event.
    The accepted format is *(int\{y,M,d,h,m\}), space seperated.
    For example, if you want an event of length 20 days 14 hours \
    and 3 miutes, enter -l 20d 14h 3m.

    The default length is 1 hours.

    If you specified 'allday', all measurements of time below \
    day is omitted.
    """
  )



  return schedule_parser

