# -*- coding: utf-8 -*-

import pdb
import os, sys

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from aqt import forms
	
def anki_quester():
	global libtcod
	#This sucks right now, but the libtcod website is broken, so しかたない
	if sys.platform.find("win32") != -1:
		os.chdir(os.path.join(mw.addonManager.addonsFolder(), "/ankiquester/libtcod151"))
		from libtcod151 import libtcodpy
	elif sys.platform.find("darwin") != -1:
		os.chdir(os.path.join(mw.addonManager.addonsFolder(), "/ankiquester/libtcod160"))
		from libtcod160 import libtcodpy
	else:
		showInfo("Unsupported Platform")
		return
	
	libtcod = libtcodpy
	
	#Our game stuff
	global Player, Entities, con
	Entities = []
	Player = Entity()
	ckky = Entity()
	ckky.X = 40
	ckky.Y = 25
	ckky.Tile = "d"
	
	#Set up libtcod
	SCREEN_WIDTH = 80
	SCREEN_HEIGHT = 50
	LIMIT_FPS = 10
	libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'AnkiQuest', False)
	libtcod.sys_set_fps(LIMIT_FPS)
	con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
	
	while not libtcod.console_is_window_closed():
		draw_entities()
		libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
		erase_entities()
		handle_key(libtcod.console_wait_for_keypress(True))

# create a new menu item, connect our function, and add it to the menu
action = QAction("AnkiQuest", mw)
mw.connect(action, SIGNAL("triggered()"), anki_quester)
mw.form.menuTools.addAction(action)

class WorldMechanics:
	def __init__(self):
		pass
	
	def Fudge(srcvalue, fudgeratio):
		return srcvalue
	
	def Attack(attacker, defender):
		defender.TakeDamage(self.Fudge(attacker.Stats["Strength"], defender.Stats["Luck"]))
		
class Entity:
	def __init__(self, initstats=None):
		if not initstats:
			self.Stats =   {"HP": 100,
							"Strength": 10,
							"Speed": 100,
							"Luck": 10,
							}
		self.X = 0
		self.Y = 0
		self.Tile = "@"
		Entities.append(self)
		
	def TakeDamage(self, amount):
		opponent.Stats["HP"] -= amount
		
def handle_key(key):
 
	#movement keys
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		Player.Y -= 1
	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		Player.Y += 1
	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		Player.X -= 1
	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		Player.X += 1

def draw_entities():
	for entity in Entities:
		libtcod.console_put_char(con, entity.X, entity.Y, entity.Tile, libtcod.BKGND_NONE)
	
def erase_entities():
	for entity in Entities:
		libtcod.console_put_char(con, entity.X, entity.Y, " ", libtcod.BKGND_NONE)
	 