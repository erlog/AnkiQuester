# -*- coding: utf-8 -*-
from random import randint
from os import linesep
from math import ceil

class AnkiQuester:
	def __init__(self):
		self.CurrentFloor = DungeonFloor()
		
		#To-do: Write a proper Player class instead of using a simple Entity
		self.Player = Entity()
		self.PlayerX = 0
		self.PlayerY = 0
		
		self.AQAnswerResult = None
		self.Messages = []
		self.TurnCounter = 0
		
		self.SpawnEnemy()
		self.CurrentFloor.PutEntity(self.Player, self.PlayerX, self.PlayerY)
	
	def PlayerMove(self, direction):
		#Movement code is mostly fine here, but the collision code should be more pass through
		#	style in order to allow collisions to resolve between entities.
		newx = self.PlayerX
		newy = self.PlayerY
		
		if direction == "Up": newy -= 1
		elif direction == "Down": newy += 1
		elif direction == "Left": newx -= 1
		elif direction == "Right": newx += 1
		elif direction == "Rest": pass

		collisioncheck = self.CurrentFloor.CollisionCheck(newx, newy)
		
		if collisioncheck == False:
			self.CurrentFloor.RemoveEntity(self.Player, self.PlayerX, self.PlayerY)
			self.PlayerX = newx
			self.PlayerY = newy
			self.CurrentFloor.PutEntity(self.Player, self.PlayerX, self.PlayerY)

	
	def GiveXP(self, entity, xp):
		#To-do: allow for arbitrary experience curves that can change based on player class/race
		entity.Stats["XP"] += xp
		while entity.Stats["XP"] >= 2**entity.Stats["Level"]*15:
			entity.Stats["Level"] += 1
			self.Messages.append("Level up! Welcome to Level {0}!".format(entity.Stats["Level"]))
	
	def SpawnEnemy(self):
		#This is a convenience function mostly for testing
		position = self.CurrentFloor.RandomTile()
		self.CurrentFloor.PutEntity(Entity(None, "d"), position[0], position[1])
	
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
		dungeontiles = self.GameState.CurrentFloor.PaddedSlice((self.GameState.PlayerY - self.DungeonHeight/2), 
														(self.GameState.PlayerY + self.DungeonHeight/2),
														(self.GameState.PlayerX - self.DungeonWidth/2),
														(self.GameState.PlayerX + self.DungeonWidth/2))
		
		lines = []
		for row in dungeontiles:
			lines.append("".join([str(tile) for tile in row]))
			
		return lines
	
	def MessageWindow(self, linecount):
		#To-do: support for user-definable formatting of the MessageWindow
		linecount -= 1
		label = "MESSAGES:"
		if len(self.GameState.Messages) <= linecount: 
			return [label] + [(" "+line) for line in self.GameState.Messages]
		else:
			return [label] + [(" "+line) for line in self.GameState.Messages[-1*linecount:]]
	
	def StatusWindowItems(self):
		#To-do: support for user-definable formatting of the Status window.
		#		This should include robust support for what kind of data to display.
		
		items = ["STATUS:"]
		
		#Blank items result in a blank line.
		displayedstats = ["HP", "Strength", "Speed", "", "Level", "XP"]
		
		for key in displayedstats:
			if key in self.GameState.Player.Stats:
				items.append(" {0}: {1}".format(key, self.GameState.Player.Stats[key]))
			else:
				items.append("".center(self.StatusWidth))
		return items
	
			


class DungeonFloor:
	def __init__(self, width = 25, height = 25):
		self.Width = width
		self.Height = height
		
		#To-do: make this extensible via inheritance to be able to generate different kinds of dungeon floors
		self.Map = [[self.WallOrNot() for x in range(self.Width)] for y in range(self.Height)]
				
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
	
	def RemoveEntity(self, entity, x, y):
		self.Map[y][x].Entities.remove(entity)
		
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
	def __init__(self, glyph = " ", barrier = False, opaque = False):
		self.Glyph = glyph
		self.Barrier = barrier
		self.Opaque = opaque
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
	def __init__(self, initstats = None, tile = "@"):
		if not initstats:
			#a dictionary might be a bad way to do stats, but I'm uncertain as of yet
			self.Stats = {"HP": 10, "Strength": 10, "Speed": 100, "Luck": 10, "XP": 0, "Level": 1}
		else:
			self.Stats = initstats

		self.Glyph = tile
		self.VisionRadius = 3
	
	def __str__(self):
		#Warning: This str method could change as other UI methods are supported. 
		#For the time being it is serving as a stand-in for graphical tile information.
		return self.Glyph
