# -*- coding: utf-8 -*-
#This file is for aggregating all types of events in AQ along with their details.
#Ideally, all event types should be laid out here so that, in the future, it will be
#easy for devs to implement event types or look at which ones exist.

#Event types are all instantiated at runtime, and then modified 
#with relevant information before being passed around. Placeholder strings
#for details define what kinds of information should be passed around with the event.

class AQEvent:
	def __init__(self, eventtype = None, details = ["No details"], state = None):
		self.EventType = eventtype
		self.EventDetails = details
		self.GameState = state
		self.FlashCardAnswer = None
	
	def EventWithGameState(self, state):
		self.GameState = state
		return self
	
	def EventWithDetailsAndGameState(self, details, state):
		self.EventDetails = details
		self.GameState = state
		return self

		
NextTurn = AQEvent(1)
PlayerMove = AQEvent(2)
Attack = AQEvent(3, ["ENTITY: aggressor", "ENTITY: defender"])
