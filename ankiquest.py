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
	#if not AQ_DEBUG:
	#	mw.reviewer._answerCard = catch_review
	
	while not libtcod.console_is_window_closed(): 
		AQIOController.RefreshWindow(AQGameInstance)

def catch_review(ease):
	AQGameInstance.ShuffleNPEs()
	AQIOController.RefreshWindow(AQGameInstance)
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
		self.NPEs = [Entity(None, random.randint(0,79), random.randint(0, 49), "d")]
	
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
				self.NPEs.remove(collisionentity)
				self.NPEs.append(Entity(None, random.randint(0,79), random.randint(0, 49), "d"))
		
	def CollisionCheck(self, x, y):
		#check for collision on an existing entity, this is inefficient, but I don't care right now
		for entity in self.NPEs:
			if (entity.X == x) and (entity.Y == y): return entity
			
		return False
	
	def Entities(self):
		return [self.Player] + self.NPEs
	
	def ShuffleNPEs(self):
		for entity in self.NPEs:
			entity.X = random.randint(0,79)
			entity.Y = random.randint(0,49)
		
class IOController:
	def __init__(self):
		#Set up libtcod
		self.SCREEN_WIDTH = 80
		self.SCREEN_HEIGHT = 50
		self.LIMIT_FPS = 10
		libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
		libtcod.console_init_root(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 'AnkiQuest', False)
		libtcod.sys_set_fps(self.LIMIT_FPS)
		self.con = libtcod.console_new(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
	
	def HandleKeys(self, state, key):
		if libtcod.console_is_key_pressed(libtcod.KEY_UP): state.PlayerMove("Up")
		elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN): state.PlayerMove("Down")
		elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT): state.PlayerMove("Left")
		elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT): state.PlayerMove("Right")
	
	def DrawEntities(self, entities):
		for entity in entities:
			libtcod.console_put_char(self.con, entity.X, entity.Y, entity.Tile, libtcod.BKGND_NONE)
	
	def EraseEntities(self, entities):
		for entity in entities:
			libtcod.console_put_char(self.con, entity.X, entity.Y, " ", libtcod.BKGND_NONE)
	
	def RefreshWindow(self, state):
		self.HandleKeys(state, libtcod.console_check_for_keypress())
		self.DrawEntities(state.Entities())
		libtcod.console_blit(self.con, 0, 0, self.SCREEN_WIDTH, self.SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
		self.EraseEntities(state.Entities())
			
class Entity:
	def __init__(self, initstats = {"HP": 100, "Strength": 10, "Speed": 100, "Luck": 10}, xpos = 0, ypos = 0, tile = "@"):
		self.Stats = initstats
		self.X = xpos
		self.Y = ypos
		self.Tile = tile

if __name__ == "__main__":
	anki_quester()