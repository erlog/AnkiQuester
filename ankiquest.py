# -*- coding: utf-8 -*-

import os, sys, random
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
		self.CurrentFloor.PutEntity(self.Player, self.PlayerX, self.PlayerY)
	
	def PlayerMove(self, direction):
		self.CurrentFloor.RemoveEntity(self.PlayerX, self.PlayerY)
		if direction == "Up": self.PlayerY -= 1
		elif direction == "Down": self.PlayerY += 1
		elif direction == "Left": self.PlayerX -= 1
		elif direction == "Right": self.PlayerX += 1
		elif direction == "Rest": pass
		self.CurrentFloor.PutEntity(self.Player, self.PlayerX, self.PlayerY)
			
	def CollisionCheck(self, x, y):
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

class DungeonFloor:
	def __init__(self, width = 60, height = 30):
		self.Width = width
		self.Height = height
		self.Map = [[self.WallOrNot() for x in range(self.Width)] for y in range(self.Height)]
		self.Entities = [[" " for x in range(self.Width)] for y in range(self.Height)]
				
	def WallOrNot(self):
		x = random.randint(0,3)
		if x == 0: return Tile(" ")
		elif x == 1: return Tile(" ")
		elif x == 2: return Tile(" ")
		elif x == 3: return Tile("0", True, True)
	
	def RandomTile(self):
		return random.randint(0, self.Width-1), random.randint(0, self.Height-1)
	
	def GetTile(self, x, y):
		return self.Map[y][x]
	
	def PutEntity(self, entity, x, y):
		self.Entities[y][x] = entity
	
	def RemoveEntity(self, x, y):
		self.Entities[y][x] = " "
	
	def __str__(self):
		terrain = ""
		for row in self.Map:
			terrain += "".join([tile.Glyph for tile in row]+[os.linesep])
		
		entities = ""
		for row in self.Entities:
			entities += "".join([str(entity) for entity in row]+[os.linesep])
			
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
	
		
if __name__ == "__main__":
	anki_quester()