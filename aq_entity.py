# -*- coding: utf-8 -*-
#This file is for defining various entity types in AQ.
#It might be necessary in the future to move Player/Monster to separate
#files after they become significantly more complicated or more content is added.

from aq_mathematics import *
import aq_event

class Entity:
	#Class for non-static, "thinking," residents of the dungeon including shopkeepers/monsters/etc.
	def __init__(self, glyph = "d"):
		self.HP = 32
		self.Strength = 5
		self.Speed = 2
		
		self.XP = 0
		self.Level = 1
		
		self.VisionRadius = 15
		
		self.Glyph = glyph
		self.Name = glyph
		
		self.X = 0
		self.Y = 0
		
	def EventListener(self, event):
		#Right now this is dummied out because I'm not sure exactly what kind of
		#default behavior I want inherited.
		pass
	
	def UpdatePosition(self, destinationx, destinationy):
		#This function is for keeping track of informational variables only.
		#Use of this function does not move the entity.
		self.X = destinationx
		self.Y = destinationy
	
	def RollAttack(self, event = None):
		#This may need to be moved into some kind of overarching class that governs
		#game rules, and interactions between entities.
		maximum = self.Strength * self.Speed
		return RandomInteger(maximum/3, maximum)
	
	def Defend(self, event):
		#Governs what happens when an entity receives damage.
		if event.EventDetails[1] == self:
				enemy = event.EventDetails[0]
				self.HP -= event.EventDetails[2]
				if self.HP <= 0:
					self.HP = 0
					self.Destroy(event)
				return self.HP
	
	def Destroy(self, event):
		event.GameState.CurrentFloor.RemoveEntity(self)
	
	def Status(self):
		#Convenience function mostly for debug.
		return self.HP, self.Strength, self.Speed, self.Luck, self.XP, self.Level
	
	def __str__(self):
		#Warning: This str method could change as other UI methods are supported. 
		#For the time being it's used as part of the message system.
		return self.Name
		

class Monster(Entity):
	def __init__(self, *args, **kwargs):
		Entity.__init__(self, *args, **kwargs)
	
	def ChasePlayer(self, event):
		#Default chase behavior is to attack the player or try to move closer in order to attack.
		player = event.GameState.Player
		
		if self.IsNextToPlayer(event):
			event.GameState.SendEventToListeners(aq_event.Attack.EventWithDetailsAndGameState( [self, player, self.RollAttack()], event.GameState))
		else:
			nextx, nexty = FindPath(event.GameState.CurrentFloor, self.X, self.Y, player.X, player.Y)[0]
			event.GameState.CurrentFloor.MoveEntity(self, self.X, self.Y, nextx, nexty)
			self.UpdatePosition(nextx, nexty)
		
	
	def IsNextToPlayer(self, event):
		#Offsets for adjacent tiles
		adjacenttiles =[(-1, -1), (-1,  0), (-1,  1), 
						(0,  -1), 			(0,   1), 
						(1,  -1), (1,   0),	(1,   1)]
		
		for tile in adjacenttiles:
			collisionresult = event.GameState.CurrentFloor.CollisionCheck(self.X+tile[0], self.Y+tile[1])
			if (collisionresult != True) and (collisionresult != False) and (collisionresult[0] == event.GameState.Player):
				return True
				
		return False
	
	def EventListener(self, event):
		if event.EventType == aq_event.Attack.EventType:
			self.Attack(event)
		elif event.EventType == aq_event.NextTurn.EventType:
			self.ChasePlayer(event)
		else:
			pass
	
	def Attack(self, event):
		if event.EventDetails[0] == self:
			enemy = event.EventDetails[1] #the player is the 'enemy' from the monster's perspective
			if enemy.Defend(event) == 0:
				event.GameState.CurrentFloor.MoveEntity(self, self.X, self.Y, enemy.X, enemy.Y)
				self.UpdatePosition(enemy.X, enemy.Y)
		
		return False

class Rat(Monster):
	#My first monster!
	def __init__(self, *args, **kwargs):
		Monster.__init__(self, *args, **kwargs)
		
		self.HP = RandomInteger(6, 13)
		self.Strength = RandomInteger(1, 2)
		self.Speed = RandomInteger(1, 2)
		
		self.Glyph = "r"
		self.Name = "rat"
			

class Player(Entity):
	#This class will handle player state information like equipment, inventory, available player verbs, etc.
	def __init__(self, *args, **kwargs):
		Entity.__init__(self, *args, **kwargs)
		
		self.HP = 32
		self.Strength = 5
		self.Speed = 2
	
		self.Glyph = "@"
		self.Name = "erlog"
	
	def Attack(self, event):
		if event.EventDetails[0] == self:
			enemy = event.EventDetails[1]
			if enemy.Defend(event) == 0:
				event.GameState.CurrentFloor.SpawnRandomEnemy() #<--this right here is some fucking bullshit that should be handled via proper messaging.
		
	def EventListener(self, event):
		if event.EventType == aq_event.Attack.EventType:
			self.Attack(event)
	
	def GiveXP(self, entity, xp):
		#To-do: allow for arbitrary experience curves that can change based on player class/race
		self.XP += xp
		while self.XP >= 2**self.Level*15:
			self.Level += 1