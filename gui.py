#!/usr/bin/python
import ms
from Tkinter import *
from threading import Thread
import ImageTk,Image,tkSimpleDialog,tkMessageBox,tkFileDialog
import traceback,time
from threading import Thread
class AIPlayerHandler(Thread):
	def __init__(self,gl,player):
		Thread.__init__(self)
		self.gl=gl
		self.player=player
	def run(self):
		global game
		print "ai handler starts"
		try:
			while self.gl and self.gl.state==ms.GameLogic.RUN:
				if self.gl.turn == self.player:
					self.player.make_move()
					game.update_gui()
		except NameError:
			pass

class MineSweeper:
	class StatusBar(Frame):
		def __init__(self,master):
			Frame.__init__(self,master)
			self.label=Label(self,bd=1,relief=SUNKEN,anchor=W)
			self.label.pack(fill=X)
		
	class NewGameDialog(tkSimpleDialog.Dialog):
		def body(self,master):
			Label(master,text="Row:").grid(row=0,column=0)
			Label(master,text="Column:").grid(row=1,column=0)
			Label(master,text="Mine Number:").grid(row=2,column=0)
			self.e1=Entry(master)
			self.e1.grid(row=0,column=1)
			self.e1.insert(0,"15")
			self.e2=Entry(master)
			self.e2.grid(row=1,column=1)
			self.e2.insert(0,"15")
			self.e3=Entry(master)
			self.e3.grid(row=2,column=1)
			self.e3.insert(0,"30")
			self.mode=IntVar()
			self.r1=Radiobutton(master,text="normal",variable=self.mode,value=ms.GameLogic.NORMAL)
			self.r2=Radiobutton(master,text="compete",variable=self.mode,value=ms.GameLogic.COMPETE)
			self.r1.grid(row=3,column=0)
			self.r2.grid(row=3,column=1)
			self.p1=StringVar()
			self.p2=StringVar()
			self.p1.set("Human")
			self.p2.set("AI")
			self.o1=OptionMenu(master,self.p1,"Human","AI")
			self.o2=OptionMenu(master,self.p2,"Human","AI")
			self.o1.grid(row=4,column=0)
			self.o2.grid(row=4,column=1)
			return self.e1
		def apply(self):
			self.result=(self.e1.get(),self.e2.get(),self.e3.get(),self.mode.get(),self.p1.get(),self.p2.get())
	def load_img(self,path):
		return ImageTk.PhotoImage(Image.open(path))
	def __init__(self,master):
		self.root=master
		self.frame=None
		self.gl=ms.GameLogic(ms.GameLogic.NORMAL)
		self.sl=ms.LoaderSaver()
		self.buttons=None
		menu=Menu(master)
		master['menu']=menu
		game_menu=Menu(menu)
		menu.add_cascade(label="Game",menu=game_menu)
		game_menu.add_command(label="New Game",command=self.click_new_game)
		game_menu.add_command(label="Save",command=self.click_save)
		game_menu.add_command(label="Load",command=self.click_load)
		game_menu.add_command(label="Exit",command=master.quit)
		self.images={
			"UNKNOWN":self.load_img("./resource/UNKNOWN.png"),
			"MARKED":self.load_img("./resource/MARKED.png"),
			"MINE":self.load_img("./resource/MINE.png"),
			"0":self.load_img("./resource/0.png"),
			"1":self.load_img("./resource/1.png"),
			"2":self.load_img("./resource/2.png"),
			"3":self.load_img("./resource/3.png"),
			"4":self.load_img("./resource/4.png"),
			"5":self.load_img("./resource/5.png"),
			"6":self.load_img("./resource/6.png"),
			"7":self.load_img("./resource/7.png"),
			"8":self.load_img("./resource/8.png"),
		}
		self.mouse_state=0
		self.statusbar=MineSweeper.StatusBar(master)
		self.statusbar.pack(fill=X,side=BOTTOM)
		#	gui is ready by now
		self.new_game(15,15,30)
	def update_each_cell(self):
		gl=self.gl
		row=gl.row
		col=gl.col
		f=self.frame
		UNKNOWN=ms.Cell.UNKNOWN
		KNOWN=ms.Cell.KNOWN
		MARKED=ms.Cell.MARKED
		MINE=ms.Cell.MINE

		for i in range(row):
			for j in range(col):
				b=self.buttons[i][j]
				b['bd']=1
				state=gl.get_cell_state(i,j)
				value=gl.get_cell_value(i,j)
				if state==UNKNOWN:
					if b['image']!=self.images["UNKNOWN"]:
						b['image']=self.images["UNKNOWN"]
				elif state==KNOWN:
					b['relief']=SUNKEN
					if value==MINE:
						if b['image']!=self.images["MINE"]:
							b['image']=self.images["MINE"]
					else: 
						if b['image']!=self.images[str(value)]:
							b['image']=self.images[str(value)]
				elif state==MARKED:
					if b['image']!=self.images["MARKED"]:
						b['image']=self.images["MARKED"]
		f.pack(side=TOP)
	def construct_new_frame(self):
		gl=self.gl
		row=gl.row
		col=gl.col
		f=self.frame

		if f!=None: f.destroy()	
		f=self.frame=Frame(self.root)
		self.buttons=[[Button(f) for i in range(col)] for j in range(row)]
		for i in range(row):
			for j in range(col):
				b=self.buttons[i][j]
				b.bind("<Button-1>",self.left_click)
				b.bind("<ButtonRelease-1>",self.left_release)
				b.bind("<Button-3>",self.right_click)
				b.bind("<ButtonRelease-3>",self.right_release)
				b.grid(row=i,column=j)
	def update_statusbar(self):
		msg=""
		if self.gl.mode==ms.GameLogic.NORMAL:
			msg+="normal"
		elif self.gl.mode==ms.GameLogic.COMPETE:
			msg+="compete"
		msg+="\t"
		if self.gl.mode==ms.GameLogic.COMPETE:
			msg+="%s" % self.gl.turn.name
			msg+="\t"
			msg+="%d-%d" % (self.gl.player1.score,self.gl.player2.score)
		self.statusbar.label['text']=msg
	def update_gui(self):
		if self.buttons==None: self.construct_new_frame()
		self.update_each_cell()
		msg=None
		if self.gl.state==ms.GameLogic.WIN:
			if self.gl.mode==ms.GameLogic.NORMAL:
				msg="You Win!\nCongradulations!"
			elif self.gl.mode==ms.GameLogic.COMPETE:
				p1,p2=self.gl.player1,self.gl.player2
				s1,s2=p1.score,p2.score
				msg="Final score: %d - %d\n" % (s1,s2)
				if s1 > s2: msg+="%s wins!" % p1.name
				elif s1 < s2: msg+="%s wins" % p2.name
				else: msg+="Draw : )"
		elif self.gl.state==ms.GameLogic.LOSE:
			if self.gl.mode==ms.GameLogic.NORMAL:
				msg="You Lose.\nBetter luck next time!"
		self.update_statusbar()
		if self.gl.last_move:
			last_i,last_j=self.gl.last_move
		if msg: tkMessageBox.showinfo("Result",msg)

	def sunken_neighbour_widgets(self,w):
		i,j=self.button_location(w)
		gl=self.gl
		l=gl.game_board.get_neighbours(i,j)
		for i,j in l:
			if gl.get_cell_state(i,j)==ms.Cell.UNKNOWN:
				self.buttons[i][j]['relief']=SUNKEN
	def raised_neighbour_widgets(self,w):
		i,j=self.button_location(w)
		gl=self.gl
		l=gl.game_board.get_neighbours(i,j)
		for i,j in l:
			if gl.get_cell_state(i,j)==ms.Cell.UNKNOWN:
				self.buttons[i][j]['relief']=RAISED
	def button_location(self,w):
		gl=self.gl
		row=gl.row
		col=gl.col
		for i in range(row):
			for j in range(col):
				if self.buttons[i][j]==w:
					return (i,j)
	def left_click_widget(self,w):
		i,j=self.button_location(w)
		self.dig(i,j)
	def left_right_click_widget(self,w):
		i,j=self.button_location(w)
		self.explore(i,j)
	def right_click_widget(self,w):
		i,j=self.button_location(w)
		self.toggle(i,j)
	def left_click(self,e):
		if(self.mouse_state==0):
			self.mouse_state=1
		elif(self.mouse_state==2):
			self.mouse_state=3
			self.sunken_neighbour_widgets(e.widget)

	def left_release(self,e):
		if(self.mouse_state==1):
			self.mouse_state=0
			self.left_click_widget(e.widget)
		elif(self.mouse_state==3):
			self.mouse_state=4
			self.raised_neighbour_widgets(e.widget)
			self.left_right_click_widget(e.widget)
		elif(self.mouse_state==4):
			self.mouse_state=0

	def right_click(self,e):
		if(self.mouse_state==0):
			self.mouse_state=2
			self.right_click_widget(e.widget)
		elif(self.mouse_state==1):
			self.mouse_state=3
			self.sunken_neighbour_widgets(e.widget)

	def right_release(self,e):
		if(self.mouse_state==2):
			self.mouse_state=0
		elif(self.mouse_state==3):
			self.mouse_state=4
			self.raised_neighbour_widgets(e.widget)
			self.left_right_click_widget(e.widget)
		elif(self.mouse_state==4):
			self.mouse_state=0
	def clear_ai_handler(self):
		if self.gl.player1.__class__==ms.AI:
			self.player1_handler._Thread__stop
		if self.gl.player2.__class__==ms.AI:
			self.player2_handler._Thread__stop
	def set_ai_handler(self):
		if self.gl.player1.__class__==ms.AI:
			h=AIPlayerHandler(self.gl,self.gl.player1)
			self.player1_handler=h
			h.daemon=True
			h.start()
		if self.gl.player2.__class__==ms.AI:
			h=AIPlayerHandler(self.gl,self.gl.player2)
			self.player2_handler=h
			h.daemon=True
			h.start()
	def new_game(self,row,col,num,mine_loc=None,mode=ms.GameLogic.NORMAL,player1=None,player2=None):
		if mode!=self.gl.mode:
			self.gl=ms.GameLogic(mode)
		if player1=="Human" or player1==None:
			player1=ms.Human("player1(Human)",self.gl)
		elif player1=="AI":
			player1=ms.AI("player1(AI)",self.gl)
		else: raise Exception("Unknown player")
		if player2=="Human":
			player2=ms.Human("player2(Human)",self.gl)
		elif player2=="AI" or player2==None:
			player2=ms.AI("player2(AI)",self.gl)
		else: raise Exception("Unknown player")
		self.gl.new_game(row,col,num,mine_loc=mine_loc,player1=player1,player2=player2)
		if mode==ms.GameLogic.COMPETE:
			self.set_ai_handler()
		self.buttons=None
		self.update_gui()
	def click_save(self):
		f=tkFileDialog.asksaveasfile()
		self.sl.save_to_file(self.gl,f)
		f.close()
		print "save complete"
	def click_load(self):
		f=tkFileDialog.askopenfile()
		if self.gl.mode==ms.GameLogic.COMPETE:
			self.clear_ai_handler()
		self.gl=self.sl.load_from_file(f)
		f.close()
		if self.gl.mode==ms.GameLogic.COMPETE:
			self.set_ai_handler()
		self.update_gui()
	def click_new_game(self):
		d=self.NewGameDialog(self.frame)
		(row,col,num,mode,p1,p2)=d.result

		try:
			row=int(row)
			col=int(col)
			num=int(num)
			self.gl.new_game(row,col,num)
			self.new_game(row,col,num,mode=mode,player1=p1,player2=p2)
		except Exception as e:
			print e
			traceback.print_tb(sys.exc_info()[2])
			tkMessageBox.showwarning("Warning","invalid input, please try again")
	def dig(self,i,j):
		if self.gl.mode==ms.GameLogic.NORMAL:
			self.gl.dig(i,j)
			self.update_gui()
		else:
			if self.gl.turn.__class__==ms.Human:
				self.gl.turn.make_move(i,j)
				self.update_gui()
	def mark(self,i,j):
		self.gl.mark(i,j)
		self.update_gui()
	def unmark(self,i,j):
		self.gl.unmark(i,j)
		self.update_gui()
	def toggle(self,i,j):
		if self.gl.get_cell_state(i,j)==ms.Cell.MARKED:
			self.unmark(i,j)
		elif self.gl.get_cell_state(i,j)==ms.Cell.UNKNOWN:
			self.mark(i,j)
	def explore(self,i,j):
		self.gl.explore(i,j)
		self.update_gui()

def initialize():
	global game,root
	root=Tk()
	root.title("pyms")
	root.resizable(width=FALSE,height=FALSE)
	game=MineSweeper(root)

def start_gui():
	global root
	root.mainloop()

if __name__=="__main__":
	initialize()
	start_gui()
