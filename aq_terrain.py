# -*- coding: utf-8 -*-
import pdb

#AnkiQuester imports
from aq_mathematics import *
from aq_entity import *
import aq_event

class DungeonFloor:
	#This class holds information about the current floor including residents.
	def __init__(self, width = 5, height = 5, outdoor = False):
		self.Width = width
		self.Height = height
		
		#To-do: write a real level generator
		#self.Map = self.DummyMap(self.Width, self.Height, Tile)
		self.Map = self.MakeRoom(self.Width, self.Height)
		
		#We maintain a level-wide list of entities as well as a list of Entities on each tile.
		#This way we don't have to go searching the entire level for Entities.
		self.Entities = []
	
		self.FOVMult = [
					[1,  0,  0, -1, -1,  0,  0,  1],
					[0,  1, -1,  0,  0, -1,  1,  0],
					[0,  1,  1,  0,  0, -1, -1,  0],
					[1,  0,  0,  1, -1,  0,  0, -1]
				]
		
		#The below is a convenience function for debug purposes.
		self.SpawnRandomEnemy()
	
	def SpawnRandomEnemy(self):
		pos = self.RandomPosition()
		self.PutEntity(Rat(), pos[0], pos[1])

	def OutOfBoundsCheck(self, x, y):
		if (x < 0) or (y < 0) or (x > self.Width-1) or (y > self.Height-1):
			return True
		else:
			return False
	
	def ResetTileLights(self, status = False):
		[[tile.SetLit(status) for tile in row] for row in self.Map]	
	
	def SetTileLit(self, x, y, status = True):
		if status:
			self.Map[y][x].Lit = True
			self.Map[y][x].Seen = True
		else:
			self.Map[y][x].Lit = False
	
	def ComputeFOV(self, x, y, radius):
		#Calculate lit squares from the given location and radius.
		#The area around the player is split into 8 rectangular areas.
		#This convenience function uses math to compute the shape of each of these areas.
		for oct in range(8):
			Cast_Light(self, x, y, 1, 1.0, 0.0, radius,
							 self.FOVMult[0][oct], self.FOVMult[1][oct],
							 self.FOVMult[2][oct], self.FOVMult[3][oct], 0)
	
	def EventListener(self, event):
		for entity in self.Entities:
			entity.EventListener(event)
				
	def WallOrNot(self):
		#To-do: write real dungeon generation code in place of this
		x = RandomInteger(0,5)
		if x == 0: return Tile(".")
		elif x == 1: return Tile(".")
		elif x == 2: return Tile(".")
		elif x == 3: return Tile(".")
		elif x == 4: return Tile(".")
		elif x == 5: return Tile("O", True, True)
	
	def CollisionCheck(self, x, y):
		#Return False if nothing, True if something static,
		#and the list of Entities on the Tile in the case of 
		#something interactive.
		tile = self.GetTile(x, y)
		if not tile:
			return True
		elif tile.Entities: 
			return tile.Entities
		elif tile.Barrier: 
			return True
		else:
			return False
	
	def RandomPosition(self):
		return RandomInteger(0, self.Width-1), randint(0, self.Height-1)
	
	def GetTile(self, x, y):
		if self.OutOfBoundsCheck(x, y):
			return False
		else:
			return self.Map[y][x]
	
	def PutEntity(self, entity, x, y):
		self.Map[y][x].Entities.append(entity)
		self.Entities.append(entity)
		entity.UpdatePosition(x, y)
	
	def RemoveEntity(self, entity, x = None, y = None):
		if not x: x = entity.X
		if not y: y = entity.Y
		self.Map[y][x].Entities.remove(entity)
		self.Entities.remove(entity)
	
	def MoveEntity(self, entity, sourcex, sourcey, destinationx, destinationy):
		self.Map[sourcey][sourcex].Entities.remove(entity)
		self.Map[destinationy][destinationx].Entities.append(entity)
		entity.UpdatePosition(destinationx, destinationy)
	
	def PaddedSlice(self, top, bottom, left, right):
		toppadding, bottompadding, leftpadding, rightpadding = 0, 0, 0, 0

		if top < 0: toppadding = abs(top)
		if bottom > self.Height: bottompadding = abs(bottom - self.Height)
		if left < 0: leftpadding = abs(left)
		if right > self.Width: rightpadding = abs(right - self.Width)
		
		slicedmap = Slice2DArray(top, bottom, left, right, self.Map)

		return Pad2DArray(toppadding, bottompadding, leftpadding, rightpadding, slicedmap, Tile())
	
	def RenderSlice(self, top, bottom, left, right, playerx, playery, visionradius):
		self.ResetTileLights()
		self.SetTileLit(playerx, playery)
		self.ComputeFOV(playerx, playery, visionradius)
		return self.PaddedSlice(top, bottom, left, right)
	
	def DummyMap(self, width, height, dummyfunction):
		return [[dummyfunction() for x in range(width)] for y in range(height)]
	
	def MakeRoom(self, width, height, horizontal = chr(6), vertical = chr(5), topleftcorner = chr(1), toprightcorner = chr(2), bottomrightcorner = chr(4), bottomleftcorner = chr(3), blank = " "):
		top = [Tile(horizontal, True, True) for x in range(width)]
		top[0], top[-1] = Tile(topleftcorner, True, True), Tile(toprightcorner, True, True)
		
		bottom = [Tile(horizontal, True, True) for x in range(width)]
		bottom[0], bottom[-1] = Tile(bottomleftcorner, True, True), Tile(bottomrightcorner, True, True)

		box = [top] + [[Tile(vertical, True, True)] + [Tile(blank, False, False) for x in range(width-2)] + [Tile(vertical, True, True)] for y in range(height-2)] + [bottom]
		
		return box
		
	def InsertCellsInMap(self, destinationx, destinationy, cells):
		height = len(cells)
		width = len(cells[0])
		for y in range(height):
			for x in range(width):
				self.Map[destinationy + y][destinationx + x] = cells[y][x]
		
			

class Tile:
	#The tiles that make up our dungeon. This could be extended later to include other properties such as slippery ice or lakes.
	def __init__(self, glyph = " ", barrier = False, opaque = False):
		self.Glyph = glyph
		self.Barrier = barrier
		self.Opaque = opaque
		self.Lit = False
		self.Seen = False
		
		#We may at some point in the future allow multiple entities to share a tile.
		#Entity order on the tile matters, and the order is interpreted to be bottom->top.
		#These same rules apply for objects.
		self.Entities = []
		self.Objects = []
	
	def SetLit(self, status = True):
		self.Lit = status
	
	def __str__(self):
		#Warning: This str method could change as other UI methods are supported. 
		#For the time being it is serving as a stand-in for graphical tile information.
		
		#Entities > Objects > Terrain
		if self.Lit:
			if self.Entities:
				#Our last entity(the one on top) is the one we want displayed/is most important.
				return self.Entities[-1].Glyph
			elif self.Objects:		
				#Our last item(the one on top) is the one we want displayed/is most important.
				self.Objects[-1].Glyph
			else:
				return self.Glyph
				
		elif self.Seen and self.Barrier:
			return self.Glyph
		else:
			return " "