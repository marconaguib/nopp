#this script plays the song and launches a ttk window with the current word highlighted

import os
import sys
import time

import pygame
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


#mother class of LRC and SRT
class Lyrics:
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "r")
        self.parseFile()
        self.file.close()
    
    def parseFile(self):
        pass
    
    def getCurrentLine(self):
        pass
    
    def getCurrentWord(self):
        pass
    
    def getCurrentText(self):
        pass

class LRC(Lyrics):
    #a LRC file has the following format:
    #[mm:ss.xx]line
    #where mm is minutes, ss is seconds, and xx is milliseconds
    #and line is a concatenation of intervals 
    #an interval has the following format:
    #<mm:ss.xx>word</mm:ss.xx>
    #where mm is minutes, ss is seconds, and xx is milliseconds
    # and word is the word to be displayed at that time
    #the first word is an exception, it has the following format:
    # word</mm:ss.xx>
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "r")
        self.parseFile()
        self.file.close()

        # self.rearrarrangeLines()
    
    def parseFile(self):
        self.lyrics = []
        for line in self.file.readlines():
            lyric = {}
            text = ""
            if line[0] == '[':
                lyric['startTime'] = self.timestampToSeconds(line[1:10])
                parts = line.split()
                parts = [parts[i:i+3] for i in range(0, len(parts), 3)]
                lyric['intervals'] = []
                for part in parts:
                    interval = {}
                    interval['startTime'] = self.timestampToSeconds(part[0][1:10])
                    interval['word'] = part[1]
                    text += part[1] + " "
                    interval['endTime'] = self.timestampToSeconds(part[2][1:10])
                    interval['duration'] = interval['endTime'] - interval['startTime']
                    lyric['intervals'].append(interval)
                lyric['text'] = text
                self.lyrics.append(lyric)

            
    def timestampToSeconds(self, timestamp):
        minutes = int(timestamp[0:2])
        seconds = int(timestamp[3:5])
        milliseconds = int(timestamp[6:8])
        return minutes * 60 + seconds + milliseconds / 1000
    
    def getCurrentLineIndex(self):
        currentTime = pygame.mixer.music.get_pos() / 1000
        if currentTime < self.lyrics[0]['startTime']:
            return 0
        for i in range(1, len(self.lyrics)):
            if currentTime < self.lyrics[i]['startTime']:
                return i-1
        return len(self.lyrics) - 1
    
    def getCurrentLine(self):
        currentTime = pygame.mixer.music.get_pos() / 1000
        #the first line is an exception
        if currentTime < self.lyrics[0]['startTime']:
            return self.lyrics[0]['text']
        for i in range(1, len(self.lyrics)):
            if currentTime < self.lyrics[i]['startTime']:
                return self.lyrics[i-1]['text']
        return self.lyrics[-1]['text']
    
    def getCurrentText(self):
        currentIndex = self.getCurrentLineIndex()
        current_sentence = self.lyrics[currentIndex]['text']
        if currentIndex == 0:
            previous_sentence = ""
        else:
            previous_sentence = self.lyrics[currentIndex-1]['text']
        if currentIndex == len(self.lyrics) - 1:
            next_sentence = ""
        else:
            next_sentence = self.lyrics[currentIndex+1]['text']
        return previous_sentence, current_sentence, next_sentence

    
    def getCurrentWord(self):
        currentLine = self.getCurrentText()
        if currentLine == None:
            return ""
        currentTime = pygame.mixer.music.get_pos() / 1000
        for interval in currentLine['intervals']:
            if interval['startTime'] > currentTime:
                return interval['word']
        return ""

class SRT(Lyrics):
    #a SRT file has the following format:
    #00.01-->00.02
    #word
    #
    #00.02-->00.03
    #word
    #
    #...
    #where the first line is the index of the subtitle
    #the second line is the start and end time of the subtitle
    #the third line is the subtitle itself
    #the fourth line is an empty line
    def __init__(self, filename):
        self.filename = filename
        self.file = open(filename, "r")
        self.parseFile()
        self.file.close()
    
    def parseFile(self):
        self.lyrics = []
        for line in self.file.readlines():
            lyric = {}
            line = line.strip()
            if line and line[0].isdigit() and "-->" in line:
                splitLine = line.split("-->")
                lyric['startTime'] = self.timestampToSeconds(splitLine[0])
                lyric['endTime'] = self.timestampToSeconds(splitLine[1])
                lyric['duration'] = lyric['endTime'] - lyric['startTime']
                lyric['text'] = ""
                self.lyrics.append(lyric)
            elif line:
                self.lyrics[-1]['text'] += line + " "

    
    def timestampToSeconds(self, timestamp):
        #timestamp is in the format of 00.003249 (ss.mmmmmmmmmmmmmm)
        separator = timestamp.find('.')
        seconds = int(timestamp[0:separator])
        milliseconds = int(timestamp[separator+1:])
        return seconds + milliseconds / 1000
    
    
    def getCurrentLineIndex(self):
        currentTime = pygame.mixer.music.get_pos() / 1000
        if currentTime < self.lyrics[0]['startTime']:
            return 0
        for i in range(1, len(self.lyrics)):
            if currentTime < self.lyrics[i]['startTime']:
                return i-1
        return len(self.lyrics) - 1
    
    def getCurrentLine(self):
        currentTime = pygame.mixer.music.get_pos() / 1000
        #the first line is an exception
        if currentTime < self.lyrics[0]['startTime']:
            return self.lyrics[0]['text']
        for i in range(1, len(self.lyrics)):
            if currentTime < self.lyrics[i]['startTime']:
                return self.lyrics[i-1]['text']
        return self.lyrics[-1]['text']
    
    def getCurrentText(self):
        currentIndex = self.getCurrentLineIndex()
        current_sentence = self.lyrics[currentIndex]['text']
        if currentIndex == 0:
            previous_sentence = ""
        else:
            previous_sentence = self.lyrics[currentIndex-1]['text']
        if currentIndex == len(self.lyrics) - 1:
            next_sentence = ""
        else:
            next_sentence = self.lyrics[currentIndex+1]['text']
        return previous_sentence, current_sentence, next_sentence
    

