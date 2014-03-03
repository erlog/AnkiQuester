# -*- coding: utf-8 -*-

import os, sys, random, pdb

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
	AQIOController = IOController()
	
	#hook the review process to construct our game loop
	if not AQ_DEBUG:
		mw.reviewer._answerCard = catch_answer
	
	while not libtcod.console_is_window_closed(): 
		AQIOController.Update(AQGameInstance)

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
		self.Player = Entity()
		self.NPEs = [Entity(None, random.randint(0,60), random.randint(0, 40), "d")]
		self.AQAnswerResult = None
		self.Messages = []
	
	def PlayerMove(self, direction):
		oldxy = (self.Player.X, self.Player.Y)
		
		if direction == "Up": self.Player.Y -= 1
		elif direction == "Down": self.Player.Y += 1
		elif direction == "Left": self.Player.X -= 1
		elif direction == "Right": self.Player.X += 1
		
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
					
		
	def CollisionCheck(self, x, y):
		#check for collision on an existing entity, this is inefficient, but I don't care right now
		for entity in self.NPEs:
			if (entity.X == x) and (entity.Y == y): return entity
			
		return False
	
	def GiveXP(self, entity, xp):
		entity.Stats["XP"] += xp
		requiredxp = 2**entity.Stats["Level"]
		if entity.Stats["XP"] >= requiredxp:
			entity.Stats["Level"] += 1
			self.Messages.append("Level up!")
	
	def Entities(self):
		return [self.Player] + self.NPEs
	
	def ShuffleNPEs(self):
		for entity in self.NPEs:
			entity.X = random.randint(0,60)
			entity.Y = random.randint(0,40)
	
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
	def __init__(self):
		#Set up libtcod
		self.SCREEN_WIDTH = 80
		self.SCREEN_HEIGHT = 50
		self.STATUS_WIDTH = 15
		self.STATUS_HEIGHT = self.SCREEN_HEIGHT
		self.MSG_WIDTH = self.SCREEN_WIDTH-self.STATUS_WIDTH
		self.MSG_HEIGHT = 5
		self.DUNGEON_WIDTH = self.SCREEN_WIDTH - self.STATUS_WIDTH
		self.DUNGEON_HEIGHT = self.SCREEN_HEIGHT - self.MSG_HEIGHT
		self.LIMIT_FPS = 10
		
		libtcod.console_set_custom_font('consolas12x12_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'AnkiQuest', False)
		libtcod.sys_set_fps(self.LIMIT_FPS)
		
		self.messagelog = libtcod.console_new(self.MSG_WIDTH, self.MSG_HEIGHT)
		self.statuswindow = libtcod.console_new(self.STATUS_WIDTH, self.STATUS_HEIGHT)
		self.dungeon = libtcod.console_new(self.DUNGEON_WIDTH, self.DUNGEON_HEIGHT)

	
	def FocusGame(self):
		libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'AnkiQuest', False)
	
	def FocusAnki(self):
		mw.setFocus()
	
	def HandleKeys(self, state, ispressed):
		if libtcod.console_is_key_pressed(libtcod.KEY_UP): state.PlayerMove("Up")
		elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN): state.PlayerMove("Down")
		elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT): state.PlayerMove("Left")
		elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT): state.PlayerMove("Right")
	
	def DrawEntities(self, entities):
		for entity in entities:
			libtcod.console_put_char(self.dungeon, entity.X, entity.Y, entity.Tile, libtcod.BKGND_NONE)
	
	def EraseEntities(self, entities):
		for entity in entities:
			libtcod.console_put_char(self.dungeon, entity.X, entity.Y, " ", libtcod.BKGND_NONE)
	
	def RefreshWindow(self, state):
		self.DrawEntities(state.Entities())
		libtcod.console_blit(self.dungeon, 0, 0, self.DUNGEON_WIDTH, self.DUNGEON_HEIGHT, 0, 0, 0)
		libtcod.console_blit(self.messagelog, 0, 0, self.MSG_WIDTH, self.MSG_HEIGHT, 0, 0, self.DUNGEON_HEIGHT)
		libtcod.console_blit(self.statuswindow, 0, 0, self.STATUS_WIDTH, self.STATUS_HEIGHT, 0, self.DUNGEON_WIDTH, 0)
		libtcod.console_flush()
		self.EraseEntities(state.Entities())
	
	def Update(self, state):
		self.HandleKeys(state, libtcod.console_check_for_keypress())
		self.UpdateStatusWindow(state)
		self.UpdateMessageLog(state)
		self.RefreshWindow(state)
	
	def UpdateStatusWindow(self, state):
		libtcod.console_clear(self.statuswindow)
		libtcod.console_print(self.statuswindow, 0, 0, "STATUS-")
		currentline = 1
		for stat in state.Player.DisplayedStats:
			if stat != "": libtcod.console_print(self.statuswindow, 0, currentline, "{0}: {1}".format(stat, state.Player.Stats[stat]) )
			currentline += 1
	
	def UpdateMessageLog(self, state):
		libtcod.console_clear(self.messagelog)
		libtcod.console_print(self.messagelog, 0, 0, "MESSAGES-")
		currentline = 1
		for message in state.Messages[(-1)*(self.MSG_HEIGHT-1):]:
			libtcod.console_print(self.messagelog, 0, currentline, message)
			currentline += 1
	
	def Pause(self, state):
		libtcod.console_check_for_keypress()
		self.RefreshWindow(state)
	
	def PauseForReview(self, state):
		#libtcod.console_print(self.con, 0, 49, "Paused for Card Answer")
		libtcod.console_check_for_keypress()
		self.RefreshWindow(state)
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
		self.Tile = tile

if __name__ == "__main__":
	anki_quester()