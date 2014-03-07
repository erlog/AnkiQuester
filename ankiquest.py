# -*- coding: utf-8 -*-

#Standard Library Imports
from random import randint
from os import linesep
from math import ceil
string = ""

#AnkiQuester imports
from aq_strings import *

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
			self.Messages.append(self.Strings.LevelUpMessage.format(entity.Level))
	
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

class ConsoleUserInterface:
	def __init__(self, state, screenwidth = 80, screenheight = 40, statuswidth = 15, msgheight = 6):
		#Right now our status area is on the right side of the screen with our message window across the bottom.
		#The math is done in this init function so that later the heights and widths can be user-specified
		
		self.ScreenWidth = screenwidth
		self.ScreenHeight = screenheight
		
		self.StatusWidth = statuswidth
		self.StatusHeight = self.ScreenHeight
		
		self.MsgHeight = msgheight
		self.MsgWidth = self.ScreenWidth - self.StatusWidth
		
		self.DungeonWidth = self.ScreenWidth - self.StatusWidth
		self.DungeonHeight = self.ScreenHeight - self.MsgHeight
		
		self.GameState = state
		self.Strings = AQ_Strings()
	
	def RenderScreen(self):
		#Take lists of lines for each screen portion and munge them together into a layout.
		#This is the only function that should ever be messing with line separators.
		#To-do: Support user-definable and arbitrary window layouts.
		
		dungeonlines = self.DungeonWindow()
		statuslines = self.StatusWindowItems()
		
		for index in range(len(statuslines)):
			dungeonlines[index] = dungeonlines[index] + statuslines[index]
			
		messagelines = self.MessageWindow(self.MsgHeight)
		
		return linesep.join(dungeonlines + messagelines)
	
	def DungeonWindow(self):
		#Right now our tile is deciding by itself what kind of representation to give us via logic in the str method.
		#This could be made more extensible in a graphical version later, but is fine as it is for a console version.
		dungeontiles = self.GameState.CurrentFloor.PaddedSlice((self.GameState.Player.Y - self.DungeonHeight/2), 
														(self.GameState.Player.Y + self.DungeonHeight/2),
														(self.GameState.Player.X - self.DungeonWidth/2),
														(self.GameState.Player.X + self.DungeonWidth/2))
		
		lines = []
		for row in dungeontiles:
			lines.append(string.join([str(tile) for tile in row]))
			
		return lines
	
	def MessageWindow(self, linecount):
		#To-do: support for user-definable formatting of the MessageWindow.
		#	Ideally users should be able to filter kinds of messages they receive in a granular fashion to prevent spam.
		linecount -= 1
		label = self.Strings.MessageWindowLabel
		if len(self.GameState.Messages) <= linecount: 
			return [label] + [(" "+line) for line in self.GameState.Messages]
		else:
			return [label] + [(" "+line) for line in self.GameState.Messages[-1*linecount:]]
	
	def StatusWindowItems(self):
		#To-do: support for user-definable formatting of the Status window via something like lua.
		#		This should include robust support for what kind of data to display.
		
		items = [self.Strings.StatusWindowLabel]
		
		#Blank items result in a blank line. Non-blank items map to dictionary keys in Player.Stats
		displayedstats = [  
							[self.Strings.HP, self.GameState.Player.HP],
							[self.Strings.Strength, self.GameState.Player.Strength], 
							[self.Strings.Speed, self.GameState.Player.Speed],
							[self.Strings.Luck, self.GameState.Player.Luck],
							[],
							[self.Strings.Level, self.GameState.Player.Level],
							[self.Strings.XP, self.GameState.Player.XP],
							[],
							[self.Strings.Turn, self.GameState.TurnCounter],
						]
		
		for line in displayedstats:
			if line:
				items.append(" {0}: {1}".format(line[0], line[1]))
			else:
				items.append("")
		
		return items
	
			


