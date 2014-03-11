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

def Cast_Light(floor, cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
		#Recursive lightcasting function.
		#To-do: clean up and comment this super-terse code.
		#To-do: make light have some amount of bounce/sticky nature to make it less flickery in areas with lots of obstructions.
		if start < end:
			return
			
		radius_squared = radius**2
		
		for j in range(row, radius+1):
			
			dx = -j-1
			dy = -j
			
			blocked = False
			
			while dx <= 0:
				dx += 1
				# Translate the dx, dy coordinates into map coordinates:
				X = cx + dx * xx + dy * xy
				Y = cy + dx * yx + dy * yy
				
				# l_slope and r_slope store the slopes of the left and right extremities of the square we're considering:
				l_slope = (dx-0.5)/(dy+0.5)
				r_slope = (dx+0.5)/(dy-0.5)
				
				if start < r_slope:
					continue
					
				elif end > l_slope:
					break
					
				else:
					# Our light beam is touching this square; light it:
					if not floor.OutOfBoundsCheck(X, Y) and (dx*dx + dy*dy < radius_squared):
						floor.SetTileLit(X, Y)
						
					if blocked:
						# we're scanning a row of blocked squares:
						if floor.OutOfBoundsCheck(X, Y) or floor.GetTile(X, Y).Opaque:
							new_start = r_slope
							continue
						else:
							blocked = False
							start = new_start
					else:
						if (floor.OutOfBoundsCheck(X, Y) or floor.GetTile(X, Y).Opaque) and j < radius:
							# This is a blocking square, start a child scan:
							blocked = True
							Cast_Light(floor, cx, cy, j+1, start, l_slope,
											 radius, xx, xy, yx, yy, id+1)
							new_start = r_slope
							
			# Row is scanned; do next row unless last square was blocked:
			if blocked:
				break

def RandomInteger(minimum, maximum):
	return randint(minimum, maximum)
