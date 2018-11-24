# Community_Bot

Community bot is a (currently planned to be) discord bot that aims to help make organizing a channel much easier.

It will use argparse to do all the parsing, which will make interacting with it easier.

## Dependencies:
iCalendar (https://github.com/collective/icalendar)
* This is not necessary, but if you want to be able to export the generated schedule, then it is needed

DateParser

PyTimeParse

## Under works:
* Survey Module (Mostly done)
* Scheduler Module (Under works)

## Things that need to be done:
* Mongo DB integration (Done)
* Output certain results to Google Sheets (may end up displaying information elsewhere) (Put on hold)
* Make the scheduler module output urls that will send .ics files for members to keep track of events (Under works)
* Create setup.py file for installing dependencies
* Make the bot work without the need to type in commands using NLP