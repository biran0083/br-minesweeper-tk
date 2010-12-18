#!/usr/bin/python
"""
Test on:
	construct game board from list of mine locations
	dig(valid/invalid coordinates)
	mark(valid/invalid coordinates)
	unmark(valid/invalid coordinates)
"""
import sys
sys.path.append("../")
import ms
from util import *

"""
	--*-
	*--*
	-*--
	*--*
"""
row=4
col=4
num=6
l=[(0,2),(1,0),(1,3),(2,1),(3,0),(3,3)]
gl=ms.GameLogic()
K=ms.Cell.KNOWN
U=ms.Cell.UNKNOWN
M=ms.Cell.MARKED

def create_game_board_from_list():
	global gl,l
	gl.new_game(row,col,num,mine_loc=l)
def create_game_board_from_list_validate():
	global gl,l
	for i in range(row):
		for j in range(col):
			if (i,j) in l:
				if gl.get_cell_value(i,j)!=ms.Cell.MINE:
					return False
			elif gl.get_cell_value(i,j)==ms.Cell.MINE:
				return False
	return True

def dig_0_0():
	global gl
	gl.dig(0,0)
def dig_0_0_validate():
	global gl,K,U,M
	exp=[	
		[K,U,U,U],
		[U,U,U,U],
		[U,U,U,U],
		[U,U,U,U]
	    ]
	return check_board_state(gl,exp)
def mark_1_0():
	global gl
	gl.mark(1,0)
def mark_1_0_validate():
	global gl,K,U,M
	exp=[	
		[K,U,U,U],
		[M,U,U,U],
		[U,U,U,U],
		[U,U,U,U]
	    ]
	return check_board_state(gl,exp)
def dig_10_10():
	global gl
	gl.dig(10,00)
def mark_10_10():
	global gl
	gl.mark(10,00)

def unmark_1_0():
	global gl
	gl.unmark(1,0)
def unmark_10_10():
	global gl
	gl.unmark(10,10)

def unmark_1_0_validate():
	global gl,K,U,M
	exp=[	
		[K,U,U,U],
		[U,U,U,U],
		[U,U,U,U],
		[U,U,U,U]
	    ]
	return check_board_state(gl,exp)

test_and_validate(create_game_board_from_list,\
		create_game_board_from_list_validate)
test_and_validate(dig_0_0,dig_0_0_validate)
test_and_validate(mark_1_0,mark_1_0_validate)
test_except(dig_10_10,"InvalidCoordinate")
test_except(mark_10_10,"InvalidCoordinate")
test_and_validate(unmark_1_0,unmark_1_0_validate)
test_except(unmark_10_10,"InvalidCoordinate")

print "%s:\tpass" % sys.argv[0]
