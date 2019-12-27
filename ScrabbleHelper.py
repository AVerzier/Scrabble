
import time as t
import tkinter as tk
from PIL import Image, ImageTk


from ScrabbleGrid import *
# from ScrabbleGrid import Grid, OCoords, ScrabbleGrid


class ScrabbleFinder(ScrabbleGrid):
    """Find the best play in Scrabble"""

    def __init__(self, *args):
        super().__init__(*args)
        self.gridTmp = np.zeros_like(self.grid, dtype=object)

    @staticmethod
    def jokComb(wordToCount, liJok):
        """
        Return a list of all combination of joker placement

        In liJok:
        - "?" : still a joker in the hand but not used
        - "l" : used joker and don't have the normal letter at first
        - "L" : used joker but have the normal letter at first
        """

        def changeNext(wordToCount, liJok, indexDict):
            let = liJok[0]
            startIndex = indexDict[let]

            while let in wordToCount[indexDict[let]:]:
                newIndex = wordToCount.index(let, indexDict[let])
                wordToCount[newIndex] = wordToCount[newIndex].lower()
                indexDict[let] = newIndex + 1
                if len(liJok) > 1:
                    changeNext(wordToCount, liJok[1:], indexDict)
                else:
                    allComb.append(wordToCount[:])  # Append a copy
                wordToCount[newIndex] = wordToCount[newIndex].upper()

            indexDict[let] = startIndex

        allComb = []
        liJok = [let for let in liJok if let != "?" and let.isupper()]
        indexDict = {let: 0 for let in liJok}
        if len(indexDict) > 0:
            changeNext(wordToCount, liJok, indexDict)
            return allComb
        else:  # If no combinations possible:
            return [wordToCount]

    def posLet(self, letters, orCoords):
        swCoords = -orCoords

        liLetPos = []
        prevLetters = self.prevLetters(swCoords - 1)
        postLetters = self.postLetters(swCoords + 1)

        prevLetters = "".join(prevLetters)
        postLetters = "".join(postLetters)

        for letter in set(letters):  # Different letters
            if letter == "?":  # Joker:
                # (letter not already in letters)
                for let in (let for let in self.letPt if let not in set(letters)):
                    let = let.lower()
                    testWord = prevLetters + let + postLetters
                    if testWord.upper() in self.WORDS:
                        liLetPos.append(let)
            else:
                testWord = prevLetters + letter + postLetters
                if testWord.upper() in self.WORDS:
                    liLetPos.append(letter)
        return liLetPos

    def searchWord(self, letters, direction, progressBar=None):

        pos = []  # [('word',pts), ...]

        liLetPos = Grid([[0 for x in range(15)] for y in range(15)])

        orCoords = OCoords(0, 0, direction)

        for tile in self.iter(direction):
            if tile == 0:
                if self.tileSurrounded(orCoords):
                    liLetPos[orCoords] = self.posLet(letters, orCoords)
            orCoords.next(self)

        """
        for x, y in order:
            if self[x, y] == 0:
                if self.sideTilesIsOccupied(x, y, direction):
                    # Return list of possible letters with the points associated
                    liLetPos[x, y] = self.posLet(letters, orCoords)
        """

        for x, y, tile in self.enum(direction):

            if progressBar:
                progressBar.step()
                progressBar.update()

            if tile != 0:  # Check if tile occupied
                continue

            orCoords = OCoords(x, y, direction)

            prevLetters = self.prevLetters(orCoords - 1)

            midLetters = []
            nbFreePlaces = 0

            while self[orCoords] != None:  # While inside the Grid
                if self[orCoords] == 0:  # If tile is free
                    if nbFreePlaces == len(letters):  # No more letters
                        break
                    elif liLetPos[orCoords] == []:  # No letter possible
                        break
                    elif liLetPos[orCoords] != 0:  # Letters possible
                        midLetters.append(liLetPos[orCoords])
                    else:  # Tile free
                        midLetters.append(0)
                    nbFreePlaces += 1
                else:
                    midLetters.append(self[orCoords])
                orCoords += 1

            postLetters = self.postLetters(orCoords)

            fullWord = prevLetters + midLetters + postLetters

            # If fullWord only 0: Check if just after is occupied
            if all([tile == 0 or tile == [] for tile in fullWord]):
                continue

            orCoords -= len(fullWord)  # Place the coords on the first letter

            firstNoneZero = 0
            for letter in fullWord:
                if letter != 0:
                    if type(letter) == list:
                        firstNoneZero += 1
                    break
                firstNoneZero += 1

            for word in self.WORDS:

                if len(word) > len(fullWord) or len(word) < firstNoneZero:
                    continue

                liWord = list(word)
                wordToCount = []

                # List without joker
                liLetters = [let for let in letters if let != "?"]
                liJok = ["?"] * letters.count("?")
                liStart = liLetters + liJok  # Start list

                success = True
                for i, letter in enumerate(liWord):
                    # No more letter:
                    if type(fullWord[i]) != str and liLetters == [] and liJok.count("?") == 0:
                        success = False
                        break

                    if fullWord[i] == 0:  # If the tile is free
                        if letter in liLetters:
                            liLetters.remove(letter)
                            wordToCount.append(letter)
                        elif "?" in liJok:
                            liJok.remove("?")
                            if letter in liStart:
                                liJok.append(letter)
                                wordToCount.append(letter)
                            else:
                                liJok.append(letter.lower())
                                wordToCount.append(letter.lower())
                        else:
                            success = False
                            break
                    elif type(fullWord[i]) == list:
                        if letter in fullWord[i]:
                            if letter in liLetters:  # Non-joker:
                                liLetters.remove(letter)
                                wordToCount.append(letter)
                            elif "?" in liJok:
                                liJok.remove("?")
                                if letter in liStart:
                                    liJok.append(letter)
                                    wordToCount.append(letter)
                                else:
                                    liJok.append(letter.lower())
                                    wordToCount.append(letter.lower())
                            else:
                                success = False
                                break
                        elif letter.lower() in fullWord[i] and "?" in liJok:
                            liJok.remove("?")
                            liJok.append(letter.lower())
                            wordToCount.append(letter.lower())
                        else:
                            success = False
                            break
                    elif letter == fullWord[i].upper():
                        #  Add a "_" to tell it's already on the grid
                        wordToCount.append(fullWord[i] + "_")
                    else:
                        success = False
                        break

                # No letter was used :
                if liStart == liLetters + liJok:
                    continue

                if success == True:

                    tileAfter = self[orCoords + len(word)]
                    # If tile after is occupied:
                    if tileAfter not in (0, None):
                        continue

                    # if direction == "row":
                    #     wx, wy = x - len(prevLetters), y
                    # elif direction == "col":
                    #     wx, wy = x, y - len(prevLetters)

                    if set(liJok) in (set(), {"?"}):  # No joker was used:
                        wordToCount = [letter[0]
                                       for letter in wordToCount]  # Remove "_"
                        pts = self.countPtWord(wordToCount, orCoords)
                        x, y, direction = orCoords.unpack()
                        pos.append(
                            (("".join(wordToCount), x, y, direction), pts))
                        continue

                    for wordToCount in self.jokComb(wordToCount, liJok):
                        wordToCount = [letter[0]
                                       for letter in wordToCount]  # Remove "_"
                        pts = self.countPtWord(wordToCount, orCoords)
                        x, y, direction = orCoords.unpack()
                        pos.append(
                            (("".join(wordToCount), x, y, direction), pts))
        return pos

    def firstPlay(self, letters, progressBar=None):
        pos = []

        orCoords = OCoords(1, 7, "row")
        for i in range(7):
            if progressBar:
                progressBar.step()
                progressBar.update()

            firstNoneZero = 7 - orCoords.x
            for word in self.WORDS:

                if len(word) > len(letters) or len(word) <= firstNoneZero:
                    continue

                liWord = list(word)
                wordToCount = []

                # List without joker
                liLetters = [let for let in letters if let != "?"]
                liJok = ["?"] * letters.count("?")
                liStart = liLetters + liJok  # Start list

                success = True
                for i, letter in enumerate(liWord):
                    # No more letter:
                    if liLetters == [] and liJok.count("?") == 0:
                        success = False
                        break

                    if letter in liLetters:
                        liLetters.remove(letter)
                        wordToCount.append(letter)
                    elif "?" in liJok:
                        liJok.remove("?")
                        if letter in liStart:
                            liJok.append(letter)
                            wordToCount.append(letter)
                        else:
                            liJok.append(letter.lower())
                            wordToCount.append(letter.lower())
                    else:
                        success = False
                        break

                if success:

                    if set(liJok) in (set(), {"?"}):  # No joker was used:
                        pts = self.countPtWord(wordToCount, orCoords)
                        x, y, direction = orCoords.unpack()
                        pos.append(
                            (("".join(wordToCount), x, y, direction), pts))
                        continue

                    for wordToCount in self.jokComb(wordToCount, liJok):
                        pts = self.countPtWord(wordToCount, orCoords)
                        x, y, direction = orCoords.unpack()
                        pos.append(
                            (("".join(wordToCount), x, y, direction), pts))
            orCoords += 1
        return pos

    def topPlay(self, letters, count=25, progressBar=None):
        topPlay = []  # [(('word', x, y, direction), pts), ...]

        t1 = t.process_time()

        if self.data == [[0 for x in range(15)] for y in range(15)]:
            if progressBar != None:
                progressBar["maximum"] = 7 + 1
            topPlay += self.firstPlay(letters, progressBar)
        else:
            if progressBar:
                progressBar["maximum"] = (self.W * self.H) * 2 + 1
            print("SEARCH IN ROW")
            posRow = self.searchWord(letters, "row", progressBar)
            print("SEARCH IN COL")
            posCol = self.searchWord(letters, "col", progressBar)

            topPlay += posRow
            topPlay += posCol

        topPlay.sort(key=lambda play: play[1], reverse=True)  # Sort by points
        print("In Total :", len(topPlay), "possibilities")
        topPlay = topPlay[:count]
        t2 = t.process_time()
        duration = round(t2 - t1, 3)
        print("It took", duration, "secondes")

        return topPlay


