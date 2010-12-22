#!/usr/bin/python
import sys,random,pickle
import traceback,time
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
class UnknownMode(Exception):
	pass
class ForbiddenOperation(Exception):
	pass
class UnknownTurn(Exception):
	pass
class NotMyTurn(Exception):
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


class Player:
	def __init__(self,name,gl):
		self.score=0
		self.name=name
		self.gl=gl
class Human(Player):
	def __init__(self,name,gl):
		Player.__init__(self,name,gl)
	def make_move(self,i,j):
		if self.gl.turn != self: raise NotMyTurn()
		self.gl.dig(i,j)

class AI(Player):
	def __init__(self,name,gl):
		Player.__init__(self,name,gl)
	def make_move(self):
		time.sleep(1)
		if self.gl.turn != self: raise NotMyTurn()
		for i in range(self.gl.row):
			for j in range(self.gl.col):
				if self.gl.get_cell_state(i,j)==Cell.UNKNOWN:
					self.gl.dig(i,j)
					return
					

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
	NORMAL=0
	COMPETE=1
	def __init__(self,mode=None):
		self.state=GameLogic.STOP
		if mode==None:mode=self.NORMAL
		self.set_mode(mode)
	def reset_mode(self):
		"""
			pickle cannot dump instance methods.
			Call this every time before save
			Call set_mode every time after load
		"""
		self.dig=None
		self.mark=None
		self.unmark=None
		self.explore=None
		self.check_win=None
		self.check_lose=None
		self.win=None
		self.lose=None

	def set_mode(self,mode):
		self.mode=mode
		if mode==self.NORMAL:
			self.dig=self.normal_dig
			self.mark=self.normal_mark
			self.unmark=self.normal_unmark
			self.explore=self.normal_explore
			self.check_win=self.normal_check_win
			self.check_lose=self.normal_check_lose
			self.win=self.normal_win
			self.lose=self.normal_lose
		elif mode==self.COMPETE:
			self.dig=self.compete_dig
			self.mark=self.compete_mark
			self.unmark=self.compete_unmark
			self.explore=self.compete_explore
			self.check_win=self.compete_check_win
			self.check_lose=self.compete_check_lose
			self.win=self.compete_win
			self.lose=self.compete_lose
		else: raise UnknownMode()
	def compete_sitch_turn(self):
		if self.turn==self.player1:
			self.turn=self.player2
		elif self.turn==self.player2:
			self.turn=self.player1
		else: raise UnknownTurn()

	def compete_dig(self,i,j):
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
		else: self.set_cell_state(i,j,Cell.KNOWN)
		
		if self.get_cell_value(i,j)!=Cell.MINE: 
			self.compete_sitch_turn()
			print "switche turn to %s" % self.turn.name
		else:
			self.turn.score+=1
		if self.check_win():
			self.win()

	def compete_mark(self,i,j):
		raise ForbiddenOperation()
	def compete_unmark(self,i,j):
		raise ForbiddenOperation()
	def compete_explore(self,i,j):
		raise ForbiddenOperation()
	def compete_check_win(self):
		for i in range(self.row):
			for j in range(self.col):
				if self.get_cell_state(i,j)!=Cell.KNOWN:
					return False
		return True
	def compete_check_lose(self,i,j):
		raise ForbiddenOperation()
	def compete_win(self):
		self.state=GameLogic.WIN
		s1,s2=self.player1.score,self.player2.score
		winner=None
		if s1 > s2: winner=self.player1
		elif s1 < s2: winner=self.player2
		print str(self)
		print "final score: %d - %d" % (s1,s2)
		if winner!=None:
			print "Congratulations! %s Win!!\n" % winner.name
		else:
			print "draw : )"
	def compete_lose(self):
		raise ForbiddenOperation()

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

	def flood_fill_dig(self,i,j):
		if self.game_board.invalid(i,j) or self.get_cell_state(i,j)==Cell.KNOWN:
			return
		self.set_cell_state(i,j,Cell.KNOWN)
		if self.get_cell_value(i,j)==0:
			for di in range(-1,2):
				for dj in range(-1,2):
					self.flood_fill_dig(i+di,j+dj)

	def new_game(self,row,col,num,mine_loc=None):
		self.state=GameLogic.RUN
		self.row=row
		self.col=col
		self.game_board=Board(row,col,num,mine_loc=mine_loc)
		if self.mode==GameLogic.COMPETE:
			self.player1=Human("humam",self)
			self.player2=AI("AI",self)
			self.turn=self.player1

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
#	above part are independent form mode

	def normal_lose(self):
		self.reveal_all()
		print str(self)
		self.state=GameLogic.LOSE
		print "You Lose...\n Better luck next time!\n"

	def normal_win(self):
		self.reveal_all()
		print str(self)
		self.state=GameLogic.WIN
		print "Congratulations! You Win!!\n"

	def normal_check_win(self):
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
	def normal_check_lose(self):
		"""
			return true if some MINE cell is KNOWN
		"""
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		for i in range(self.row):
			for j in range(self.col):
				if self.get_cell_value(i,j)==Cell.MINE and self.get_cell_state(i,j)==Cell.KNOWN:
					return True;
		return False

	def normal_dig(self,i,j):
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
		else: self.set_cell_state(i,j,Cell.KNOWN)

		if self.check_lose():self.lose()
		elif self.check_win():self.win()


	def normal_mark(self,i,j):
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		if self.game_board.invalid(i,j):
			raise InvalidCoordinate("invalid coordinate: (%d,%d)" % (i,j))
		if self.get_cell_state(i,j)==Cell.KNOWN:
			raise Exception("cell (%d,%d) is KNOWN already" % (i,j))
		if self.get_cell_state(i,j)==Cell.MARKED:
			raise Exception("cell (%d,%d) is MARKED already" % (i,j))
		self.set_cell_state(i,j,Cell.MARKED)

		if self.check_win():self.win()

	def normal_unmark(self,i,j):
		if self.state!=GameLogic.RUN:
			raise GameNotRunning("Game is not running")
		if self.game_board.invalid(i,j):
			raise InvalidCoordinate("invalid coordinate: (%d,%d)" % (i,j))
		if self.get_cell_state(i,j)==Cell.KNOWN:
			raise Exception("cell (%d,%d) is KNOWN already" % (i,j))
		if self.get_cell_state(i,j)==Cell.UNKNOWN:
			raise Exception("cell (%d,%d) is UNKNOWN" % (i,j))
		self.set_cell_state(i,j,Cell.UNKNOWN)
	
	def normal_explore(self,i,j):
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
class LoaderSaver:
	def save_to_file(self,gl,f):
		gl.reset_mode()
		pickle.dump(gl,f)
		gl.set_mode(gl.mode)
	def load_from_file(self,f):
		gl=pickle.load(f)
		gl.set_mode(gl.mode)
		return gl

