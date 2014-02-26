# -*- coding: utf-8 -*-



import pdb
import random
import libtcodpy as libtcod

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
	
	def TakeDamage(self, amount):
		opponent.Stats["HP"] -= amount
		
def handle_keys():
    global playerx, playery

    key = libtcod.console_wait_for_keypress(True)  #turn-based
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game
 
    #movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        playery -= 1
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        playery += 1
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        playerx -= 1
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        playerx += 1

if __name__ == "__main__":
	#erlog = Entity()
	#ckky = Entity()
	#mechanics = WorldMe
	#erlog.Attack(ckky)
	#print ckky.Stats
	
	SCREEN_WIDTH = 80
	SCREEN_HEIGHT = 50
	LIMIT_FPS = 10
	
	libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
	libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
	libtcod.sys_set_fps(LIMIT_FPS)
	 
	playerx = SCREEN_WIDTH/2
	playery = SCREEN_HEIGHT/2
 
	while not libtcod.console_is_window_closed():
	 
		#libtcod.console_set_default_foreground(0, libtcod.white)
		libtcod.console_put_char(0, playerx, playery, '@', libtcod.BKGND_NONE)
	 
		libtcod.console_flush()
	 
		libtcod.console_put_char(0, playerx, playery, ' ', libtcod.BKGND_NONE)
	 
		#handle keys and exit game if needed
		exit = handle_keys()
		if exit:
			break