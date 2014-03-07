# -*- coding: utf-8 -*-

class AQ_Strings:
	#This class is built so that localization/message re-writes can happen smoothly later.
	#To-do: Add some method of serializing out to CSV for editing/importing later.
	#To-do: Add method for loading serialized/pickled instances of this class in order to dynamically load localized strings.
	def __init__(self):	
		#Interface Labels
		self.MessageWindowLabel = "MESSAGES-"
		self.StatusWindowLabel = "STATUS-"
		
		
		#Entity Stats and Information Strings
		self.HP = "HP"
		self.Strength = "Strength"
		self.Speed = "Speed"
		self.Luck = "Luck"
		self.Level = "Level"
		self.XP = "XP"
		
		self.HP_Short = self.HP
		self.Strength_Short = "Str"
		self.Speed_Short = "Spd"
		self.Luck_Short = "Lck"
		self.Level_Short = "Lvl"
		self.XP_Short = "XP"
		
		
		#Misc Labels
		self.LevelUpMessage = "Level up! Welcome to Level {0}!"
		self.Turn = "Turn"
		
		
		
		
		