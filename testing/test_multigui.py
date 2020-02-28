import tkinter as tk

class Win1:
	def __init__(self, master):
		self.master = master
		self.master.geometry("400x400")
		self.frame = tk.Frame(self.master)
		self.butnew("Click to open Window 2", "2", Win2)
		self.butnew("Click to open Window 3", "3", Win3)
		self.frame.pack()

	def butnew(self, text, number, _class):
		tk.Button(self.frame, text = text, command= lambda: self.new_window(number, _class)).pack()

	def new_window(self, number, _class):
		self.new = tk.Toplevel(self.master)
		_class(self.new, number)

class Win2:
	def __init__(self, master, number):
		self.master = master
		self.master.geometry("200x200+200+200")
		self.frame = tk.Frame(self.master)
		self.quit = tk.Button(self.frame, text = f"Quit this window n. {number}", command = self.close_window)
		self.quit.pack()
		self.frame.pack()

	def close_window(self):
		self.master.destroy()

class Win3:
	def __init__(self, master, number):
		self.master = master
		self.master.geometry("200x200+400+400")
		self.frame = tk.Frame(self.master)
		self.quit = tk.Button(self.frame, text = f"Quit this window n. {number}", command = self.close_window)
		self.quit.pack()
		self.label = tk.Label(self.frame, text="THIS IS ONLY IN THE THIRD WINDOW")
		self.label.pack()
		self.frame.pack()


	def close_window(self):
		self.master.destroy()

root = tk.Tk()
app = Win1(root)
root.mainloop()
