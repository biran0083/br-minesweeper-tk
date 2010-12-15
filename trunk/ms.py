#!/usr/bin/python
import sys,random,pickle
class Cell:
	"""
		fields:
			row
			col
			val
			state
	"""
	MINE=-1
	#	state value
	UNKNOWN=0
	KNOWN=1
	MARKED=2
	def __init__(self,row=0,col=0,val=0,str=None):
		self.row=row
		self.col=col
		self.val=val
		self.state=Cell.UNKNOWN
	def __str__(self):
		if self.state==Cell.UNKNOWN:
			return '[ ]'
		elif self.state==Cell.KNOWN:
			if self.val==Cell.MINE:
				return '|*|'
			elif self.val==0:
				return '| |'
			return '|%d|' % self.val
		elif self.state==Cell.MARKED:
			return '|M|'

class InvalidMineNumber(Exception):
	pass
class InvalidBoardSize(Exception):
	pass
class InvalidCoordinate(Exception):
	pass
class CellKnownAlready(Exception):
	pass
class CellMarkedAlready(Exception):
	pass
class GameNotRunning(Exception):
	pass
class NotReadyToExplore(Exception):
	pass

class Board:
	"""
		fields:
			board
			row
			col
	"""
	def random_fillin_mines(self,board,num):
		for i in range(num):
			while 1:
				ti=random.randint(0,self.row-1)
				tj=random.randint(0,self.col-1)
				if board[ti][tj].val!=Cell.MINE:
					board[ti][tj].val=Cell.MINE
					break
	def invalid(self,i,j):
		return i<0 or j<0 or i>=self.row or j>=self.col
	def inc_all_neighbours(self,board,i,j):
		l=self.get_neighbours(i,j)
		for i,j in l:
			if board[i][j].val==Cell.MINE:continue
			board[i][j].val+=1
	def build_board(self,row,col,num,mine_loc=None):
		self.row=row
		self.col=col
		board=[[Cell(i,j,0) for j in range(col)]for i in range(row)]
		if mine_loc==None:
			self.random_fillin_mines(board,num)
		else:
			for i,j in mine_loc:
				board[i][j].val=Cell.MINE
		for i in range(row):
			for j in range(col):
				if board[i][j].val==Cell.MINE:
					self.inc_all_neighbours(board,i,j)
		return board

	def __init__(self,row,col,num,mine_loc=None):
		if row < 2 or col < 2 or row > 30 or col > 30: 
			raise InvalidBoardSize("Row number and column number must be within [2,30]")
		if num>row*col: raise InvalidMineNumber("Number of mines cannot be larger than numer of cells")
		if num<=0: raise InvalidMineNumber("Must have positive mine numbers")
		if mine_loc!=None and len(mine_loc)!=num:raise InvalidMineNumber("Mine locatin list does not agree with mine number given")

		self.board=self.build_board(row,col,num,mine_loc=mine_loc)

	def get_neighbours(self,i,j):
		res=[]
		for di in range(-1,2):
			for dj in range(-1,2):
				if di==0 and dj==0:continue
				ti=i+di
				tj=j+dj
				if self.invalid(ti,tj):continue
				res.append((ti,tj))
		return res
		
	def __str__(self):
		res="\n"
		res+="  "
		for i in range(self.col):res+="%3d" % i
		res+="\n"
		for i in range(self.row):
			res+="%-3d" % i
			row=self.board[i]
			for cell in row:
				res+=str(cell)
			res+="\n"
		return res



class GameLogic:
	"""
		field:
			game_board
			row
			col
			state
	"""
	STOP=0
	RUN=1
	WIN=2
	LOSE=3
	def __init__(self):
		self.state=GameLogic.STOP
#private
	def get_cell_value(self,i,j):
		return self.game_board.board[i][j].val
	def get_cell_state(self,i,j):
		return self.game_board.board[i][j].state
	def set_cell_state(self,i,j,val):
		self.game_board.board[i][j].state=val
	def reveal_all(self):
		for i in range(self.row):
			for j in range(self.col):
				self.set_cell_state(i,j,Cell.KNOWN)
	def lose(self):
		self.reveal_all()
		print str(self)
		self.state=GameLogic.LOSE
		print "You Lose...\n Better luck next time!\n"
	def win(self):
		self.reveal_all()
		print str(self)
		self.state=GameLogic.WIN
		print "Congratulations! You Win!!\n"

	def flood_fill_dig(self,i,j):
		if self.game_board.invalid(i,j) or\
			self.get_cell_state(i,j)==Cell.KNOWN:
			return
		self.set_cell_state(i,j,Cell.KNOWN)
		if self.get_cell_value(i,j)==0:
			for di in range(-1,2):
				for dj in range(-1,2):
					self.flood_fill_dig(i+di,j+dj)
	def check_win(self):
		"""
			return true if all MINE cells are MARKED, and the rest are KNOWN
		"""
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		for i in range(self.row):
			for j in range(self.col):
				if self.get_cell_value(i,j)==Cell.MINE:
					if self.get_cell_state(i,j)!=Cell.MARKED:
						return False
				elif self.get_cell_state(i,j)!=Cell.KNOWN:
					return False
		return True
