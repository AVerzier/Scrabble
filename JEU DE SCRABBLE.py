#--JEU DE SCRABBLE--#

import time as t
from random import sample
import json

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from ScrabbleGrid import *

# style = ttk.Style().configure("White.TButton", background="white")
# print(style.lookup("TLabel", "font"))
# style.configure("TLabel", font=("Arial", "bold", 32))
# print(style.lookup("TLabel", "font"))


class ScrPlayer():

    def __init__(self, name):
        self.name = name
        self.pts = 0
        self.letters = []

    def pick(self, stock, first=False):
        if first:
            n = 1
        else:
            n = min(7 - len(self.letters), len(stock.letters))
        newLetters = stock.pick(n)
        self.letters += newLetters

    def __str__(self):
        return self.name


class ScrStock():

    def __init__(self, lang="FR"):
        with open(f"Letters/letCount {lang}.txt") as file:
            self.letCount = eval(file.read())
        self.letters = []
        for let, nb in self.letCount.items():
            self.letters += [let] * nb

    def pick(self, n):
        newLetters = sample(self.letters, n)
        for letter in newLetters:
            self.letters.remove(letter)
            self.letCount[letter] -= 1
        return newLetters


class ScrabbleGame(ScrabbleGrid):
    """docstring for ScrabbleGame"""

    def __init__(self, *args):
        print("Loading game...")
        super().__init__(*args)

        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.attributes("-fullscreen", True)
        self.scrW = self.root.winfo_screenwidth()
        self.scrH = self.root.winfo_screenheight()

        print("Loading Images...")

        self.loadImages()

        self.frontScreen()

        self.root.mainloop()

    def loadImages(self):
        self.PilImages = {}
        self.tkImages = {}

        self.tileW = min(self.scrW * 0.80 // 15, self.scrH * 0.80 // 15)
        self.tileH = self.tileW
        board = Image.open("Images/Board/board.png")
        board.thumbnail((self.tileW * 15, self.tileH * 15))
        self.boardW, self.boardH = board.size
        self.PilImages["Board"] = board
        self.tkImages["Board"] = ImageTk.PhotoImage(board)

        for let in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            im = Image.open(f"Images/Letters/{self.lang}/{let}.png")
            im.thumbnail((self.tileW, self.tileH))
            self.PilImages[let] = im
            self.tkImages[let] = ImageTk.PhotoImage(im)

        for smallLet in "abcdefghijklmnopqrstuvwxyz":
            im = Image.open(f"Images/Letters/{self.lang}/Blanks/{smallLet}.png")
            im.thumbnail((self.tileW, self.tileH))
            self.PilImages[smallLet] = im
            self.tkImages[smallLet] = ImageTk.PhotoImage(im)

        im = Image.open(f"Images/Letters/{self.lang}/Blanks/blank.png")
        im.thumbnail((self.tileW, self.tileH))
        self.PilImages["?"] = im
        self.tkImages["?"] = ImageTk.PhotoImage(im)

        self.transparentImages(200)

    def transparentImages(self, alpha=200):
        self.transpImages = {}
        for key, im in self.PilImages.items():
            transp = im.convert("LA")
            for (x, y) in [(n, m) for n in range(transp.size[0]) for m in range(transp.size[1])]:
                val, a = transp.getpixel((x, y))
                if a > alpha:
                    transp.putpixel((x, y), (val, alpha))
            self.transpImages[key] = ImageTk.PhotoImage(transp.convert("RGBA"))
            # To keep aplha in tkinter

    def frontScreen(self):
        for child in self.root.winfo_children():
            child.destroy()

        bgIm = Image.open("Images/BgImages/Background.png")
        w, h = bgIm.size
        ratio = min(w / self.scrW, h / self.scrW)
        bgIm.thumbnail((w / ratio, h / ratio))
        self.bg = tk.Label(self.root)
        self.bg.image = ImageTk.PhotoImage(bgIm)
        self.bg["image"] = self.bg.image

        self.newBut = tk.Button(self.root, bd=0, command=self.newGame)
        self.newBut.image = ImageTk.PhotoImage(file="Images/Buttons/New Button.png")
        self.newBut["image"] = self.newBut.image

        self.loadBut = tk.Button(self.root, bd=0, command=self.load)
        self.loadBut.image = ImageTk.PhotoImage(file="Images/Buttons/Load Button.png")
        self.loadBut["image"] = self.loadBut.image

        self.quitBut = tk.Button(self.root, bd=0, command=self.root.destroy)
        self.quitBut.image = ImageTk.PhotoImage(file="Images/Buttons/Quit Button.png")
        self.quitBut["image"] = self.quitBut.image

        self.bg.place(x=0, y=0)
        self.root.grid_columnconfigure(1, weight=1)
        for i in range(3):
            self.root.grid_rowconfigure(i, weight=1)
        self.newBut.grid(row=0, column=1)
        self.loadBut.grid(row=1, column=1)
        self.quitBut.grid(row=2, column=1)

    def newGame(self):
        self.newBut.destroy()
        self.loadBut.destroy()
        self.quitBut.destroy()

        frame = ttk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        label = ttk.Label(frame, text="How many Players :")
        label.pack(side="top")

        nb = tk.IntVar()

        for i in range(2, 11):
            but = ttk.Button(frame, text=str(i), command=lambda n=i: nb.set(n))
            but.pack(side="left")

        self.root.wait_variable(nb)
        frame.destroy()
        nb = nb.get()

        self.players = []
        players = self.players
        names = []

        frame = ttk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        label = ttk.Label(frame, justify="center")
        label.pack(side="top")

        toName = lambda entry: " ".join(entry.get().split()).title()

        for i in range(nb):
            name = tk.StringVar()
            label["text"] = f"Name of Player {i+1} :"
            entry = ttk.Entry(frame)
            entry.pack()
            cmd = lambda e:  name.set(toName(entry)) if toName(entry) not in names else None
            entry.bind("<Return>", cmd)
            entry.focus_force()

            self.root.wait_variable(name)
            entry.destroy()
            name = name.get()

            players.append(ScrPlayer(name))
            names.append(name)

        self.stock = ScrStock(self.lang)

        for player in players:
            player.pick(self.stock, first=True)

        players.sort(key=lambda p: p.letters[0])

        text = "New Order:"
        for p in players:
            text += f"\n - {p} picked a {p.letters[0]}"
        text += "\n\nPress Enter to start"

        for player in players:
            player.pick(self.stock)

        label["text"] = text
        label.focus_force()
        label.bind("<Return>", lambda e: [self.gameScreen(), label.destroy()])

    def load(self):
        pass

    def close(self):

        self.frontScreen()

    def gameScreen(self):
        for widget in self.root.winfo_children():
            if widget != self.bg:
                widget.destroy()

        self.closeBut = tk.Button(self.root, command=self.close)
        self.closeBut.image = ImageTk.PhotoImage(file="Images/Buttons/Close Button.png")
        self.closeBut["image"] = self.closeBut.image
        self.closeBut.place(x=self.scrW - 5, y=5, anchor="ne")

        self.boardFrame = ttk.Frame(self.root, takefocus=False)
        self.boardFrame.pack(side="left", padx=25, pady=10)

        self.boardCan = tk.Canvas(self.boardFrame, width=self.boardW,
                                  height=self.boardH)
        self.boardCan.pack(padx=5, pady=5)

        def showBoard():

            w = self.tileW
            h = self.tileH

            self.boardCan.delete("all")

            board = self.tkImages["Board"]
            self.boardCan.create_image(0, 0, anchor="nw", image=board)

            for x, y, let in self.enum():
                if let == 0:
                    continue
                # elif let.islower():
                #     piece = self.tkImages["?"]
                #     self.boardCan.create_image(x * w, y * h, anchor="nw", image=piece, tags="piece")
                # elif let.isupper():
                else:
                    piece = self.tkImages[let]
                    self.boardCan.create_image(x * w, y * h, anchor="nw", image=piece, tags="piece")

            for x, y, let in self.playerGrid.enum():
                if let in (0, "_"):
                    continue
                # elif let.islower():
                #     piece = self.transpImages["?"]
                #     self.boardCan.create_image(x * w, y * h, anchor="nw", image=piece, tags="piece")
                # elif let.isupper():
                else:
                    piece = self.transpImages[let]
                    self.boardCan.create_image(x * w, y * h, anchor="nw", image=piece, tags="piece")

        def showCursor():
            x, y = self.cursorPos

            w = self.tileW
            h = self.tileH

            x1, y1 = x * w, y * h
            x2, y2 = x1 + w - 1, y1 + h - 1

            if self.playerWord == "":
                outline = "black"
            else:
                outline = "blue"

            self.boardCan.create_rectangle(x1, y1, x2, y2, outline=outline, width=3, tags="cursor")

            if self.cursorPos.direction == "row":
                x3 = x2
                y3 = (2 * y1 + y2) / 3
                x4 = x2
                y4 = y2 - y3 + y1
                x5 = x2 + w / 8
                y5 = (y1 + y2) / 2
            else:
                x3 = (2 * x1 + x2) / 3
                y3 = y2
                x4 = x2 - x3 + x1
                y4 = y2
                x5 = (x1 + x2) / 2
                y5 = y2 + w / 8
            self.boardCan.create_polygon((x3, y3, x4, y4, x5, y5), width=3,
                                         outline=outline, fill="light green", tags="cursor")

        def KeyBoard(event):
            # word = self.playerWord
            key = event.keysym
            arrows = ("Up", "Down", "Left", "Right")
            player = self.currentPlayer
            PGrid = self.playerGrid
            if self.playerWord == "":  # if no letter already put
                if key in arrows:
                    if key == "Up":
                        self.cursorPos.nextFreeTile(PGrid, "backward",
                                                    direction="col", wrapGrid=self)
                    elif key == "Down":
                        if self.cursorPos.direction == "row":
                            self.cursorPos.switchDir()
                        else:
                            self.cursorPos.nextFreeTile(PGrid, "forward", wrapGrid=self)
                    elif key == "Left":
                        self.cursorPos.nextFreeTile(PGrid, "backward",
                                                    direction="row", wrapGrid=self)
                    elif key == "Right":
                        if self.cursorPos.direction == "col":
                            self.cursorPos.switchDir()
                        else:
                            self.cursorPos.nextFreeTile(PGrid, "forward", wrapGrid=self)

                    self.boardCan.delete("cursor")
                    showCursor()
                    return None

            if key.lower() in list("abcdefghijklmnopqrstuvwxyz"):
                if key.islower() and "?" in player.letters:
                    PGrid[self.cursorPos] = key
                    player.letters.remove("?")
                elif key in player.letters:
                    PGrid[self.cursorPos] = key
                    player.letters.remove(key)
                else:
                    return None
                nbJumps = self.cursorPos.nextFreeTile(PGrid, "forward", boundGrid=self)
                self.playerWord += key + "_" * nbJumps  # Add "_" for tile already occupied

            elif self.playerWord != "":
                if key == "BackSpace":
                    self.cursorPos.nextFreeTile(PGrid, "backward")
                    self.playerWord = self.playerWord.rstrip("_")  # Remove "_"
                    PGrid[self.cursorPos] = 0
                    lastLetter = self.playerWord[-1]
                    self.playerWord = self.playerWord[:-1]
                    if lastLetter.islower():
                        player.letters.append("?")
                    else:
                        player.letters.append(lastLetter)

            gridLetters(player.letters, row=1)
            showBoard()
            showCursor()

        self.boardCan.bind("<Key>", KeyBoard)

        self.letterFrame = tk.Frame(self.boardFrame, bg="wheat", bd=2, relief="raised")
        self.letterFrame.pack(side="bottom", padx=5, pady=5)
        self.letterFrame.grid_rowconfigure(0, minsize=self.tileH * 1.5, weight=1)
        self.currentPLabel = ttk.Label(self.letterFrame, justify="center")
        self.currentPLabel.grid(row=0, column=0, padx=10, columnspan=7)

        self.rackFrame = ttk.Frame(self.root, takefocus=False)
        self.rackFrame.pack(side="right", padx=25, pady=10)

        # self.grabbedLetter = None

        def entered(event):
            label = event.widget
            label["bd"] = 2
            label["bg"] = "black"

        def left(event):
            label = event.widget
            label["bd"] = 2
            label["bg"] = "wheat"

        def clicked(event):
            player = self.currentPlayer
            label = event.widget
            name = label.name
            image = label["image"]
            player.letters.remove(name)
            gridLetters(player.letters, row=1)
            self.grabbedLetter = tk.Label(self.root, bd=2, bg="dark blue", image=image)
            self.grabbedLetter.name = name
            self.grabbedLetter.bind("<B1-Motion>", grabbed)
            self.grabbedLetter.bind("<ButtonRelease-1>", released)
            x = event.x_root
            y = event.y_root
            self.grabbedLetter.place(x=x, y=y, anchor="center")
            self.root.update()

        def grabbed(event):
            x = event.x_root
            y = event.y_root
            event.widget.place(x=x, y=y, anchor="center")
            self.root.update()

        def released(event):
            player = self.currentPlayer
            # if self.grabbedLetter == None:
            #     return None

            # Get the mouse pointer relative to the frame
            x = event.x_root - self.letterFrame.winfo_rootx() + self.tileW / 2
            y = event.y_root - self.letterFrame.winfo_rooty() + self.tileH / 2

            row, col = self.letterFrame.grid_location(x, y)
            if row < 0:
                row = 0
            label = event.widget
            player.letters.insert(row, label.name)
            gridLetters(player.letters, row=1)
            label.destroy()
            # self.grabbedLetter = None

        def gridLetters(playerLetters, row=0):
            for label in self.letterFrame.winfo_children():
                if label != self.currentPLabel:
                    label.destroy()

            for i, letter in enumerate(playerLetters):
                tile = self.tkImages[letter]
                Lab = tk.Label(self.letterFrame, bg="wheat", bd=2, image=tile)
                Lab.name = letter
                Lab.bind("<Enter>", entered)
                Lab.bind("<Leave>", left)
                Lab.bind("<Button-1>", clicked)
                Lab.grid(row=row, column=i)
                # self.letterFrame.labels.append(tmpLab)

        def nextPlayer():
            self.cursorPos = OCoords(7, 7)

            self.currentPlayer = self.players[0]
            player = self.currentPlayer
            otherPlayers = self.players[1:]

            self.currentPLabel["text"] = f"{player}\n{player.pts} pts"

            gridLetters(player.letters, row=1)

            for p in otherPlayers:
                frame = ttk.Frame(self.rackFrame, takefocus=False)
                frame.pack(side="top", padx=5, pady=5)
                rack = tk.Canvas(frame, width=self.tileW * 8, height=self.tileH * 1.05,
                                 bg="wheat")
                rack.pack(side="bottom", padx=5, pady=5)
                label = ttk.Label(frame, text=f"{p} : {p.pts} pts", justify="center")
                label.pack(side="top")

                x = 0
                for letter in p.letters:
                    x += self.tileW // 8
                    tile = self.tkImages[letter]
                    rack.create_image(x, 2, anchor="nw", image=tile, tags="tile")
                    x += self.tileW

            self.playerGrid = self.copy()
            for i, j, tile in self.playerGrid.enum():
                if tile != 0:  # Tile is occupied
                    self.playerGrid[i, j] = "_"

            self.playerWord = ""

            self.boardCan.focus_force()
            showBoard()
            showCursor()

        nextPlayer()

        def Pass():
            pass

        def PlaceWord():
            pass


if __name__ == '__main__':
    game = ScrabbleGame()
