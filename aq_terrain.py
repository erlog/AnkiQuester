# -*- coding: utf-8 -*-

#AnkiQuester imports
from aq_mathematics import *

class DungeonFloor:
	#This class holds our information about the current floor including residents.
	def __init__(self, width = 100, height = 100):
		self.Width = width
		self.Height = height
		
		#To-do: make this extensible via inheritance to be able to generate different kinds of dungeon floors
		self.Map = [[self.WallOrNot() for x in range(self.Width)] for y in range(self.Height)]
		
		#We maintain a level-wide list of entities as well as a list of Entities on each tile.
		#Except for the player, I don't want entities in the dungeon to ever be thinking in terms of their X/Y position.
		#This may need to be refactored later because it could be, like, the worst idea.
		self.Entities = []
	
		self.FOVMult = [
					[1,  0,  0, -1, -1,  0,  0,  1],
					[0,  1, -1,  0,  0, -1,  1,  0],
					[0,  1,  1,  0,  0, -1, -1,  0],
					[1,  0,  0,  1, -1,  0,  0, -1]
				]

	def OutOfBoundsCheck(self, x, y):
		if (x < 0) or (y < 0) or (x > self.Width-1) or (y > self.Height-1):
			return True
	
	def ResetLitTiles(self):
		[[tile.ResetLight() for tile in row] for row in self.Map]			
	
	def SetLit(self, x, y):
		self.Map[y][x].Lit = True
		self.Map[y][x].Seen = True
	
	def SetUnlit(self, x, y):
		self.Map[y][x].Lit = False
	
	def ComputeFOV(self, x, y, radius):
		#Calculate lit squares from the given location and radius.
		#The area around the player is split into 8 rectangular areas.
		#This convenience function uses math to compute the shape of each of these areas.
		for oct in range(8):
			self._Cast_Light(x, y, 1, 1.0, 0.0, radius,
							 self.FOVMult[0][oct], self.FOVMult[1][oct],
							 self.FOVMult[2][oct], self.FOVMult[3][oct], 0)

			
	def _Cast_Light(self, cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
		#Recursive lightcasting function.
		#To-do: clean up and comment this super-terse code.
		#To-do: make light have some amount of bounce/sticky nature to make it less flickery in areas with lots of obstructions.
		if start < end:
			return
			
		radius_squared = radius**2
		
		for j in range(row, radius+1):
			
			dx = -j-1
			dy = -j
			
			blocked = False
			
			while dx <= 0:
				dx += 1
				# Translate the dx, dy coordinates into map coordinates:
				X = cx + dx * xx + dy * xy
				Y = cy + dx * yx + dy * yy
				
				# l_slope and r_slope store the slopes of the left and right extremities of the square we're considering:
				l_slope = (dx-0.5)/(dy+0.5)
				r_slope = (dx+0.5)/(dy-0.5)
				
				if start < r_slope:
					continue
					
				elif end > l_slope:
					break
					
				else:
					# Our light beam is touching this square; light it:
					if not self.OutOfBoundsCheck(X, Y) and (dx*dx + dy*dy < radius_squared):
						self.SetLit(X, Y)
						
					if blocked:
						# we're scanning a row of blocked squares:
						if self.OutOfBoundsCheck(X, Y) or self.GetTile(X, Y).Opaque:
							new_start = r_slope
							continue
						else:
							blocked = False
							start = new_start
					else:
						if (self.OutOfBoundsCheck(X, Y) or self.GetTile(X, Y).Opaque) and j < radius:
							# This is a blocking square, start a child scan:
							blocked = True
							self._Cast_Light(cx, cy, j+1, start, l_slope,
											 radius, xx, xy, yx, yy, id+1)
							new_start = r_slope
							
			# Row is scanned; do next row unless last square was blocked:
			if blocked:
				break
				
	def WallOrNot(self):
		#To-do: write real dungeon generation code in place of this
		x = RandomInteger(0,4)
		if x == 0: return Tile(".")
		elif x == 1: return Tile(".")
		elif x == 2: return Tile(".")
		elif x == 3: return Tile(".")
		elif x == 4: return Tile("O", True, True)
	
	def CollisionCheck(self, x, y):
		if self.OutOfBoundsCheck(x, y):
			return True
			
		#Return False if nothing, True if something static, and the list of Entities on the Tile in the case of something interactive.
		tile = self.GetTile(x, y)
		if tile.Entities: 
			return tile.Entities
		elif tile.Barrier: 
			return True
		else:
			return False
	
	def RandomTile(self):
		return RandomInteger(0, self.Width-1), randint(0, self.Height-1)
	
	def GetTile(self, x, y):
		return self.Map[y][x]
	
	def PutEntity(self, entity, x, y):
		self.Map[y][x].Entities.append(entity)
		self.Entities.append(entity)
	
	def RemoveEntity(self, entity, x, y):
		self.Map[y][x].Entities.remove(entity)
		self.Entities.remove(entity)
	
	def MoveEntity(self, entity, sourcex, sourcey, destinationx, destinationy):
		self.Map[sourcey][sourcex].Entities.remove(entity)
		self.Map[destinationy][destinationx].Entities.append(entity)
	
	def PaddedSlice(self, top, bottom, left, right):
		toppadding = 0
		bottompadding = 0
		leftpadding = 0
		rightpadding = 0
		
		if top < 0: toppadding = abs(top)
		if bottom > self.Height: bottompadding = abs(bottom - self.Height)
		if left < 0: leftpadding = abs(left)
		if right > self.Width: rightpadding = abs(right - self.Width)
		
		slicedmap = Slice2DArray(top, bottom, left, right, self.Map)

		return Pad2DArray(toppadding, bottompadding, leftpadding, rightpadding, slicedmap, Tile())
	
	def RenderSlice(self, top, bottom, left, right, playerx, playery, visionradius):
		self.ResetLitTiles()
		self.SetLit(playerx, playery)
		self.ComputeFOV(playerx, playery, visionradius)
		return self.PaddedSlice(top, bottom, left, right)

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
	
	def ResetLight(self):
		self.Lit = False
	
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