#public
	def new_game(self,row,col,num,mine_loc=None):
		self.state=GameLogic.RUN
		self.row=row
		self.col=col
		self.game_board=Board(row,col,num,mine_loc=mine_loc)

	def dig(self,i,j):
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		if self.game_board.invalid(i,j):
			raise InvalidCoordinate("invalid coordinate: (%d,%d)" % (i,j))
		if self.get_cell_state(i,j)==Cell.KNOWN:
			raise Exception("cell (%d,%d) is KNOWN already" % (i,j))
		if self.get_cell_state(i,j)==Cell.MARKED:
			raise Exception("cell (%d,%d) is MARKED already" % (i,j))
		if self.get_cell_value(i,j)==0:
			self.flood_fill_dig(i,j)
		elif self.get_cell_value(i,j)==Cell.MINE:
			self.lose()
			return
		else: self.set_cell_state(i,j,Cell.KNOWN)
		
		if self.check_win():
			self.win()
	def mark(self,i,j):
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		if self.game_board.invalid(i,j):
			raise InvalidCoordinate("invalid coordinate: (%d,%d)" % (i,j))
		if self.get_cell_state(i,j)==Cell.KNOWN:
			raise Exception("cell (%d,%d) is KNOWN already" % (i,j))
		if self.get_cell_state(i,j)==Cell.MARKED:
			raise Exception("cell (%d,%d) is MARKED already" % (i,j))
		self.set_cell_state(i,j,Cell.MARKED)

		if self.check_win():
			self.win()
	def unmark(self,i,j):
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		if self.game_board.invalid(i,j):
			raise InvalidCoordinate("invalid coordinate: (%d,%d)" % (i,j))
		if self.get_cell_state(i,j)==Cell.KNOWN:
			raise Exception("cell (%d,%d) is KNOWN already" % (i,j))
		if self.get_cell_state(i,j)==Cell.UNKNOWN:
			raise Exception("cell (%d,%d) is UNKNOWN" % (i,j))
		self.set_cell_state(i,j,Cell.UNKNOWN)
	
	def explore(self,i,j):
		if self.get_cell_state(i,j)!=Cell.KNOWN:
			raise Exception("cell (%d,%d) is not KNOWN, cannot explore yet" % (i,j))
		if self.get_cell_value(i,j)<=0:
			raise Exception("cell (%d,%d) must has positive number" % (i,j))
		l=self.game_board.get_neighbours(i,j)
		marked_ct=0
		for ti,tj in l:
			if self.get_cell_state(ti,tj)==Cell.MARKED:
				marked_ct+=1
		if marked_ct!=self.get_cell_value(i,j):
			raise NotReadyToExplore("number of cell (%d,%d)'s marked neighbours does not agree with its value" % (i,j))
		for ti,tj in l:
			if self.get_cell_state(ti,tj)==Cell.UNKNOWN:
				self.dig(ti,tj)
	def __str__(self):
		if self.state==GameLogic.RUN:
			return str(self.game_board)
		return ""
	def cheat(self):
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		res=""
		for i in range(self.row):
			for j in range(self.col):
				res+="%3d" % self.game_board.board[i][j].val
			res+="\n"
		return res
class LoaderSaver:
	def save_to_file(self,gl,f):
		pickle.dump(gl,f)
	def save_to_str(self,gl):
		return pickle.dumps(gl)
	def load_from_file(self,f):
		return pickle.load(f)
	def load_from_str(self,s):
		return pickle.load(s)

def usage():
	print "welcome to pyms"
	print ""
	print "\tnew <row> <col> <num>		start a new game"
	print "\tdig <row> <col>			dig cell (<row>,<col>)"
	print "\tmark <row> <col>		mark cell (<row>,<col>)"
	print "\tunmkar <row> <col>		unmark cell (<row>,<col>)"
	print "\texplore <row> <col>		explore neighbours of cell (<row>,<col>)"
	print "\tload <file name> 		load from file"
	print "\tsave <file name>		save to file"
	print "\texit				exit game"

if __name__=="__main__":
	usage()
	game=GameLogic()
	sl=LoaderSaver()
	while 1:
		print str(game)
		sys.stdout.write(">> ")
		line=sys.stdin.readline()
		try:
			if line.startswith("new"):
				l=line.split()
				if len(l)!=4:raise Exception("numer of arguments is not correct for \"new\"")
				row=int(l[1])
				col=int(l[2])
				num=int(l[3])
				game.new_game(row,col,num)

			elif line.startswith("dig"):
				l=line.split()
				if len(l)!=3:raise Exception("numer of arguments is not correct for \"dig\"")
				row=int(l[1])
				col=int(l[2])
				game.dig(row,col)
			elif line.startswith("mark"):
				l=line.split()
				if len(l)!=3:raise Exception("numer of arguments is not correct for \"mark\"")
				row=int(l[1])
				col=int(l[2])
				game.mark(row,col)
			elif line.startswith("unmark"):
				l=line.split()
				if len(l)!=3:raise Exception("numer of arguments is not correct for \"unmark\"")
				row=int(l[1])
				col=int(l[2])
				game.unmark(row,col)
			elif line.startswith("explore"):
				l=line.split()
				if len(l)!=3:raise Exception("numer of arguments is not correct for \"explore\"")
				row=int(l[1])
				col=int(l[2])
				game.explore(row,col)
			elif line.startswith("load"):
				l=line.split()
				if len(l)!=2:raise Exception("numer of arguments is not correct for \"load\"")
				game=sl.load_from_file(file(l[1]))
			elif line.startswith("save"):
				l=line.split()
				if len(l)!=2:raise Exception("numer of arguments is not correct for \"save\"")
				sl.save_to_file(game,file(l[1],"w"))
			elif line.startswith("cheat"):
				print(game.cheat())
			elif line.startswith("exit"):
				break
			else: raise Exception("unknown command: %s" % line)
		except Exception as e:
			print e
