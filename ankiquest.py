# -*- coding: utf-8 -*-

import os, sys, random, pdb
from math import ceil
from PyQt4 import QtGui, QtCore


#Check to see if we're running inside Anki, and load appropriate Anki libraries
try:
	from aqt import mw
	from aqt.utils import showInfo
	from aqt.qt import *
	from aqt import forms
	from anki.hooks import wrap
	AQ_PATH = os.path.normpath(os.path.join(mw.pm.addonFolder().encode(sys.getfilesystemencoding()), "ankiquester/"))
	AQ_DEBUG = False
except ImportError:
	AQ_DEBUG = True
	AQ_PATH = os.path.abspath(os.curdir)

	def qt_trace(self=None):
		QtCore.pyqtRemoveInputHook()
		pdb.set_trace()
		
def anki_quester():
	pass

def catch_answer(ease):
	if mw.reviewer.state == "answer":
		AQGameInstance.AQAnswerResult = ease
	OLD_answerCard(ease)

if not AQ_DEBUG:
	#If we're in Anki then we add the AQ menu item and clone _answerCard for later
	action = QAction("AnkiQuest", mw)
	mw.connect(action, SIGNAL("triggered()"), anki_quester)
	mw.form.menuTools.addAction(action)
	OLD_answerCard = mw.reviewer._answerCard
	
	
class AnkiQuester:
	def __init__(self):
		self.CurrentFloor = DungeonFloor()
		self.Player = Entity()
		self.PlayerX = 0
		self.PlayerY = 0
		self.AQAnswerResult = None
		self.Messages = []
		self.TurnCounter = 0
		self.SpawnEnemy()
		self.CurrentFloor.PutEntity(self.Player, self.PlayerX, self.PlayerY)
	
	def PlayerMove(self, direction):
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
		entity.Stats["XP"] += xp
		while entity.Stats["XP"] >= 2**entity.Stats["Level"]*15:
			entity.Stats["Level"] += 1
			self.Messages.append("Level up! Welcome to Level {0}!".format(entity.Stats["Level"]))
	
	def SpawnEnemy(self):
		position = self.CurrentFloor.RandomTile()
		self.CurrentFloor.PutEntity(Entity(None, "d"), position[0], position[1])
	
	def DoFlashcard(self):
		if AQ_DEBUG:
			return 2
		else:
			self.AQAnswerResult = None
			AQIOController.FocusAnki()
			
			while self.AQAnswerResult == None:
				AQIOController.PauseForReview(AQGameInstance)
				
			AQIOController.FocusGame()
			return self.AQAnswerResult

class UserInterface:
	def __init__(self, state, screenwidth = 80, screenheight = 40, statuswidth = 15, msgheight = 6):
		#Right now our status area is on the right side of the screen with our message window across the bottom.
		#The math is done in this init function so that later the heights and widths can be user-specified
		#To-do: more robust placement options for status and message areas
		
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
		dungeonlines = self.GameState.CurrentFloor.RenderFloor((self.GameState.PlayerY - self.DungeonHeight/2), 
														(self.GameState.PlayerY + self.DungeonHeight/2),
														(self.GameState.PlayerX - self.DungeonWidth/2),
														(self.GameState.PlayerX + self.DungeonWidth/2))

		statuslines = self.StatusWindowItems()
		
		for index in range(len(statuslines)):
			dungeonlines[index] = dungeonlines[index] + statuslines[index]
			
		messagelines = self.MessageWindow(self.MsgHeight)
		
		return os.linesep.join(dungeonlines + messagelines)
	
	def MessageWindow(self, linecount):
		linecount -= 1
		label = "MESSAGES:"
		if len(self.GameState.Messages) <= linecount: 
			return [label] + [(" "+line) for line in self.GameState.Messages]
		else:
			return [label] + [(" "+line) for line in self.GameState.Messages[-1*linecount:]]
	
	def StatusWindowItems(self):
		items = ["STATUS:"]
		for key in self.GameState.Player.DisplayedStats:
			if key in self.GameState.Player.Stats:
				items.append(" {0}: {1}".format(key, self.GameState.Player.Stats[key]))
			else:
				"".center(self.StatusWidth)
		return items
	
			


class DungeonFloor:
	def __init__(self, width = 100, height = 100):
		self.Width = width
		self.Height = height
		self.Map = [[self.WallOrNot() for x in range(self.Width)] for y in range(self.Height)]
				
	def WallOrNot(self):
		x = random.randint(0,3)
		if x == 0: return Tile(" ")
		elif x == 1: return Tile(" ")
		elif x == 2: return Tile(" ")
		elif x == 3: return Tile("O", True, True)
	
	def CollisionCheck(self, x, y):
		tile = self.GetTile(x, y)
		if tile.Entities: 
			return tile.Entities
		elif tile.Barrier: 
			return True
		else:
			return False
	
	def RandomTile(self):
		return random.randint(0, self.Width-1), random.randint(0, self.Height-1)
	
	def GetTile(self, x, y):
		return self.Map[y][x]
	
	def PutEntity(self, entity, x, y):
		self.Map[y][x].Entities.append(entity)
	
	def RemoveEntity(self, entity, x, y):
		self.Map[y][x].Entities.remove(entity)
		
	def Slice2DArray(self, top, bottom, left, right, array):
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
		emptyrow = [paddingobject for x in range(leftpadding + len(array[0]) + rightpadding)]
		leftpad = [paddingobject for x in range(leftpadding)]
		rightpad = [paddingobject for x in range(rightpadding)]
		
		paddedrows = [emptyrow for x in range(toppadding)]
		
		for row in array:
			paddedrows.append(leftpad + row + rightpad)
			
		paddedrows += [emptyrow for x in range(bottompadding)]
		
		return paddedrows
	
	def RenderFloor(self, top, bottom, left, right):
		toppadding = 0
		bottompadding = 0
		leftpadding = 0
		rightpadding = 0
		
		if top < 0: toppadding = abs(top)
		if bottom > self.Height: bottompadding = abs(bottom - self.Height)
		if left < 0: leftpadding = abs(left)
		if right > self.Width: rightpadding = abs(right - self.Width)
		
		slicedmap = self.Slice2DArray(top, bottom, left, right, self.Map)
		padded = self.Pad2DArray(toppadding, bottompadding, leftpadding, rightpadding, slicedmap, " ")

		return self.RenderLayer(padded)
		
	def RenderLayer(self, layer):
		lines = []
		for row in layer:
			lines.append("".join([str(tile) for tile in row]))
		return lines

class Tile:
	def __init__(self, glyph = " ", barrier = False, opaque = False):
		self.Glyph = glyph
		self.Barrier = barrier
		self.Opaque = opaque
		self.Seen = False
		self.Entities = []
	
	def __str__(self):
		if self.Entities:
			return self.Entities[-1].Glyph
		else:
			return self.Glyph

class Entity:
	def __init__(self, initstats = None, tile = "@"):
		if not initstats:
			self.Stats = {"HP": 10, "Strength": 10, "Speed": 100, "Luck": 10, "XP": 0, "Level": 1}
		else:
			self.Stats = initstats
		self.DisplayedStats = ["HP", "Strength", "Speed", "", "Level", "XP"]
		self.Glyph = tile
		self.VisionRadius = 3
	
	def __str__(self):
		return self.Glyph
	
		
if __name__ == "__main__":
	anki_quester()