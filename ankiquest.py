# -*- coding: utf-8 -*-

import os, sys, random
from math import ceil

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
	import pdb
	

	
def anki_quester():
	global libtcod, AQGameInstance, AQIOController
	
	#Load libtcod
	libtcodpath = os.path.normpath(os.path.join(AQ_PATH, "libtcod151/"))
	os.chdir(libtcodpath)
	sys.path.append(libtcodpath)
	
	#scope gets weird with Anki plugins, and so this way we can be sure our libtcod will be available where we need it
	import libtcodpy
	libtcod = libtcodpy
	
	#Set up our game objects
	AQGameInstance = AnkiQuester()
	AQIOController = IOController(AQGameInstance)
	
	#hook the review process to construct our game loop
	if not AQ_DEBUG:
		mw.reviewer._answerCard = catch_answer
	
	AQGameInstance.CurrentFloor
	
	while not libtcod.console_is_window_closed(): 
		AQIOController.Update()

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
		self.Player.X = 0
		self.Player.Y = 0
		self.NPEs = [Entity(None, random.randint(0,60), random.randint(0, 40), "d")]
		self.AQAnswerResult = None
		self.Messages = []
		self.TurnCounter = 0
		
	
	def PlayerMove(self, direction):
		oldxy = (self.Player.X, self.Player.Y)
		
		if direction == "Up": self.Player.Y -= 1
		elif direction == "Down": self.Player.Y += 1
		elif direction == "Left": self.Player.X -= 1
		elif direction == "Right": self.Player.X += 1
		elif direction == "Rest": pass
		
		collisionentity = self.CollisionCheck(self.Player.X, self.Player.Y)
		if collisionentity != False:
			self.Player.X = oldxy[0]
			self.Player.Y = oldxy[1]
			#simple code to vanquish an enemy and spawn a new one
			if collisionentity in self.NPEs:
				attackresult = self.DoFlashcard()
				if attackresult > 1:
					self.Messages.append("Vanquished!")
					self.NPEs.remove(collisionentity)
					self.NPEs.append(Entity(None, random.randint(0,60), random.randint(0, 40), "d"))
					self.GiveXP(self.Player, collisionentity.Stats["HP"])
			else:
				self.Messages.append("Hit a wall!")
					
		
	def CollisionCheck(self, x, y):
		if self.CurrentFloor.Map[y][x].Barrier: return True
		#check for collision on an existing entity, this is inefficient, but I don't care right now
		for entity in self.NPEs:
			if (entity.X == x) and (entity.Y == y): return entity
			
		return False
	
	def GiveXP(self, entity, xp):
		entity.Stats["XP"] += xp
		while entity.Stats["XP"] >= 2**entity.Stats["Level"]*15:
			entity.Stats["Level"] += 1
			self.Messages.append("Level up! Welcome to Level {0}!".format(entity.Stats["Level"]))
	
	def Entities(self):
		return [self.Player] + self.NPEs
	
	def MoveNPEs(self):
		for entity in self.NPEs:
			oldx = entity.X
			oldy = entity.Y
			entity.MoveCloserTo(self.Player)
			if self.CollisionCheck(entity.X, entity.Y) == True:
				entity.X = oldx
				entity.Y = oldy
	
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
	
