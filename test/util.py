#!/usr/bin/python
import sys
sys.path.append("../")
import ms
import traceback
def print_to_stderr(s):
	if s[-1]!='\n':s+='\n'
	sys.stderr.write(s)
def test_no_except(func):
	try:
		func()
	except Exception as e:
		print_to_stderr( "Fail when calling \"%s\"" % func.__name__)
		print_to_stderr( "Encounter %s when creating GameLogic" % e.__class__.__name__)
		traceback.print_to_stderr(_tb(sys.exc_info()[2]))
		exit(-1)
	
def test_except(func,wanted_exc):
	exc_name="No Exception"
	try:
		func()
	except Exception as e:
		exc_name=e.__class__.__name__
	if exc_name!=wanted_exc:
		print_to_stderr( "Fail when callinag \"%s\"" % func.__name__)
		print_to_stderr( "Want %s, %s encountered" % (wanted_exc,exc_name))
		exit(-1)
def test_and_validate(func,validate):
	test_no_except(func)
	if not validate():
		print_to_stderr( "Fail when callinag \"%s\"" % func.__name__)
		print_to_stderr( "Validation function returns False")
		exit(-1)
def check_board_state(gl,exp):
	K=ms.Cell.KNOWN
	U=ms.Cell.UNKNOWN
	M=ms.Cell.MARKED
	board=gl.game_board.board
	for i in range(gl.row):
		for j in range(gl.col):
			if board[i][j].state != exp[i][j]:
				return False
	return True
def quiet(flag=True):	
	global __stdout__
	if flag:
		__stdout__=sys.stdout
		try:
			sys.stdout=file("/dev/null","w")
		except:
			sys.stdout=file("nul","w")
	else:
		if __stdout__==None:return
		sys.stdout=__stdout__
		__stdout__=None

