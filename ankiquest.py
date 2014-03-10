# -*- coding: utf-8 -*-
#This file is for holding the overall game flow logic of AQ.
#Ideally, this file should resemble an uncomplicated and easy-to-read main loop for the game.

#Standard Library Imports
#from math import ceil

#AnkiQuester imports
from aq_entity import *
from aq_terrain import *
from aq_console_ui import *

class AnkiQuester:
	#The main loop and traffic cop for AQ. This class should be concerned only with keeping track
	#	of game state and providing communication between various classes that make up AQ.
	def __init__(self):
		self.CurrentFloor = DungeonFloor()
		self.Player = Player()
		
		self.AQAnswerResult = None
		self.Messages = []
		self.TurnCounter = 0
		
		self.SpawnEnemy()
		self.CurrentFloor.PutEntity(self.Player, self.Player.X, self.Player.Y)
	
	def PlayerMove(self, direction):
		#To-do: write a proper game rules class to handle the details of resolving collisions between entities.
		newx = self.Player.X
		newy = self.Player.Y
		
		if direction == "Up": newy -= 1
		elif direction == "Down": newy += 1
		elif direction == "Left": newx -= 1
		elif direction == "Right": newx += 1
		elif direction == "Rest": pass

		collisioncheck = self.CurrentFloor.CollisionCheck(newx, newy)
		
		if collisioncheck == False:
			self.CurrentFloor.MoveEntity(self.Player, self.Player.X, self.Player.Y, newx, newy)
			self.Player.UpdatePosition(newx, newy)
			self.NextTurn()
	
	def NextTurn(self):
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
	
	def DoFlashcard(self, debug):
		#This is our single handler for flashcard data. 
		#Nowhere else should ever try to do anything with flashcards.
		#The idea is that if we can easily dummy this function out for an Anki-less experience.
		#To-do: Fix this hook. It was broken when we moved from libtcod to Qt.
		if debug:
			return 2
		else:
			self.AQAnswerResult = None
			AQIOController.FocusAnki()
			
			while self.AQAnswerResult == None:
				AQIOController.PauseForReview(AQGameInstance)
				
			AQIOController.FocusGame()
			return self.AQAnswerResult


			