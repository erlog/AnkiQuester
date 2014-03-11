# -*- coding: utf-8 -*-

#AnkiQuester imports
from aq_strings import *

class AQEvent:
	def __init__(self, eventtype = None, details = None):
		self.Strings = AQ_Strings()
		self.EventType = eventtype
		self.EventDetails = details

		
NextTurn = AQEvent("NextTurn")
PlayerMove = AQEvent("PlayerMove")
