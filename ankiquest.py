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
import aq_event;

class AnkiQuester:
	#The main loop and traffic cop for AQ. This class should be concerned only with keeping track
	#	of game state and providing communication between various classes that make up AQ.
	def __init__(self, ankiwindow = None, debug = True):
		self.CurrentFloor = DungeonFloor(30, 30)
		self.Player = Player()
		self.Strings = AQ_Strings()
		self.EventListeners = [self.Player, self.CurrentFloor] #Event stuff is profoundly poorly implemented right now
		
		self.NewX = None #this is proof of concept stuff that should be moved into a real event system
		self.NewY = None #this is proof of concept stuff that should be moved into a real event system
		self.AttackedEntity = None #this is proof of concept stuff that should be moved into a real event system
		
		self.WaitingForFlashcard = False
		
		self.AQDebug = debug
		self.AnkiWindow = ankiwindow
		
		self.Messages = []
		self.TurnCounter = 0
		
		self.SpawnEnemy()
		self.SpawnEnemy()
		self.SpawnEnemy()
		self.SpawnEnemy()
		self.CurrentFloor.PutEntity(self.Player, self.Player.X, self.Player.Y)
	
	def SendEventToListeners(self, event = None):
		#Event stuff is profoundly poorly implemented right now
		for listener in self.EventListeners:
			listener.EventListener(event)
	
	def PlayerMove(self, direction):
		if self.WaitingForFlashcard == True:
			self.Messages.append(self.Strings.WaitingForFlashcard)
			return
		
		#To-do: write a proper game rules class to handle the details of resolving collisions between entities.
		newx = self.Player.X
		newy = self.Player.Y
		
		if direction == "Up": newy -= 1
		elif direction == "Down": newy += 1
		elif direction == "Left": newx -= 1
		elif direction == "Right": newx += 1
		elif direction == "Rest": pass

		collisioncheck = self.CurrentFloor.CollisionCheck(newx, newy)
		
		if collisioncheck == True:
			return
		elif collisioncheck == False:
			self.CurrentFloor.MoveEntity(self.Player, self.Player.X, self.Player.Y, newx, newy)
			self.Player.UpdatePosition(newx, newy)
			self.NextTurn()
		elif isinstance(collisioncheck[0], Entity):
			#If we run into an Entity then we want to throw the flashcard up for the user. So we save
			#a little bit of information so that we can respond to their answer. In the future there 
			#will be a property event system that will help keep track of game state and consequences 
			#for flashcard answers.
			
			self.AttackedEntity = collisioncheck[0]
			self.NewX = newx
			self.NewY = newy
			self.DoFlashcard()
			if self.AQDebug:
				self.ReceiveFlashcardAnswer(RandomInteger(1,2))
			
	
	def NextTurn(self):
		for entity in self.CurrentFloor.Entities:
			if isinstance(entity, Monster):
				entity.ChasePlayer(self.Player, self.CurrentFloor)
		
		self.TurnCounter += 1
	
	def GiveXP(self, entity, xp):
		#To-do: allow for arbitrary experience curves that can change based on player class/race
		entity.XP += xp
		while entity.XP >= 2**entity.Level*15:
			entity.Level += 1
	
	def SpawnEnemy(self):
		#This is a stub function that should eventually be deleted or handled by DungeonFloor.
		position = self.CurrentFloor.RandomTile()
		self.CurrentFloor.PutEntity(Monster(), position[0], position[1])
	
	def DoFlashcard(self):
		#This is our single handler for flashcard data. 
		#Nowhere else should ever try to do anything with flashcards.
		#The idea is that if we can easily dummy this function out for an Anki-less experience.
		#To-do: Fix this hook. It was broken when we moved from libtcod to Qt.
		self.WaitingForFlashcard = True
		
		if not self.AQDebug:
			self.AnkiWindow.activateWindow()
			
	def ReceiveFlashcardAnswer(self, answer):
		#This function right now is designed for a kind of simple combat scenario where enemies die in 1 hit
		#if the player gets the question correct. This is proof of concept code that should be replaced by a
		#proper event system that will make it easier to manage game state and card consequences.
	
		self.WaitingForFlashcard = False
		
		if answer > 1:
			self.CurrentFloor.RemoveEntity(self.AttackedEntity, self.NewX, self.NewY)
			self.Messages.append(self.Strings.EnemyKilled)
			self.CurrentFloor.MoveEntity(self.Player, self.Player.X, self.Player.Y, self.NewX, self.NewY)
			self.Player.UpdatePosition(self.NewX, self.NewY)
			
			self.AttackedEntity = None
			self.NewX = None
			self.NewY = None
			
			self.NextTurn()
		else:
			self.Messages.append(self.Strings.Missed)
		

			