def normal_mode_usage():
	print 	"	new <row> <col> <num>				start a new game"
	print 	"	dig <row> <col>					dig cell (<row>,<col>)"
	print 	"	mark <row> <col>				mark cell (<row>,<col>)"
	print 	"	unmkar <row> <col>				unmark cell (<row>,<col>)"
	print 	"	explore <row> <col>				explore neighbours of cell (<row>,<col>)"		
	print 	"	load <file name> 				load from file"
	print 	"	save <file name>				save to file"
	print 	"	exit						exit game"
def compete_mode_usage():
	print 	"	new <row> <col> <num>				start a new game"
	print 	"	dig <row> <col>					dig cell (<row>,<col>)"
	print 	"	load <file name> 				load from file"
	print 	"	save <file name>				save to file"
	print 	"	exit						exit game"
def choose_mode_usage():
	print 	"	normal						start normal mode"
	print 	"	compete 					start compete mode"
	print 	"	exit						exit"
def play_normal_mode():
	"""
		play normal mode in text UI
	"""
	global sl
	game=GameLogic(GameLogic.NORMAL)
	while 1:
		normal_mode_usage()
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
			traceback.print_tb(sys.exc_info()[2])

def play_compete_mode():
	"""
		play compete mode in text UI
	"""
	global sl
	game=GameLogic(GameLogic.COMPETE)
	while 1:
		compete_mode_usage()
		print str(game)
		player=game.turn
		if player!=None:
			print "%s's turn:\n" % player.name
		sys.stdout.write(">> ")
		if player.__class__==AI:
			player.make_move()
			continue
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
			else: raise Exception("unknown command: %s" % line)
		except Exception as e:
			print e
			traceback.print_tb(sys.exc_info()[2])

if __name__=="__main__":
	sl=LoaderSaver()
	while 1:
		choose_mode_usage()
		line=sys.stdin.readline()
		line=line[:-1]
		try:
			if line=="normal":
				play_normal_mode()
			elif line.startswith("compete"):
				play_compete_mode()
			elif line=="exit":
				break
			else: raise Exception("Bad option: %s" % line)
		except Exception as e:
			print e
			traceback.print_tb(sys.exc_info()[2])
