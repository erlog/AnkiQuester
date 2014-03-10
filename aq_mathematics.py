# -*- coding: utf-8 -*-

#Standard Library Imports
from random import randint

def Pad2DArray(toppadding, bottompadding, leftpadding, rightpadding, array, paddingobject):
		#To-do: There's no reason for this to be a method of this class.
		#		This should be moved to a separate math library so that future optimizations,
		#		such as NumPy support, can be easily added.
		emptyrow = [paddingobject for x in range(leftpadding + len(array[0]) + rightpadding)]
		leftpad = [paddingobject for x in range(leftpadding)]
		rightpad = [paddingobject for x in range(rightpadding)]
		
		paddedrows = [emptyrow for x in range(toppadding)]
		
		for row in array:
			paddedrows.append(leftpad + row + rightpad)
			
		paddedrows += [emptyrow for x in range(bottompadding)]
		
		return paddedrows
		
def Slice2DArray(top, bottom, left, right, array):
		#To-do: There's no reason for this to be a method of this class.
		#		This should be moved to a separate math library so that future optimizations,
		#		such as NumPy support, can be easily added.
		
		arrayheight = len(array)
		arraywidth = len(array[0])
		
		if top < 0: 
			top = 0
		if bottom > arrayheight: 
			bottom = arrayheight
		if left < 0: 
			left = 0
		if right > arraywidth: 
			right = arraywidth
	
		return [row[left:right] for row in array[top:bottom]]

def RandomInteger(minimum, maximum):
	return randint(minimum, maximum)
