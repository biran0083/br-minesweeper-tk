#!/usr/bin/python
"""
Test on:
	construct board form list
	lose a game
"""
import sys
sys.path.append("../")
import ms
from util import *

"""
	---*-
	----*
	*----
	--*--
	-----
"""
row=5
col=5
num=4
l=[(0,3),(1,4),(2,0),(3,2)]
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
				if gl.game_board.board[i][j].val!=ms.Cell.MINE:
					return False
			elif gl.game_board.board[i][j].val==ms.Cell.MINE:
				return False
	return True
def play_the_game():
	global gl
	gl.dig(0,0)
	gl.mark(1,4)
	gl.mark(0,3)
	gl.dig(2,0)
def play_the_game_validate():
	global gl
	return gl.state==gl.LOSE

quiet()

test_and_validate(create_game_board_from_list,\
		create_game_board_from_list_validate)
test_and_validate(play_the_game,play_the_game_validate)

quiet(flag=False)
print "%s:\tpass" % sys.argv[0]
