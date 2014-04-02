# -*- coding: utf-8 -*-
#This file is for containing logic for message display and logging.
#At this moment it's kind of a stub, but can be extended later in order to
#do things like cache out the message log to disk instead of cluttering up
#memory with it.

import aq_event

class MessageHandler:
	def __init__(self):
		self.Messages = []
		self.DoNotPrint = [aq_event.NextTurn.EventType]
	
	def EventListener(self, event):
		if event.EventType not in self.DoNotPrint:
			if event.EventDetails is not None:
				self.PostMessage(event.Message.format(**event.EventDetails))
			else:
				self.PostMessage(event.Message)
	
	def PostMessage(self, message):
		self.Messages.append(message)