#tkinter window for displaying the lyrics
class LRCWindow(tk.Toplevel):
    def __init__(self, master, lyricsPath):
        super().__init__(master)
        self.master = master
        #create the LRC object
        if lyricsPath[-4:] == ".srt":
            self.lrc = SRT(lyricsPath)
        elif lyricsPath[-4:] == ".lrc":
            self.lrc = LRC(lyricsPath)
        self.title("Lyrics")
        self.geometry("1500x500")
        self.configure(background='black')
        self.lrcLabel = tk.Text(self, bg="black", fg="grey", font=("Helvetica", 30))
        self.lrcLabel.pack(expand=True, fill="both")
        self.updateLRC()

    #updates the lrc label with the current line
    def updateLRC(self):
        self.lrcLabel.configure(state="normal")
        self.lrcLabel.delete("1.0", "end")

        prev_line, current_line, next_line = self.lrc.getCurrentText()
        # print(prev_line, current_line, next_line)
        self.lrcLabel.insert("1.0", "\n\n" + prev_line + "\n\n" + current_line + "\n\n" + next_line)

        #get the index of the end of the previous line
        index1 = str(len(prev_line) + 2) + ".0"
        #get the index of the end of the current line
        index2 = str(len(prev_line) + len(current_line) + 2) + ".0"

        self.lrcLabel.configure(state="disabled")
        self.lrcLabel.tag_configure("center", justify="center")
        self.lrcLabel.tag_add("center", "1.0", "end")

        #only highlight the current line (between index1 and index2)
        self.lrcLabel.tag_configure("highlight", foreground="white")
        self.lrcLabel.tag_add("highlight", "5.0", "6.0")

        self.after(100, self.updateLRC)

#main window
class MainApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        #initialize pygame
        pygame.init()
        pygame.mixer.init()
        
        self.pack()
        self.create_widgets()

    #creates the widgets
    def create_widgets(self):
        # a button to play/stop the song
        self.playButton = ttk.Button(self, text="Play", command=self.play)
        self.playButton.pack(side="left")

        # a button to pause/unpause the song
        self.pauseButton = ttk.Button(self, text="Pause", command=self.pause)
        self.pauseButton.pack(side="left")

        # a button to show the lyrics
        self.showLRCButton = ttk.Button(self, text="Show Lyrics", command=self.showLRC)
        self.showLRCButton.pack(side="left")

        # a button to open a new song
        self.openButton = ttk.Button(self, text="Open", command=self.open)
        self.openButton.pack(side="left")


    #plays the song
    def play(self):
        pygame.mixer.music.play()
        #change the play button to a stop button
        self.playButton.configure(text="Stop", command=self.stop)

    #pauses the song
    def pause(self):
        pygame.mixer.music.pause()
        #change the pause button to an unpause button
        self.pauseButton.configure(text="Unpause", command=self.unpause)


    #stops the song
    def stop(self):
        pygame.mixer.music.stop()
        #change the stop button to a play button
        self.playButton.configure(text="Play", command=self.play)

    #unpauses the song
    def unpause(self):
        pygame.mixer.music.unpause()
        #change the unpause button to a pause button
        self.pauseButton.configure(text="Pause", command=self.pause)

    #opens a new song
    def open(self):
        #stop the current song
        self.stop()
        #open a new song
        filename = filedialog.askopenfilename(initialdir = "~/noub",title = "Select file",filetypes = (("mp3 files","*.mp3"),("all files","*.*")))
        self.songPath = filename
        pygame.mixer.music.load(filename)

    #shows the lyrics window
    def showLRC(self):
        self.lrcWindow = LRCWindow(self.master, self.songPath.replace(".mp3", ".srt"))

#main function
def main():
    #create the root window
    root = tk.Tk()
    root.title("Music Player")
    root.geometry("800x500")
    root.configure(background='black')


    #create the main application
    app = MainApplication(root)

    #run the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