class DungeonFloor:
	#This class holds our information about the current floor including residents.
	def __init__(self, width = 25, height = 25):
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

	def SetLit(self, x, y):
		self.Map[y][x].Lit = True
	
	def ComputeFOV(self, x, y, radius):
		#"Calculate lit squares from the given location and radius"
		for oct in range(8):
			self._Cast_Light(x, y, 1, 1.0, 0.0, radius,
							 self.FOVMult[0][oct], self.FOVMult[1][oct],
							 self.FOVMult[2][oct], self.FOVMult[3][oct], 0)

			
	def _Cast_Light(self, cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
		#"Recursive lightcasting function"
		if start < end:
			return
		radius_squared = radius*radius
		for j in range(row, radius+1):
			dx, dy = -j-1, -j
			blocked = False
			while dx <= 0:
				dx += 1
				# Translate the dx, dy coordinates into map coordinates:
				X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
				# l_slope and r_slope store the slopes of the left and right
				# extremities of the square we're considering:
				l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
				if start < r_slope:
					continue
				elif end > l_slope:
					break
				else:
					# Our light beam is touching this square; light it:
					if dx*dx + dy*dy < radius_squared:
						self.set_lit(X, Y)
					if blocked:
						# we're scanning a row of blocked squares:
						if self.blocked(X, Y):
							new_start = r_slope
							continue
						else:
							blocked = False
							start = new_start
					else:
						if self.blocked(X, Y) and j < radius:
							# This is a blocking square, start a child scan:
							blocked = True
							self._cast_light(cx, cy, j+1, start, l_slope,
											 radius, xx, xy, yx, yy, id+1)
							new_start = r_slope
			# Row is scanned; do next row unless last square was blocked:
			if blocked:
				break
				
	def WallOrNot(self):
		#To-do: write real dungeon generation code in place of this
		x = randint(0,4)
		if x == 0: return Tile(".")
		elif x == 1: return Tile(" ")
		elif x == 2: return Tile("'")
		elif x == 3: return Tile(" ")
		elif x == 4: return Tile("O", True, True)
	
	def CollisionCheck(self, x, y):
		#Simple bounds check on the values
		if (x < 0) or (y < 0) or (x > self.Width-1) or (y > self.Height-1):
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
		return randint(0, self.Width-1), randint(0, self.Height-1)
	
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
		
	def Slice2DArray(self, top, bottom, left, right, array):
		#To-do: There's no reason for this to be a method of this class.
		#		This should be moved to a separate math library so that future optimizations,
		#		such as NumPy support, can be easily added.
		
		arrayheight = len(array)
		arraywidth = len(array[0])
		
		if top < 0: 
			top = 0
		if bottom > arrayheight: 
			bottom = arrayheight
		if left < 0: 
			left = 0
		if right > arraywidth: 
			right = arraywidth
	
		return [row[left:right] for row in array[top:bottom]]
	
	def Pad2DArray(self, toppadding, bottompadding, leftpadding, rightpadding, array, paddingobject):
		#To-do: There's no reason for this to be a method of this class.
		#		This should be moved to a separate math library so that future optimizations,
		#		such as NumPy support, can be easily added.
		emptyrow = [paddingobject for x in range(leftpadding + len(array[0]) + rightpadding)]
		leftpad = [paddingobject for x in range(leftpadding)]
		rightpad = [paddingobject for x in range(rightpadding)]
		
		paddedrows = [emptyrow for x in range(toppadding)]
		
		for row in array:
			paddedrows.append(leftpad + row + rightpad)
			
		paddedrows += [emptyrow for x in range(bottompadding)]
		
		return paddedrows
	
	def PaddedSlice(self, top, bottom, left, right):
		toppadding = 0
		bottompadding = 0
		leftpadding = 0
		rightpadding = 0
		
		if top < 0: toppadding = abs(top)
		if bottom > self.Height: bottompadding = abs(bottom - self.Height)
		if left < 0: leftpadding = abs(left)
		if right > self.Width: rightpadding = abs(right - self.Width)
		
		slicedmap = self.Slice2DArray(top, bottom, left, right, self.Map)

		return self.Pad2DArray(toppadding, bottompadding, leftpadding, rightpadding, slicedmap, Tile())

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
	
	def __str__(self):
		#Warning: This str method could change as other UI methods are supported. 
		#For the time being it is serving as a stand-in for graphical tile information.
		
		#Entities > Objects > Terrain
		if self.Entities:
			#Our last entity(the one on top) is the one we want displayed/is most important.
			return self.Entities[-1].Glyph
		elif self.Objects:		
			#Our last item(the one on top) is the one we want displayed/is most important.
			self.Objects[-1].Glyph
		else:
			return self.Glyph

class Entity:
	#Class for non-static, "thinking," residents of the dungeon including shopkeepers/monsters/etc.
	def __init__(self, glyph = "d"):
		self.HP = 10
		self.Strength = 10
		self.Speed = 10
		self.Luck = 10
		
		self.XP = 0
		self.Level = 1
		
		self.VisionRadius = 3
		
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
			