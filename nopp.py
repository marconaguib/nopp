import os
import argparse
import pygame
import tkinter as tk
from tkinter import ttk
import random

directory = os.path.dirname(os.path.realpath(__file__))
os.chdir(directory)

def tk_gui(themes):

    #create the main window
    root = tk.Tk()
    root.title("N'oubliez pas les paroles !")

    pygame.mixer.init()

    #use a beautiful theme
    style = ttk.Style()
    style.theme_use("clam")


    #create the main frame
    mainframe = ttk.Frame(root, padding="3 3 12 12")
    mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    #create the theme frame
    theme_frame = ttk.Frame(mainframe, padding="3 3 12 12")
    theme_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(0, weight=1)

    #create the song frame
    song_frame = ttk.Frame(mainframe, padding="3 3 12 12")
    song_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
    mainframe.columnconfigure(0, weight=1)
    mainframe.rowconfigure(1, weight=1)

    #randomly select 4 theme names
    themes = dict(random.sample(themes.items(), 4))
    theme_names = list(themes.keys())

    #display the themes
    for i, theme in enumerate(themes):
        #make sure all buttons have the "!button{}".format(i) name
        ttk.Button(theme_frame, text="{}. {} ({} points)".format(i+1, theme, themes[theme]["points"]), name="!button{}".format(i)).grid(column=i, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        theme_frame.columnconfigure(i, weight=1)
        theme_frame.rowconfigure(0, weight=1)

    #on theme button click
    def theme_click(event):
        #get the theme number
        theme = int(event.widget["text"][0])
        #select the theme
        theme_name = theme_names[theme-1]
        
        #replace the theme buttons with a label with the theme name
        for i in range(4):
            theme_frame.children["!button{}".format(i)].destroy()
        ttk.Label(theme_frame, text="{}. {} ({} points)".format(theme, theme_name, themes[theme_name]["points"]), name="!label0").grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        theme_frame.columnconfigure(0, weight=1)
        theme_frame.rowconfigure(0, weight=1)

        #randomly select 2 songs
        songs = random.sample(themes[theme_name]["chansons"], 2)

        #enable the song buttons
        for i in range(2):
            song_frame.children["!button{}".format(i)].state(["!disabled"])
        
        #display the songs
        for i, song in enumerate(songs):
            #create the song button
            song_frame.children["!button{}".format(i)]["text"] = "{}. {}".format(i+1, song)
            song_frame.columnconfigure(i, weight=1)
            song_frame.rowconfigure(0, weight=1)

    #by default, the song buttons are disabled
    for i in range(2):
        ttk.Button(song_frame, text="{}. ".format(i+1), name="!button{}".format(i), state=["disabled"]).grid(column=i, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        song_frame.columnconfigure(i, weight=1)
        song_frame.rowconfigure(0, weight=1)

    def song_click(event):
        #if the song button is disabled, do nothing
        if "disabled" in event.widget.state():
            return

        #select the song
        song_name = event.widget["text"][3:]
        
        #replace the song buttons with a label with the song name
        for i in range(2):
            song_frame.children["!button{}".format(i)].destroy()
        ttk.Label(song_frame, text=song_name).grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        song_frame.columnconfigure(0, weight=1)
        song_frame.rowconfigure(0, weight=1)

        #play the song
        theme_name = theme_names[int(theme_frame.children["!label0"]["text"][0])-1]
        #directory name is the only one that starts with the theme name
        for directory in os.listdir("NOPP"):
            if directory.startswith(theme_name):
                theme_name = directory
                break
        song_fname = "NOPP/{}/{}_trimmed.mp3".format(directory, song_name)
        pygame.mixer.music.load(song_fname)
        pygame.mixer.music.play()

        #show the text found in the _trimmed.txt file
        with open(song_fname[:-4]+".txt", "r") as f:
            text = f.read()
        
        #create a new Text widget
        text_widget = tk.Text(song_frame, width=50, height=30)
        text_widget.insert(tk.END, text)
        text_widget.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        

        
    #bind the theme buttons
    for i, theme in enumerate(themes):
        theme_frame.children["!button{}".format(i)].bind("<Button-1>", theme_click)

    #bind the song buttons
    for i in range(2):
        song_frame.children["!button{}".format(i)].bind("<Button-1>", song_click)
    


    #start the main loop
    root.mainloop()


def main():
    # Get the NOPP directory from arg -d
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="Directory to NOPP", default="NOPP")
    args = parser.parse_args()

    #get names of subdirectories of NOPP
    names = os.listdir(args.directory)

    #separate names as a dict of (theme: points) separated by a comma
    themes = {}
    for name in names:
        theme, points = name.split(",")
        #get names of files in each subdirectory that end with _trimmed.mp3 and replace _trimmed.mp3 with nothing
        files = [file[:-12] for file in os.listdir(os.path.join(args.directory, name)) if file.endswith("_trimmed.mp3")]
        themes[theme] = {}
        themes[theme]["points"] = points
        themes[theme]["chansons"] = files

    #simple_gui()
    tk_gui(themes)

if __name__ == "__main__":
    main()