# -*- coding: utf-8 -*-
#This file exists to aggregate mathematical functions that might need to be
#changed or optimized in the future. For example, a lot of the array functions
#could probably be moved to NumPy in the future if need be.

#Standard Library Imports
from random import randint

def Pad2DArray(toppadding, bottompadding, leftpadding, rightpadding, array, paddingobject):
		emptyrow = [paddingobject for x in range(leftpadding + len(array[0]) + rightpadding)]
		leftpad = [paddingobject for x in range(leftpadding)]
		rightpad = [paddingobject for x in range(rightpadding)]
		
		paddedrows = [emptyrow for x in range(toppadding)]
		
		for row in array:
			paddedrows.append(leftpad + row + rightpad)
			
		paddedrows += [emptyrow for x in range(bottompadding)]
		
		return paddedrows
		
def Slice2DArray(top, bottom, left, right, array):
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
