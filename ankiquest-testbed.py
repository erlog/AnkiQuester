# -*- coding: utf-8 -*-

import pdb
import random

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

if __name__ == "__main__":
	erlog = Entity()
	ckky = Entity()
	mechanics = WorldMe
	erlog.Attack(ckky)
	print ckky.Stats