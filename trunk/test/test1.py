#!/usr/bin/python
"""
Test on:
	constructing game logic
	creating new game(valid/invalid size)
"""
import sys
sys.path.append("../")
import ms
from util import *

def create_new_game():
	global gl
	gl=ms.GameLogic()
def create_valid_new_game():
	global gl
	gl.new_game(10,10,10)
def create_too_small_new_game():
	global gl
	gl.new_game(-1,-1,10)
def create_too_big_new_game():
	global gl
	gl.new_game(-1,-1,10)
def create_not_enuogh_mines_new_game():
	global gl
	gl.new_game(10,10,0)
def create_too_many_mines_new_game():
	global gl
	gl.new_game(10,10,1000)

test_no_except(create_new_game)
test_no_except(create_valid_new_game)
test_except(create_too_small_new_game,"InvalidBoardSize")
test_except(create_too_big_new_game,"InvalidBoardSize")
test_except(create_not_enuogh_mines_new_game,"InvalidMineNumber")
test_except(create_too_many_mines_new_game,"InvalidMineNumber")

print "%s:\tpass" % sys.argv[0]