class ScrabbleHelper(ScrabbleFinder):
    """GUI for help in Scrabble"""

    def __init__(self, *args):
        super().__init__(*args)
        self.cursorPos = OCoords(7, 7)

        self._win = tk.Tk()
        scrHeight = self._win.winfo_screenheight()
        scrWidth = self._win.winfo_screenwidth()
        self._win.geometry("+0+0")
        self._win.title("SCRABBLE HELPER")
        self._win.iconbitmap("Images/Board/64x64.ico")
        self._win["bg"] = "SpringGreen4"

        self.rightFrame = tk.Frame(self._win, bd=5, relief="raised")
        self.rightFrame.pack(side="right", padx=10, pady=10)

        self.modBoardBut = tk.Button(self.rightFrame, text="MODIFY\nBOARD",
                                     command=self.modifyBoard)
        self.modBoardBut.pack(padx=5, pady=5)

        self.topPlayBut = tk.Button(self.rightFrame, text="TOP PLAY", state="disable",
                                    command=self.TopPlay)
        self.topPlayBut.pack(padx=5, pady=5)

        self.topPlayBox = tk.Listbox(self.rightFrame, state="disable", activestyle="none",
                                     selectmode="single", width=30)
        self.topPlayBox.bind("<<ListboxSelect>>", self.showSelectedWord)
        self.topPlayBox.pack(padx=5, pady=5)

        self.placeSelWordBut = tk.Button(self.rightFrame, text="PLACE WORD", state="disable",
                                         command=self.placeSelWord)
        self.placeSelWordBut.pack(padx=5, pady=5)

        self.leftFrame = tk.Frame(self._win, bd=5, relief="sunken")
        self.leftFrame.pack(side="top", padx=10, pady=10)

        self.boardFrame = tk.Frame(self.leftFrame, bd=5, relief="sunken")
        self.boardFrame.pack(side="top")

        self.PilImages = {}

        im = Image.open("Images/Board/board.png")
        self.PilImages["Board"] = im
        if im.height < scrHeight * 75 // 100:
            self.tileSize = im.height // 15
        else:
            self.tileSize = scrHeight * 75 // 100 // 15
        self.boardSize = self.tileSize * 15

        # Images of the pieces
        for let in self.letPt:
            im = Image.open(f"Images/Letters/{self.lang}/{let}.png")
            self.PilImages[let] = im

            smallLet = let.lower()
            im = Image.open(f"Images/Letters/{self.lang}/Blanks/{smallLet}.png")
            self.PilImages[smallLet] = im

        # Blank
        im = Image.open(f"Images/Letters/{self.lang}/Blanks/blank.png")
        self.PilImages["?"] = im
        ##

        self.boardCan = tk.Canvas(self.boardFrame, takefocus=0,
                                  width=self.boardSize, height=self.boardSize)

        self.boardCan.bind("<Key>", self.Keyboard)
        self.boardCan.pack(side="top")

        self.lettersFrame = tk.Frame(
            self.leftFrame, bd=10, bg="blanched almond", relief="raised")
        self.lettersFrame.pack(side="bottom", padx=5, pady=5)

        self.lettersCan = tk.Canvas(self.lettersFrame, takefocus=0,  bg="peach puff",
                                    width=self.tileSize * 8, height=self.tileSize)
        self.lettersCan.bind("<Key>", self.KeyLet)
        self.lettersCan.pack(side="left", padx=5)

        self.letters = ""

        self.modLetBut = tk.Button(self.lettersFrame, text="MODIFY LETTERS",
                                   command=self.modifyLetters)
        self.modLetBut.pack(side="right", padx=5)

        self.resizeBoard()

        self._win.mainloop()

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

        info = tk.Toplevel(self._win)
        info.title("Top Play")
        x = self.topPlayBut.winfo_rootx() - self.topPlayBut.winfo_reqwidth()
        y = self.topPlayBut.winfo_rooty() + self.topPlayBut.winfo_reqheight()
        info.geometry(f"+{x}+{y}")
        text = tk.Label(info, text="SEARCH EVERY POSSIBLE WORDS,\nPLEASE WAIT ...",
                        justify="center")
        text.pack(padx=10, pady=10)
        info.transient(self._win)
        info.update()

        self.topPlayList = self.topPlay(self.letters)

        info.destroy()

        self.topPlayBox["state"] = "normal"

        for i, pos in enumerate(self.topPlayList):
            self.topPlayBox.insert("end", f"{i + 1} : {pos[1]}pts - {pos[0][0]}")

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
        word, x, y, direction = self.topPlayList[index][0]
        orCoords = OCoords(x, y, direction)
        for letter in word:
            if self[orCoords] == 0:
                x, y = orCoords
                if letter.islower():
                    piece = self.tmpImages[letter]
                    self.boardCan.create_image(x * w, y * h, anchor="nw",
                                               image=piece, tags="piece")
                    self.tmpLetters = self.tmpLetters.replace(
                        "?", "", 1)  # Remove let
                elif letter.isupper():
                    piece = self.tmpImages[letter]
                    self.boardCan.create_image(x * w, y * h, anchor="nw",
                                               image=piece, tags="piece")
                    self.tmpLetters = self.tmpLetters.replace(
                        letter, "", 1)  # Remove let
            orCoords += 1

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
        x = self.modLetBut.winfo_rootx() + self.modLetBut.winfo_reqwidth()
        self.info.geometry(f"+{x}-50")
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
        self.boardCan.create_rectangle(x1, y1, x2, y2, width=3, tags="cursor")

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
                                     outline="black", fill="light green", tags="cursor")

    def resizeBoard(self):

        self.tmpImages = {}  # Transparent Images
        self.tkImages = {}

        for key in self.PilImages:
            im = self.PilImages[key]

            w = self.tileSize
            h = self.tileSize

            if key == "Board":
                im = im.resize((w * 15, h * 15), Image.BILINEAR)
                self.PilImages[key] = im
                self.tkImages[key] = ImageTk.PhotoImage(im)
            else:
                im = im.resize((w, h), Image.BILINEAR)
                self.PilImages[key] = im
                self.tkImages[key] = ImageTk.PhotoImage(im)
                for x, y in [(n, m) for m in range(h) for n in range(w)]:
                    r, g, b, a = im.getpixel((x, y))
                    if a > 200:
                        im.putpixel((x, y), (r, g, b, 200))
                self.tmpImages[key] = ImageTk.PhotoImage(im)

        self.showBoard()

    def showBoard(self):

        w = self.tileSize
        h = self.tileSize

        self.boardCan.delete("all")

        board = self.tkImages["Board"]
        self.boardCan.create_image(0, 0, anchor="nw", image=board)

        for x, y in [(n, m) for m in range(15) for n in range(15)]:
            let = self[x, y]
            if let == 0:
                continue
            # elif let.islower():
            #     piece = self.tkImages["?"]
            #     self.boardCan.create_image(
            #         x * w, y * h, anchor="nw", image=piece, tags="piece")
            # elif let.isupper():
            else:
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
        key = event.keysym
        arrows = ("Up", "Down", "Left", "Right")
        if key in arrows:
            if key == "Up":
                self.cursorPos.backward(direction="col", wrapGrid=self)
            elif key == "Down":
                if self.cursorPos.direction == "row":
                    self.cursorPos.switchDir()
                else:
                    self.cursorPos.forward(direction="col", wrapGrid=self)
            elif key == "Left":
                self.cursorPos.backward(direction="row", wrapGrid=self)
            elif key == "Right":
                if self.cursorPos.direction == "col":
                    self.cursorPos.switchDir()
                else:
                    self.cursorPos.forward(direction="row", wrapGrid=self)
            self.boardCan.delete("cursor")
            self.showCursor()
            return None
        elif key.lower() in list("abcdefghijklmnopqrstuvwxyz"):
            self[self.cursorPos] = key
            self.cursorPos.forward(wrapGrid=self)
        elif key == "BackSpace":
            self[self.cursorPos] = 0
            self.cursorPos.backward(wrapGrid=self)
        elif key == "Escape":
            self.boardCan.delete("cursor")
            self.info.destroy()
            self.buttonsOn()
            self._win.focus_set()
            return None
        self.showBoard()
        self.showCursor()

    def modifyBoard(self):

        self.info = tk.Toplevel()
        self.info.title("Modify Board")
        x = self.topPlayBut.winfo_rootx() - self.topPlayBut.winfo_reqwidth()
        y = self.topPlayBut.winfo_rooty() + self.topPlayBut.winfo_reqheight()
        self.info.geometry(f"+{x}+{y}")
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