class IOController:
	def __init__(self, state):
		self.GameState = state
		
		#Set up libtcod
		self.SCREEN_WIDTH = 80
		self.SCREEN_HEIGHT = 50
		self.STATUS_WIDTH = 15
		self.STATUS_HEIGHT = self.SCREEN_HEIGHT
		self.MSG_WIDTH = self.SCREEN_WIDTH-self.STATUS_WIDTH
		self.MSG_HEIGHT = 6
		self.DUNGEON_WIDTH = self.SCREEN_WIDTH - self.STATUS_WIDTH
		self.DUNGEON_HEIGHT = self.SCREEN_HEIGHT - self.MSG_HEIGHT
		self.LIMIT_FPS = 30
	
		libtcod.console_set_custom_font('consolas12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'AnkiQuest', False)
		libtcod.sys_set_fps(self.LIMIT_FPS)
		
		self.messagelog = libtcod.console_new(self.MSG_WIDTH, self.MSG_HEIGHT)
		self.statuswindow = libtcod.console_new(self.STATUS_WIDTH, self.STATUS_HEIGHT)
		self.dungeon = self.InitDungeon(self.GameState.CurrentFloor.Map)
		self.blank = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

	
	def FocusGame(self):
		libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'AnkiQuest', False)
	
	def FocusAnki(self):
		mw.setFocus()
	
	def HandleKeys(self, key):
		if key == libtcod.KEY_NONE:
			return False
		elif key == libtcod.KEY_UP: self.GameState.PlayerMove("Up")
		elif key == libtcod.KEY_DOWN: self.GameState.PlayerMove("Down")
		elif key == libtcod.KEY_LEFT: self.GameState.PlayerMove("Left")
		elif key == libtcod.KEY_RIGHT: self.GameState.PlayerMove("Right")
		elif (key == libtcod.KEY_SPACE) or (key == libtcod.KEY_CHAR): self.GameState.PlayerMove("Rest")
		elif (key == libtcod.KEY_ESCAPE) and AQ_DEBUG: sys.exit()
		elif (key == libtcod.KEY_F2) and AQ_DEBUG: pdb.set_trace()
		else:
			return False
		
		return True
	
	def DrawEntities(self, entities):
		for entity in entities:
			libtcod.console_put_char(self.dungeon, entity.X, entity.Y, entity.Glyph, libtcod.BKGND_NONE)
	
	def EraseEntities(self, entities):
		for entity in entities:
			libtcod.console_put_char(self.dungeon, entity.X, entity.Y, self.GameState.CurrentFloor.Map[entity.Y][entity.X].Glyph, libtcod.BKGND_NONE)
	
	def RefreshWindow(self):
		self.DrawEntities(self.GameState.Entities())
		libtcod.console_blit(self.blank, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_blit(self.dungeon, self.GameState.Player.X-(self.DUNGEON_WIDTH/2), self.GameState.Player.Y-(self.DUNGEON_HEIGHT/2), self.DUNGEON_WIDTH, self.DUNGEON_HEIGHT, 0, 0, 0)
		libtcod.console_blit(self.messagelog, 0, 0, self.MSG_WIDTH, self.MSG_HEIGHT, 0, 0, self.DUNGEON_HEIGHT)
		libtcod.console_blit(self.statuswindow, 0, 0, self.STATUS_WIDTH, self.STATUS_HEIGHT, 0, self.DUNGEON_WIDTH, 0)
		libtcod.console_flush()
		self.EraseEntities(self.GameState.Entities())
	
	def Update(self):
		if self.HandleKeys(libtcod.console_check_for_keypress().vk):
			self.GameState.TurnCounter += 1
			self.GameState.MoveNPEs()
		self.UpdateDungeon()
		self.UpdateStatusWindow()
		self.UpdateMessageLog()
		self.RefreshWindow()
	
	def InitDungeon(self, floor):
		height = len(floor)
		width = len(floor[0])
		consolizedfloor = libtcod.console_new(height, width)
		for y in range(height):
			for x in range(width):
				libtcod.console_put_char(consolizedfloor, x, y, floor[y][x].Glyph, libtcod.BKGND_NONE)
		return consolizedfloor
		
	def UpdateDungeon(self):
		self.GameState.Player.X
		
				
	def UpdateStatusWindow(self):
		libtcod.console_print_frame(self.statuswindow, 0, 0, self.STATUS_WIDTH, self.STATUS_HEIGHT)
		libtcod.console_print(self.statuswindow, 1, 0, "STATUS")
		currentline = 1
		for stat in self.GameState.Player.DisplayedStats:
			if stat != "": libtcod.console_print(self.statuswindow, 1, currentline, "{0}: {1}".format(stat, self.GameState.Player.Stats[stat]) )
			currentline += 1
		libtcod.console_print(self.statuswindow, 1, currentline+2, "Turn: {0}".format(self.GameState.TurnCounter))
		if AQ_DEBUG:
			libtcod.console_print(self.statuswindow, 1, currentline+3, "FPS: {0}".format(libtcod.sys_get_fps()))
	
	def UpdateMessageLog(self):
		libtcod.console_print_frame(self.messagelog, 0, 0, self.MSG_WIDTH, self.MSG_HEIGHT)
		libtcod.console_print(self.messagelog, 1, 0, "MESSAGES")
		currentline = 1
		for message in self.GameState.Messages[(-1)*(self.MSG_HEIGHT-2):]:
			libtcod.console_print(self.messagelog, 1, currentline, message)
			currentline += 1
	
	def Pause(self):
		libtcod.console_check_for_keypress()
		self.RefreshWindow()
	
	def PauseForReview(self):
		#libtcod.console_print(self.con, 0, 49, "Paused for Card Answer")
		libtcod.console_check_for_keypress()
		self.RefreshWindow()
		#libtcod.console_print(self.con, 0, 49, "                      ")
			
class Entity:
	def __init__(self, initstats = None, xpos = 0, ypos = 0, tile = "@"):
		if not initstats:
			self.Stats = {"HP": 10, "Strength": 10, "Speed": 100, "Luck": 10, "XP": 0, "Level": 1}
		else:
			self.Stats = initstats
		self.DisplayedStats = ["HP", "Strength", "Speed", "", "Level", "XP"]
		self.X = xpos
		self.Y = ypos
		self.Glyph = tile
		self.VisionRadius = 3
	
	def MoveCloserTo(self, entity):
		#Base speed of 100 = 1 turn/second
		distance = 1
		if (self.X > entity.X) and (self.X - distance != entity.X): self.X -= distance
		elif (self.X < entity.X) and (self.X + distance != entity.X): self.X += distance
		if (self.Y > entity.Y) and (self.Y - distance != entity.Y): self.Y -= distance
		elif (self.Y < entity.Y) and (self.Y + distance != entity.Y): self.Y += distance

class DungeonFloor:
	def __init__(self):
		self.Width = 100
		self.Height = 100
		self.Map = [[self.WallOrNot() for x in range(self.Width)] for y in range(self.Height)]
				
				
	def WallOrNot(self):
		x = random.randint(0,3)
		if x == 0: return Tile(" ")
		elif x == 1: return Tile(" ")
		elif x == 2: return Tile(" ")
		elif x == 3: return Tile("0", True, True)
		

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