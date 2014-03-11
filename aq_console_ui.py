# -*- coding: utf-8 -*-
#This file is for containing the Console-style AQ UI. 
#The goal is to keep different UI's independent of each other, and independent of AQ.
#To-do: write a comprehensive event system so that UI doesn't need to concern itself with message strings.

#Standard Library Imports
from os import linesep
string = ""

#AnkiQuester imports
from aq_strings import *

class ConsoleUserInterface:
	def __init__(self, state, screenwidth = 80, screenheight = 40, statuswidth = 15, msgheight = 6):
		#Right now our status area is on the right side of the screen with our message window across the bottom.
		#The math is done in this init function so that later the heights and widths can be user-specified
		
		self.ScreenWidth = screenwidth
		self.ScreenHeight = screenheight
		
		self.StatusWidth = statuswidth
		self.StatusHeight = self.ScreenHeight
		
		self.MsgHeight = msgheight
		self.MsgWidth = self.ScreenWidth - self.StatusWidth
		
		self.DungeonWidth = self.ScreenWidth - self.StatusWidth
		self.DungeonHeight = self.ScreenHeight - self.MsgHeight
		
		self.GameState = state
		self.Strings = AQ_Strings()
	
	def RenderScreen(self):
		#Take lists of lines for each screen portion and munge them together into a layout.
		#This is the only function that should ever be messing with line separators.
		#To-do: Support user-definable and arbitrary window layouts.
		
		dungeonlines = self.DungeonWindow()
		statuslines = self.StatusWindowItems()
		
		for index in range(len(statuslines)):
			dungeonlines[index] = dungeonlines[index] + statuslines[index]
			
		messagelines = self.MessageWindow(self.MsgHeight)
		
		return linesep.join(dungeonlines + messagelines)
	
	def DungeonWindow(self):
		#Right now our tile is deciding by itself what kind of representation to give us via logic in the str method.
		#This could be made more extensible in a graphical version later, but is fine as it is for a console version.
		dungeontiles = self.GameState.CurrentFloor.RenderSlice((self.GameState.Player.Y - self.DungeonHeight/2), 
														(self.GameState.Player.Y + self.DungeonHeight/2),
														(self.GameState.Player.X - self.DungeonWidth/2),
														(self.GameState.Player.X + self.DungeonWidth/2),
														self.GameState.Player.X,
														self.GameState.Player.Y,
														self.GameState.Player.VisionRadius)
		
		lines = []
		for row in dungeontiles:
			lines.append(string.join([str(tile) for tile in row]))
			
		return lines
	
	def MessageWindow(self, linecount):
		#To-do: support for user-definable formatting of the MessageWindow.
		#	Ideally users should be able to filter kinds of messages they receive in a granular fashion to prevent spam.
		linecount -= 1
		label = self.Strings.MessageWindowLabel
		if len(self.GameState.Messages) <= linecount: 
			return [label] + [(" "+line) for line in self.GameState.Messages]
		else:
			return [label] + [(" "+line) for line in self.GameState.Messages[-1*linecount:]]
	
	def StatusWindowItems(self):
		#To-do: support for user-definable formatting of the Status window via something like lua.
		#		This should include robust support for what kind of data to display.
		
		items = [self.Strings.StatusWindowLabel]
		
		#Blank items result in a blank line. Non-blank items map to dictionary keys in Player.Stats
		displayedstats = [  
							[self.Strings.HP, self.GameState.Player.HP],
							[self.Strings.Strength, self.GameState.Player.Strength], 
							[self.Strings.Speed, self.GameState.Player.Speed],
							[self.Strings.Luck, self.GameState.Player.Luck],
							[],
							[self.Strings.Level, self.GameState.Player.Level],
							[self.Strings.XP, self.GameState.Player.XP],
							[],
							[self.Strings.Turn, self.GameState.CurrentTurn],
						]
		
		for line in displayedstats:
			if line:
				items.append(" {0}: {1}".format(line[0], line[1]))
			else:
				items.append("")
		
		return items