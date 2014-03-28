# -*- coding: utf-8 -*-

import aq_event

class MessageHandler:
	def __init__(self):
		self.Messages = []
		self.DoNotPrint = [aq_event.NextTurn.EventType]
	
	def EventListener(self, event):
		if event.EventType not in self.DoNotPrint:
			self.PostMessage(event.Message.format(event.EventDetails))
	
	def PostMessage(self, message):
		self.Messages.append(message)