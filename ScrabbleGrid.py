
class Grid:
    """2D Rectangular Grid"""

    def __init__(self, listOfLists):
        if type(listOfLists) != list or any([type(row) != list for row in listOfLists]):
            raise TypeError("Need a list of lists")
        testLen = len(listOfLists[0])
        if any([len(row) != testLen for row in listOfLists]):
            raise ValueError("Not a rectangle grid")

        self.data = listOfLists

        self.H = len(self.data)
        self.W = testLen

    def __iter__(self):
        for row in self.data:
            for elem in row:
                yield elem

    def __repr__(self):
        elemLen = max((len(repr(elem)) for elem in self))

        name = type(self).__name__
        res = f"{name}(["

        for y, row in enumerate(self.data):
            if y != 0:  # Not First Row
                res += " " * len(name + ")")
            res += f"[{row[0]!r: >{elemLen}}"
            for elem in row[1:]:
                res += f", {elem!r: >{elemLen}}"
            if y != self.H - 1:  # Not Last Row
                res += "],\n "
        res += "]])"

        return res

    def __str__(self):
        elemLen = max((len(str(elem)) for elem in self))

        res = "["
        for y, row in enumerate(self.data):
            res += f"[{row[0]: >{elemLen}}"
            for elem in row[1:]:
                res += f" {elem: >{elemLen}}"
            if y != self.H - 1:  # Not Last Row
                res += "]\n "
        res += "]]"

        return res

    def __getitem__(self, orCoords):
        x, y = orCoords
        if x in range(self.W) and y in range(self.H):
            return self.data[y][x]
        else:
            return None

    def __setitem__(self, orCoords, letter):
        x, y = orCoords
        if x in range(self.W) and y in range(self.H):
            self.data[y][x] = letter
        else:
            raise IndexError("Key out of range")

    def copy(self):
        data = [row[:] for row in self.data]
        return Grid(data)

    def iter(self, direction="row"):
        if direction == "row":
            order = [(n, m) for m in range(self.H) for n in range(self.W)]
        elif direction == "col":
            order = [(n, m) for n in range(self.W) for m in range(self.H)]

        for i, j in order:
            yield self[i, j]

    def enum(self, direction="row"):
        if direction == "row":
            order = [(n, m) for m in range(self.H) for n in range(self.W)]
        elif direction == "col":
            order = [(n, m) for n in range(self.W) for m in range(self.H)]

        for i, j in order:
            yield (i, j, self[i, j])

    def arroundVals(self, x, y):
        vals = []
        for i, j in [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]:
            vals.append(self[x + i, y + j])
        return vals


class OCoords:
    """Oriented Coordinates for ScrabbleGrid"""

    def __init__(self, x=0, y=0, direction="row"):
        self.x = x
        self.y = y
        self.direction = direction

    def __repr__(self):
        name = type(self).__name__
        args = (self.x, self.y, self.direction)
        return f"{name}{args}"

    def __str__(self):
        return f"(x : {self.x}, y : {self.y})"

    def __iter__(self):
        return iter((self.x, self.y))

    def __add__(self, n):
        orCoords = OCoords(self.x, self.y, self.direction)
        if type(n) == int:
            for i in range(n):
                orCoords.forward()
            return orCoords

    def __sub__(self, n):
        orCoords = OCoords(self.x, self.y, self.direction)
        if type(n) == int:
            for i in range(n):
                orCoords.backward()
            return orCoords

    def __neg__(self):
        orCoords = OCoords(self.x, self.y, self.direction)
        orCoords.switchDir()
        return orCoords

    def unpack(self):
        return self.x, self.y, self.direction

    def switchDir(self):
        if self.direction == "row":
            self.direction = "col"
        else:
            self.direction = "row"

    def chDir(self, direction):
        if direction not in ("row", "col"):
            raise ValueError("Direction should be 'row' or 'col'")
        else:
            self.direction = direction

    def next(self, grid):
        self.forward()
        w, h = grid.W, grid.H

        if self.x >= w:
            self.x = 0
            self.y += 1
            if self.y >= h:
                self.y = 0

        elif self.y >= h:
            self.y = 0
            self.x += 1
            if self.x >= w:
                self.x = 0

    def move(self, way, direction=None, wrapGrid=None, boundGrid=None):
        if direction != None:
            self.chDir(direction)

        if way == "forward":
            leap = 1
        elif way == "backward":
            leap = -1
        else:
            raise ValueError("way should be 'forward' or 'backward'")

        if self.direction == "row":
            self.x += leap
            if boundGrid:
                self.x = min(max(self.x, 0), boundGrid.W - 1)
            elif wrapGrid:
                self.x %= wrapGrid.W
        elif self.direction == "col":
            self.y += leap
            if boundGrid:
                self.y = min(max(self.y, 0), boundGrid.H - 1)
            elif wrapGrid:
                self.y %= wrapGrid.H

    def forward(self, *args, **kwargs):
        self.move("forward", *args, **kwargs)

    def backward(self, *args, **kwargs):
        self.move("backward", *args, **kwargs)

    def nextFreeTile(self, playerGrid, *args, **kwargs):
        if self.direction == "row":
            size = playerGrid.W
        else:
            size = playerGrid.H
        for i in range(size):
            self.move(*args, **kwargs)
            if playerGrid[self] != "_":
                break

        return i  # Nb of "_" jumped


