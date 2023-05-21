#this script makes a GUI to trim mp3 files
#it uses the python module pydub to trim the mp3 files
#it also features an integrated mp3 player with a slider to show the current position of the song
#it uses the python module pygame to play the mp3 files
#it uses the python module tkinter to make the GUI

#this script is written by me, and is free to use, modify and distribute
#I am not responsible for any damage caused by this script
import pygame
from pydub import AudioSegment
from tkinter import *
from tkinter.filedialog import askopenfilename 
from timeit import default_timer as timer


class App:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.frame.pack()
        self.master.title("MP3 Trimmer")
        self.master.geometry("1200x1000")
        self.master.resizable(0,0)
        self.master.configure(background="white")
        self.master.bind("<Return>", self.trim)
        self.master.bind("<Escape>", self.quit)
        self.master.bind("<Control-o>", self.open)
        self.master.bind("<Control-p>", self.play)
        self.master.bind("<Control-m>", self.pause)

        #make an adaptive vertcal space
        self.label1 = Label(self.master, text="Start time (in seconds):", bg="white")
        self.label1.place(x=10, y=10)
        self.label2 = Label(self.master, text="End time (in seconds):", bg="white")
        self.label2.place(x=10, y=40)
        self.label5 = Label(self.master, text="Pause time (in seconds):", bg="white")
        self.label5.place(x=10, y=130)
        self.label6 = Label(self.master, text="Loaded song:", bg="white")
        self.label6.place(x=10, y=160)
        self.label7 = Label(self.master, text="Trimmed song:", bg="white")
        self.label7.place(x=10, y=190)
        
        self.entry1 = Entry(self.master, width=10)
        self.entry1.place(x=150, y=10)
        self.entry2 = Entry(self.master, width=10)
        self.entry2.place(x=150, y=40)

        self.button3 = Button(self.master, text="Open", command=self.open)
        self.button3.place(x=10, y=220)
        self.button4 = Button(self.master, text="Play", command=self.play)
        self.button4.place(x=110, y=220)
        self.button6 = Button(self.master, text="Pause", command=self.pause)
        self.button6.place(x=210, y=220)
        self.button1 = Button(self.master, text="Trim", command=self.trim)
        self.button1.place(x=310, y=220)
        self.button5 = Button(self.master, text="Quit", command=self.quit)
        self.button5.place(x=410, y=220)


        #make a wide slider
        self.slider = Scale(self.master, from_=0, to=900, orient=HORIZONTAL, command=self.slider)
        self.slider.place(x=10, y=300)
        self.slider.config(state=DISABLED, length=780)
        

        #make a scrollable text box that enters in the window
        self.text = Text(self.master, width=97, height=15)
        self.text.place(x=10, y=400)

    def trim(self, event=None):
        try:
            start = float(self.entry1.get())
            end = float(self.entry2.get())
            file = self.file_name
            song = AudioSegment.from_mp3(file)
            trimmed = song[start*1000:end*1000]
            trimmed.export("{0}_trimmed.mp3".format(file[:-4]), format="mp3")
            self.label7.config(text="Trimmed song: {0}_trimmed.mp3".format(file[:-4]))

            #read the text box and write it to a text file with the same name as the trimmed mp3 file
            with open(file[:-4] + "_trimmed.txt", "w") as f:
                text = self.text.get(1.0, END)
                text = self.replace_words_in_innermost_brackets(text)
                f.write(text)

        except:
            print("Error : Trim failed")
              
            
    def open(self, event=None):
        self.file_name = askopenfilename(initialdir = "~/noub/to trim",title = "Select file",filetypes = (("mp3 files","*.mp3"),("all files","*.*")))
        self.label6.config(text="Loaded song: " + self.file_name)

        #if there is a text file with the same name as the mp3 file, read it and put in the text box
        try:
            with open(self.file_name[:-4] + ".txt", "r") as f:
                self.text.delete(1.0, END)
                self.text.insert(1.0, f.read())
        except:
            print("No text file found")

    def play(self, event=None):
        try:
            song = AudioSegment.from_mp3(self.file_name)
            pygame.mixer.init()
            pygame.mixer.music.load(self.file_name)
            pygame.mixer.music.play()
            self.slider.config(state=NORMAL)
            self.slider.config(to=song.duration_seconds)
            self.slider.set(0)
        except:
            print("Error : Play failed")
            

    def pause(self, event=None):
        pygame.mixer.music.pause()
        self.slider.config(state=DISABLED)
        #put pause time in end time entry
        self.entry2.delete(0, END)
        self.entry2.insert(0, pygame.mixer.music.get_pos()/1000)
        end = timer()
        length = end - self.start
        end_time_in_song = self.slider.get() + length
        #set label to show pause time

        self.label5.config(text="Pause time (in seconds): " + str(end_time_in_song))
        #put pause time in end time entry
        self.entry2.delete(0, END)
        self.entry2.insert(0, end_time_in_song)
        
        
    def slider(self, event=None):
        pygame.mixer.music.set_pos(self.slider.get())
        #put slider position in start time entry
        self.entry1.delete(0, END)
        self.entry1.insert(0, self.slider.get())
        #start a timer
        self.start = timer()


    def quit(self, event=None):
        try:
            pygame.mixer.music.stop()
        except:
            pass
        self.master.destroy()

    def replace_words_in_innermost_brackets(self,text):
        pattern = r'<([^<>]*(?:(?:<[^<>]*>)[^<>]*)*)>'
        match = re.search(pattern, text)
        if match:
            outer_text = match.group(1)
            #get the words between brackets in the outer text
            inner_text = re.findall(r'<([^<>]*)>', outer_text)[0]
            #count words
            count = len(inner_text.split())
            #replace <...> with 4 underscores * count
            outer_text = re.sub(r'<([^<>]*)>', '____ '*count, outer_text)
            return outer_text
        else:
            return ""

root = Tk()
app = App(root)
root.mainloop()



        

