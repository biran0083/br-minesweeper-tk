#!/usr/bin/python
import ms
from Tkinter import *
import ImageTk,Image,tkSimpleDialog,tkMessageBox,tkFileDialog
class MineSweeper:
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
			return self.e1
		def apply(self):
			self.result=(self.e1.get(),self.e2.get(),self.e3.get())
	def load_img(self,path):
		return ImageTk.PhotoImage(Image.open(path))
	def __init__(self,master):
		self.root=master
		f=self.frame=Frame(master,height=200,width=200)
		self.gl=ms.GameLogic()
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
		self.new_game(15,15,30)
	def update_gui(self):
		gl=self.gl
		row=gl.row
		col=gl.col
		f=self.frame
		UNKNOWN=ms.Cell.UNKNOWN
		KNOWN=ms.Cell.KNOWN
		MARKED=ms.Cell.MARKED
		MINE=ms.Cell.MINE
		if self.buttons==None:
			#constructing new board
			f.destroy()
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
		for i in range(row):
			for j in range(col):
				b=self.buttons[i][j]
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
		self.frame.pack()
		if self.gl.state==self.gl.WIN:
			tkMessageBox.showinfo("You Win","Congradulations!")
		elif self.gl.state==self.gl.LOSE:
			tkMessageBox.showinfo("You Lose","Better luck next time!")
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

	
	def new_game(self,row,col,num):
		self.gl.new_game(row,col,num)
		self.buttons=None
		self.update_gui()
	def click_save(self):
		f=tkFileDialog.asksaveasfile()
		self.sl.save_to_file(self.gl,f)
		f.close()
	def click_load(self):
		f=tkFileDialog.askopenfile()
		self.gl=self.sl.load_from_file(f)
		f.close()
		self.update_gui()
	def click_new_game(self):
		d=self.NewGameDialog(self.frame)
		(row,col,num)=d.result
		try:
			row=int(row)
			col=int(col)
			num=int(num)
			self.gl.new_game(row,col,num)
			self.new_game(row,col,num)
		except:
			tkMessageBox.showwarning("Warning","invalid input, please try again")
	def dig(self,i,j):
		self.gl.dig(i,j)
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

def start_gui():
	root=Tk()
	root.title("pyms")
	root.resizable(width=FALSE,height=FALSE)
	game=MineSweeper(root)
	root.mainloop()

if __name__=="__main__":
	start_gui()