class ScrabbleGrid(Grid):

    def __init__(self, data=[[0 for x in range(15)] for y in range(15)], lang="FR"):
        super().__init__(data)
        self.lang = lang
        # Dictionnary
        with open(f"Words/WORDS {self.lang}.txt", "r") as file:
            self.WORDS = file.read().split("\n")

        # Points on each letter
        with open(f"Letters/letPt {self.lang}.txt", "r") as file:
            self.letPt = eval(file.read())
        self.gridPt = Grid([[4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4],
                            [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
                            [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
                            [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
                            [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                            [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
                            [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
                            [4, 0, 0, 1, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 4],
                            [0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0],
                            [0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 0],
                            [0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0],
                            [1, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 1],
                            [0, 0, 3, 0, 0, 0, 1, 0, 1, 0, 0, 0, 3, 0, 0],
                            [0, 3, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 3, 0],
                            [4, 0, 0, 1, 0, 0, 0, 4, 0, 0, 0, 1, 0, 0, 4]])

    def tileSurrounded(self, orCoords):
        """Check if one of the tile beside is occupied"""

        return bool(self[-orCoords - 1] or self[-orCoords + 1])

    def wordAcross(self, letter, orCoords):
        """Return the word made accross"""

        swCoords = -orCoords

        prevLetters = self.prevLetters(swCoords - 1)
        postLetters = self.postLetters(swCoords + 1)
        wordAcross = prevLetters + [letter] + postLetters
        return "".join(wordAcross)

    def prevLetters(self, orCoords):
        """Return the the letters going backward"""

        prevLetters = []
        while self[orCoords] not in (0, None):
            prevLetters.append(self[orCoords])
            orCoords -= 1
        return prevLetters[::-1]  # Reverse

    def postLetters(self, orCoords):
        """Return the the letters going forward"""

        postLetters = []
        while self[orCoords] not in (0, None):
            postLetters.append(self[orCoords])
            orCoords += 1
        return postLetters

    def placeWord(self, word, x, y, direction):
        """Put the Letters on the grid"""

        orCoords = OCoords(x, y, direction)
        for letter in word:
            if self[orCoords] == 0:
                self[orCoords] = letter
            orCoords += 1

    def countPtAcross(self, letter, orCoords):
        """Count the points made by the word beside"""

        pts = 0
        mult = 1

        wordAcross = self.wordAcross(letter, orCoords)
        for let in wordAcross:
            if let.isupper():
                pts += self.letPt[let]

        # letter on bonus tile:
        bonusCase = self.gridPt[orCoords]
        if bonusCase == 1:
            if letter.isupper():
                pts += self.letPt[letter]
        elif bonusCase == 2:
            if letter.isupper():
                pts += self.letPt[letter] * 2
        elif bonusCase == 3:
            mult *= 2
        elif bonusCase == 4:
            mult *= 3

        return pts * mult

    def countPtWord(self, wordToCount, orCoords):
        """Count the points of the word made"""

        totPts = 0
        wordPts = 0
        mult = 1
        nbLetUsed = 0

        for letter in wordToCount:
            if letter.isupper():
                wordPts += self.letPt[letter]

            if self[orCoords] != 0:  # If the tile was occupied:
                orCoords += 1
                continue

            nbLetUsed += 1

            bonusCase = self.gridPt[orCoords]
            if bonusCase == 1:
                if letter.isupper():
                    wordPts += self.letPt[letter]
            elif bonusCase == 2:
                if letter.isupper():
                    wordPts += self.letPt[letter] * 2
            elif bonusCase == 3:
                mult *= 2
            elif bonusCase == 4:
                mult *= 3

            if self.tileSurrounded(orCoords):
                totPts += self.countPtAcross(letter, orCoords)

            orCoords += 1

        totPts += wordPts * mult

        if nbLetUsed == 7:
            totPts += 50

        return totPts

    def isConnected(self, newLetters, orCoords):

        if self[orCoords - 1]:  # Letter before
            return True

        for letter in newLetters:
            if self.tileSurrounded(orCoords):
                return True
            orCoords += 1

        if self[orCoords]:  # Letter after
            return True

        return False

    def validate(self, newLetters, x, y, direction):
        """Check if Letters added make legit play"""

        orCoords = OCoords(x, y, direction)

        if not self.isConnected(newLetters, orCoords + 0):  # "+ 0" to copy
            print("New Letters are not connected to the current Letters")
            # raise IndexError("New Letters are not connected to the current Letters")
            return False

        prevLetters = self.prevLetters(orCoords - 1)

        midLetters = []
        for letter in newLetters:
            if self[orCoords] == None:
                raise IndexError(f"{orCoords} : {letter} not on the grid")
                return False

            elif self[orCoords] != 0:
                if letter != "_" and letter.upper() != self[orCoords].upper():
                    print(f"{letter} and {self[orCoords]} doesn't correspond")
                    # raise ValueError(f"{letter} and {self[orCoords]} doesn't correspond")
                    return False

                midLetters.append(self[orCoords])
                orCoords += 1
                continue

            if self.tileSurrounded(orCoords):
                wordAcross = self.wordAcross(letter, orCoords)
                if wordAcross.upper() not in self.WORDS:
                    print(f"{orCoords} : {wordAcross.upper()} not in the dictionnary")
                    # raise ValueError(f"{orCoords} : {wordAcross.upper()} not in the dictionnary")
                    return False

            midLetters.append(letter)
            orCoords += 1

        postLetters = self.postLetters(orCoords)

        wordToCount = prevLetters + midLetters + postLetters
        wordToCount = "".join(wordToCount)

        print(wordToCount)

        if wordToCount.upper() not in self.WORDS:
            print(f"{wordToCount.upper()} not in the dictionnary")
            # raise ValueError(f"{wordToCount.upper()} not in the dictionnary")

        return True


if __name__ == '__main__':
    g = Grid([[i * j for j in range(5)]for i in range(3)])
    print(g)
    a = g.copy()
    a[1, 1] = -5
    print(g)
    print(a.data)
    print(g.data)
