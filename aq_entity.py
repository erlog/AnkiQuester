# -*- coding: utf-8 -*-
#This file is for defining various entity types in AQ.
#It might be necessary in the future to move Player/Monster to separate
#files after they become significantly more complicated or more content is added.

from aq_mathematics import *
import aq_event

class Entity:
	#Class for non-static, "thinking," residents of the dungeon including shopkeepers/monsters/etc.
	def __init__(self, glyph = "d"):
		self.HP = 10
		self.Strength = 10
		self.Speed = 10
		self.Luck = 10
		
		self.XP = 0
		self.Level = 1
		
		self.VisionRadius = 15
		
		self.Glyph = glyph
		
		self.X = 0
		self.Y = 0
	
	def UpdatePosition(self, destinationx, destinationy):
		#This function is for updating informational variables only.
		#Use of this function does not move the entity.
		self.X = destinationx
		self.Y = destinationy
	
	def __str__(self):
		#Warning: This str method could change as other UI methods are supported. 
		#For the time being it is serving as a stand-in for graphical tile information.
		return self.Glyph
		

class Monster(Entity):
	#Stub for monster class.
	def __init__(self, *args, **kwargs):
		Entity.__init__(self, *args, **kwargs)
	
	def ChasePlayer(self, player, floor):
		nextx, nexty = FindPath(floor, self.X, self.Y, player.X, player.Y)[0]
		floor.MoveEntity(self, self.X, self.Y, nextx, nexty)
		self.UpdatePosition(nextx, nexty)
			
			

class Player(Entity):
	#This class will handle player state information like equipment, inventory, available player verbs, etc.
	def __init__(self, *args, **kwargs):
		Entity.__init__(self, *args, **kwargs)
	
		self.Glyph = "@"
	
	def Attack(self, event):
		if event.EventDetails[0] == self:
			enemy = event.EventDetails[1]
			event.GameState.CurrentFloor.RemoveEntity(enemy)
			event.GameState.CurrentFloor.MoveEntity(self, self.X, self.Y, enemy.X, enemy.Y)
			self.UpdatePosition(enemy.X, enemy.Y)
			event.GameState.CurrentFloor.SpawnRandomEnemy()
		
	def EventListener(self, event):
		if event.EventType == aq_event.Attack.EventType:
			self.Attack(event)
		
	