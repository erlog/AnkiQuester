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
		self.SpawnEnemy()
		self.SpawnEnemy()
		self.SpawnEnemy()
		self.SpawnEnemy()
		self.SpawnEnemy()
		self.CurrentFloor.PutEntity(self.Player, self.PlayerX, self.PlayerY)
	
	def PlayerMove(self, direction):
		oldxy = (self.PlayerX, self.PlayerY)		
		if direction == "Up": self.PlayerY -= 1
		elif direction == "Down": self.PlayerY += 1
		elif direction == "Left": self.PlayerX -= 1
		elif direction == "Right": self.PlayerX += 1
		elif direction == "Rest": pass
		
		collisioncheck = self.CollisionCheck(self.PlayerX, self.PlayerY)
		
		if collisioncheck == False:
			self.CurrentFloor.RemoveEntity(oldxy[0], oldxy[1])
			self.CurrentFloor.PutEntity(self.Player, self.PlayerX, self.PlayerY)
		elif collisioncheck != True:
			self.CurrentFloor.RemoveEntity(self.PlayerX, self.PlayerY)
			self.Messages.append("Vanquished!")
			self.GiveXP(self.Player, collisioncheck.Stats["HP"])
			self.PlayerX = oldxy[0]
			self.PlayerY = oldxy[1]
			self.SpawnEnemy()
		else:
			self.PlayerX = oldxy[0]
			self.PlayerY = oldxy[1]
		
			
	
	def MessageWindow(self, lines):
		lines = lines-1
		label = "MESSAGES:"
		if len(self.Messages) <= lines: 
			return os.linesep.join([label] + self.Messages)
		else:
			return os.linesep.join([label] + self.Messages[-1*lines:])
	
	def StatusWindow(self):
		statuswindowstring = "STATUS:"+os.linesep
		for key in self.Player.DisplayedStats:
			if key in self.Player.Stats:
				statuswindowstring += "{0}: {1}{2}".format(key, self.Player.Stats[key], os.linesep)
			else:
				statuswindowstring += os.linesep
		return statuswindowstring
			
	def CollisionCheck(self, x, y):
		if self.CurrentFloor.GetTile(x, y).Barrier:
			return True
		elif self.CurrentFloor.GetEntity(x, y) != " ":
			return self.CurrentFloor.GetEntity(x, y)
		else:
			return False
	
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
	
			


class DungeonFloor:
	def __init__(self, width = 100, height = 100):
		self.Width = width
		self.Height = height
		self.Map = [[self.WallOrNot() for x in range(self.Width)] for y in range(self.Height)]
		self.Entities = [[" " for x in range(self.Width)] for y in range(self.Height)]
				
	def WallOrNot(self):
		x = random.randint(0,3)
		if x == 0: return Tile(" ")
		elif x == 1: return Tile(" ")
		elif x == 2: return Tile(" ")
		elif x == 3: return Tile("O", True, True)
	
	def RandomTile(self):
		return random.randint(0, self.Width-1), random.randint(0, self.Height-1)
	
	def GetEntity(self, x, y):
		return self.Entities[y][x]
	
	def GetTile(self, x, y):
		return self.Map[y][x]
	
	def PutEntity(self, entity, x, y):
		self.Entities[y][x] = entity
	
	def RemoveEntity(self, x, y):
		self.Entities[y][x] = " "
	
	def RenderLayer(self, top, bottom, left, right, dungeonlayer):
		height = bottom - top
		width = (right - left) + len(os.linesep)
		toppadding = False
		bottompadding = False
		leftpadding = False
		rightpadding = False
		
		if top < 0: 
			toppadding = abs(top)
			top = 0
		if bottom > self.Height-1: 
			bottompadding = abs(bottom-self.Height+1)
			bottom = self.Height-1
		if left < 0: 
			leftpadding = abs(left)
			left = 0
		if right > self.Width-1:
			rightpadding = abs(right-self.Width+1)
			right = self.Width - 1
		
		layer = ""
		if toppadding:
			for x in range(toppadding):
				layer += os.linesep.rjust(width, " ")
		for row in dungeonlayer[top:bottom]:
			if leftpadding: 
				layer += "".center(leftpadding, " ")
			layer += "".join([str(tile) for tile in row[left:right]])
			if rightpadding: 
				layer += "".center(rightpadding, " ")
			layer += os.linesep
		if bottompadding:
			for x in range(bottompadding): 
				layer += os.linesep.rjust(width, " ")

		return layer
	
	def RenderFloor(self, top, bottom, left, right):
		terrain = self.RenderLayer(top, bottom, left, right, self.Map)
		entities = self.RenderLayer(top, bottom, left, right, self.Entities)
		
		outstring = ""
		for x in range(len(terrain)):
			if entities[x] != " ":
				outstring += entities[x]
			else:
				outstring += terrain[x]
		return outstring

class Tile:
	def __init__(self, glyph = " ", barrier = False, opaque = False):
		self.Glyph = glyph
		self.Barrier = barrier
		self.Opaque = opaque
		self.Seen = False
	
	def __str__(self):
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