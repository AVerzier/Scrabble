import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


from ScrabbleGrid import ScrabbleGrid


class ScrabbleHelper(ScrabbleGrid):
    """GUI for help in Scrabble"""

    def __init__(self, lang="FR"):
        super().__init__(lang)
        self.cursorPos = [7, 7]  # [x, y]

        self._win = tk.Tk()
        scrHeight = self._win.winfo_screenheight()
        scrWidth = self._win.winfo_screenwidth()
        self._win.geometry("+0+0")
        self._win.title("SCRABBLE HELPER")
        self._win.iconbitmap("Images/Board/64x64.ico")
        self._win["bg"] = "SpringGreen4"

        self.rightFrame = ttk.Frame(self._win)
        self.rightFrame.pack(side="right", padx=10, pady=10)

        self.modBoardBut = ttk.Button(self.rightFrame, text="MODIFY\nBOARD",
                                      command=self.modifyBoard)
        self.modBoardBut.pack(padx=5, pady=5)

        self.topPlayBut = ttk.Button(self.rightFrame, text="TOP PLAY", state="disable",
                                     command=self.TopPlay)
        self.topPlayBut.pack(padx=5, pady=5)

        self.topPlayBox = tk.Listbox(self.rightFrame, state="disable", activestyle="none",
                                     selectmode="single", width=30)
        self.topPlayBox.bind("<<ListboxSelect>>", self.showSelectedWord)
        self.topPlayBox.pack(padx=5, pady=5)

        self.placeSelWordBut = ttk.Button(self.rightFrame, text="PLACE WORD", state="disable",
                                          command=self.placeSelWord)
        self.placeSelWordBut.pack(padx=5, pady=5)

        self.leftFrame = ttk.Frame(self._win)
        self.leftFrame.pack(side="top", padx=10, pady=10)

        self.boardFrame = tk.Frame(self.leftFrame)
        self.boardFrame.pack(side="top")

        self.PilImages = {}
        self.transpImages = {}

        im = Image.open("Images/Board/board.png")
        self.PilImages["Board"] = im
        if im.height < scrHeight * 75 // 100:
            self.tileSize = im.height // 15
        else:
            self.tileSize = scrHeight * 75 // 100 // 15
        self.boardSize = self.tileSize * 15

        # Images of the pieces
        for let in self.letPt:
            im = Image.open(f"Images/Letters/{self.lang}/" + let + ".png")
            self.PilImages[let] = im
        # Blank
        im = Image.open(f"Images/Letters/{self.lang}/blank.png")
        self.PilImages["?"] = im
        ##

        self.boardCan = tk.Canvas(self.boardFrame, takefocus=0,
                                  width=self.boardSize, height=self.boardSize)

        self.boardCan.bind("<Key>", self.Keyboard)
        self.boardCan.pack(side="top")

        self.lettersFrame = tk.Frame(self.leftFrame)
        self.lettersFrame.pack(side="bottom", padx=5, pady=5)

        self.lettersCan = tk.Canvas(self.lettersFrame, takefocus=0,  bg="peach puff",
                                    width=self.tileSize * 8, height=self.tileSize)
        self.lettersCan.bind("<Key>", self.KeyLet)
        self.lettersCan.pack(side="left", padx=5)

        self.letters = ""

        self.modLetBut = ttk.Button(self.lettersFrame, text="MODIFY LETTERS",
                                    command=self.modifyLetters)
        self.modLetBut.pack(side="right", padx=5)

        self.resizeBoard()

        self._win.mainloop()

    def _transpImage(self, key, alpha):
        if f"{key} {alpha}" in self.transpImages:  # If already exits
            return self.transpImages[f"{key} {alpha}"]

        im = self.PilImages[key]

        w = self.tileSize
        h = self.tileSize

        if key == "Board":
            im = im.resize((w * 15, h * 15), Image.BILINEAR)
        else:
            im = im.resize((w, h), Image.BILINEAR)

        w, h = im.size

        for x, y in [(n, m) for m in range(h) for n in range(w)]:
            r, g, b, a = im.getpixel((x, y))
            if a > alpha:
                im.putpixel((x, y), (r, g, b, alpha))

        self.transpImages[f"{key} {alpha}"] = ImageTk.PhotoImage(im)

        return self.transpImages[f"{key} {alpha}"]

    def placeSelWord(self):
        index = int(self.topPlayBox.curselection()[0])
        word, x, y, direction = self.topPlayList[index][0]
        self.placeWord(word, x, y, direction)

        self.letters = self.tmpLetters

        self.clearList()
        self.showBoard()

    def clearList(self):
        self.topPlayList = []
        self.topPlayBox.delete(0, "end")
        self.buttonsOff()
        self.buttonsOn()

    def TopPlay(self):
        self.buttonsOff()

        info = tk.Toplevel()
        info.title("Top Play")
        x = str(self.topPlayBut.winfo_rootx() -
                self.topPlayBut.winfo_reqwidth())
        y = str(self.topPlayBut.winfo_rooty() +
                self.topPlayBut.winfo_reqheight())
        info.geometry(f"+{x}+{y}")
        progress = ttk.Progressbar(info, length=300)
        progress.pack(side="bottom")
        text = tk.Label(info, text="SEARCH EVERY POSSIBLE WORDS,\nPLEASE WAIT ...",
                        justify="center")
        text.pack(padx=10, pady=10)
        info.transient(self._win)
        info.update()

        self.topPlayList = self.topPlay(self.letters, 25, progress)

        info.destroy()

        self.topPlayBox["state"] = "normal"

        for i, pos in enumerate(self.topPlayList):
            self.topPlayBox.insert("end", str(i + 1) + " : " +
                                   (str(pos[1]) + "pts - " + str(pos[0][0])))

        if self.topPlayBox.size() > 0:
            self.topPlayBox["state"] = "normal"
            self.placeSelWordBut["state"] = "normal"
        else:
            self.topPlayBut["state"] = "disable"
            self.buttonsOn()

    def showSelectedWord(self, event):

        self.tmpLetters = self.letters
        self.showBoard()

        w = self.tileSize
        h = self.tileSize

        index = int(self.topPlayBox.curselection()[0])
        word, ax, ay, direction = self.topPlayList[index][0]
        for letter in word:
            if self[ax, ay] == 0:
                if letter.islower():
                    piece = self._transpImage("?", 180)
                    self.boardCan.create_image(
                        ax * w, ay * h, anchor="nw", image=piece, tags="piece")
                    self.tmpLetters = self.tmpLetters.replace(
                        "?", "", 1)  # Remove let
                elif letter.isupper():
                    piece = self._transpImage(letter, 180)
                    self.boardCan.create_image(
                        ax * w, ay * h, anchor="nw", image=piece, tags="piece")
                    self.tmpLetters = self.tmpLetters.replace(
                        letter, "", 1)  # Remove let
            ax, ay = self.coorAfter(ax, ay, direction)

        self.showLetters(self.tmpLetters)

    def KeyLet(self, event):
        key = event.keysym

        if len(self.letters) < 7:
            if key.upper() in self.letPt:
                self.letters += key.upper()
                self.showLetters()
            elif key == "question":
                self.letters += "?"
                self.showLetters()

        if key == "BackSpace":
            self.letters = self.letters[:-1]  # Remove last piece
            self.showLetters()
        elif key == "Escape":
            self.info.destroy()
            self.buttonsOn()
            self._win.focus_set()

    def modifyLetters(self):

        self.info = tk.Toplevel()
        self.info.title("Modify Letters")
        x = str(self.modLetBut.winfo_rootx() + self.modLetBut.winfo_reqwidth())
        self.info.geometry("+" + x + "-50")
        text = tk.Label(self.info, text="Modify your letters :\nPress:\n<Letter> to add the letter\n< ? > to add a blank\n<BackSpace> to delete\n<Esc> to validate",
                        justify="center")
        text.pack(padx=10, pady=10)
        self.info.update()
        self.info.transient(self._win)

        self.clearList()
        self.lettersCan.focus_set()
        self.buttonsOff()

    def showLetters(self, letters=None):
        if letters == None:
            letters = self.letters

        self.lettersCan.delete("piece")

        x = 0
        w = self.tileSize

        for letter in letters:
            x += w // 7
            piece = self.tkImages[letter]
            self.lettersCan.create_image(
                x, 0, anchor="nw", image=piece, tags="piece")
            x += w

    def showCursor(self):
        x, y = self.cursorPos

        w = self.tileSize
        h = self.tileSize

        x1, y1 = x * w, y * h
        x2, y2 = x1 + w - 1, y1 + h - 1
        self.cursor = self.boardCan.create_rectangle(x1, y1, x2, y2, width=3)

    def resizeBoard(self):

        self.tkImages = {}

        for key, im in self.PilImages.items():

            w = self.tileSize
            h = self.tileSize

            if key == "Board":
                im = im.resize((w * 15, h * 15), Image.BILINEAR)
            else:
                im = im.resize((w, h), Image.BILINEAR)
            self.tkImages[key] = ImageTk.PhotoImage(im)

        self.showBoard()

    def showBoard(self):

        w = self.tileSize
        h = self.tileSize

        self.boardCan.delete("all")

        board = self.tkImages["Board"]
        self.boardCan.create_image(0, 0, anchor="nw", image=board)

        # for y in range(15):
        #     for x in range(15):
        for x, y in [(n, m) for m in range(15) for n in range(15)]:
            let = self[x, y]
            if let == 0:
                continue
            elif let.islower():
                piece = self.tkImages["?"]
                self.boardCan.create_image(
                    x * w, y * h, anchor="nw", image=piece, tags="piece")
            elif let.isupper():
                piece = self.tkImages[let]
                self.boardCan.create_image(
                    x * w, y * h, anchor="nw", image=piece, tags="piece")

    def buttonsOff(self):
        for widget in self.rightFrame.winfo_children():
            widget["state"] = "disable"
        self.modLetBut["state"] = "disable"

    def buttonsOn(self):
        self.modLetBut["state"] = "normal"
        for widget in self.rightFrame.winfo_children():
            widget["state"] = "normal"

        if len(self.letters) > 0:
            self.topPlayBut["state"] = "normal"
        else:
            self.topPlayBut["state"] = "disable"

        if self.topPlayBox.size() > 0:
            self.topPlayBox["state"] = "normal"
            self.placeSelWordBut["state"] = "normal"
        else:
            self.topPlayBox["state"] = "disable"
            self.placeSelWordBut["state"] = "disable"

    def Keyboard(self, event):
        x, y = self.cursorPos
        key = event.keysym
        arrows = ("Up", "Down", "Left", "Right")
        if key in arrows:
            if key == "Up":
                y = (y - 1) % 15
            elif key == "Down":
                y = (y + 1) % 15
            elif key == "Left":
                x = (x - 1) % 15
            elif key == "Right":
                x = (x + 1) % 15
            self.cursorPos = x, y
            self.boardCan.delete(self.cursor)
            self.showCursor()
            return None
        elif key.lower() in list("abcdefghijklmnopqrstuvwxyz"):
            self[x, y] = key
        elif key == "BackSpace":
            self[x, y] = 0
        elif key == "Escape":
            self.boardCan.delete(self.cursor)
            self.info.destroy()
            self.buttonsOn()
            self._win.focus_set()
            return None
        self.showBoard()
        self.showCursor()

    def modifyBoard(self):

        self.info = tk.Toplevel()
        self.info.title("Modify Board")
        x = str(self.modBoardBut.winfo_rootx() -
                self.modBoardBut.winfo_reqwidth())
        y = str(self.modBoardBut.winfo_rooty() +
                self.modBoardBut.winfo_reqheight())
        self.info.geometry("+" + x + "+" + y)
        text = tk.Label(self.info, text="Modify the board :\nPress:\n<Arrow> to move the cursor\n<Capital Letter> to add the letter\n<Small Letter> to add the letter as a blank\n<BackSpace> to delete\n<Esc> to validate",
                        justify="center")
        text.pack(padx=10, pady=10)
        self.info.update()
        self.info.transient(self._win)

        self.clearList()
        self.boardCan.focus_set()
        self.buttonsOff()
        self.showCursor()

if __name__ == '__main__':
    win = ScrabbleHelper()
