# -*- coding: utf-8 -*-
#This file is for defining various entity types in AQ.
#It might be necessary in the future to move Player/Monster to separate
#files after they become significantly more complicated or more content is added.

class Entity:
	#Class for non-static, "thinking," residents of the dungeon including shopkeepers/monsters/etc.
	def __init__(self, glyph = "d"):
		self.HP = 10
		self.Strength = 10
		self.Speed = 10
		self.Luck = 10
		
		self.XP = 0
		self.Level = 1
		
		self.VisionRadius = 10
		
		self.Glyph = glyph
	
	def __str__(self):
		#Warning: This str method could change as other UI methods are supported. 
		#For the time being it is serving as a stand-in for graphical tile information.
		return self.Glyph

class Monster(Entity):
	#Stub for monster class
	def __init__(self, *args, **kwargs):
		Entity.__init__(self, *args, **kwargs)

class Player(Entity):
	#This class will handle player state information like equipment, inventory, available player verbs, etc.
	def __init__(self, *args, **kwargs):
		Entity.__init__(self, *args, **kwargs)
		
		self.Glyph = "@"
		self.X = 0
		self.Y = 0
		
	def UpdatePosition(self, destinationx, destinationy):
		self.X = destinationx
		self.Y = destinationy