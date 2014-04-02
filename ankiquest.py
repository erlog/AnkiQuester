# -*- coding: utf-8 -*-
#This file is for holding the overall game flow logic of AQ.
#Ideally, this file should resemble an uncomplicated and easy-to-read main loop for the game.

#Standard Library Imports
#from math import ceil

#AnkiQuester imports
from aq_entity import *
from aq_terrain import *
from aq_console_ui import *
from aq_strings import *
from aq_mathematics import *
from aq_messagehandler import *
import aq_event;



class AnkiQuester:
	#The main loop and traffic cop for AQ. This class should be concerned only with keeping track
	#	of game state and providing communication between various classes that make up AQ.
	def __init__(self, ankiwindow = None, debug = True):
		self.CurrentFloor = DungeonFloor(20, 20)
		self.Player = Player()
		self.Strings = AQ_Strings()
		self.MessageHandler = MessageHandler()
		self.EventListeners = [self.CurrentFloor, self.MessageHandler]
	
		self.PendingEvent = None
		self.WaitingForFlashcard = False
		
		self.AQDebug = debug
		self.AnkiWindow = ankiwindow
		
		self.CurrentTurn = 0
	
		self.Player.UpdatePosition(3,3)
		self.CurrentFloor.PutEntity(self.Player, self.Player.X, self.Player.Y)
	
	def SendEventToListeners(self, event):
		for listener in self.EventListeners:
			listener.EventListener(event)
		
		#Clear the event to prevent it from being sent twice accidentally.
		event.EventDetails = None
		
	
	def PlayerMove(self, direction):
		if self.WaitingForFlashcard == True:
			self.MessageHandler.PostMessage(self.Strings.WaitingForFlashcard)
			return
		
		#To-do: write a proper game rules class to handle the details of resolving collisions between entities.
		newx, newy = self.Player.X, self.Player.Y
		
		if direction == "Up": newy -= 1
		elif direction == "Down": newy += 1
		elif direction == "Left": newx -= 1
		elif direction == "Right": newx += 1
		elif direction == "UpLeft": 
			newx -= 1
			newy -= 1
		elif direction == "UpRight":
			newx += 1
			newy -= 1
		elif direction == "DownLeft":
			newx -= 1
			newy += 1
		elif direction == "DownRight":
			newx += 1
			newy += 1
		elif direction == "Rest": 
			self.NextTurn()
			return
			
		self.SendEventToListeners(aq_event.EntityMove.EventWithDetailsAndGameState({"Entity" : self.Player, "DestinationXY" : (newx, newy)}, self))
		self.NextTurn()
	
	def NextTurn(self):
		self.CurrentTurn += 1
		self.SendEventToListeners(aq_event.NextTurn.EventWithDetailsAndGameState({"CurrentTurn" : self.CurrentTurn}, self))
	
	def DoFlashcard(self, event):
		self.PendingEvent = event
		self.WaitingForFlashcard = True
		if not self.AQDebug:
			self.AnkiWindow.activateWindow()
			
	def ReceiveFlashcardAnswer(self, answer):
		self.WaitingForFlashcard = False
		self.PendingEvent.FlashCardAnswer = answer
		self.SendEventToListeners(self.PendingEvent)
		self.PendingEvent = None
		

			