
import numpy as np
import pandas as pd
import json
import re


class ScrabbleGrid:

    def __init__(self, lang="FR"):

        self.grid = np.zeros((15, 15), dtype=object)
        self.grid.fill(" ")

        self.lang = lang
        # Dictionnary
        with open(f"Words/SCRDICT {self.lang}.json", "r") as file:
            self.WORDS = json.load(file)
        # Points on each letter
        with open(f"Letters/letters {self.lang}.csv", "r") as file:
            self.letters = pd.read_csv(file, index_col=0)

        self.wordMult = np.loadtxt("wordMult.txt", dtype="uint8")

        self.letMult = np.loadtxt("letMult.txt", dtype="uint8")

        self.gridPts = np.zeros_like(self.grid, dtype="uint8")

    def __str__(self):
        return str(self.grid)

    @staticmethod
    def arr2str(arr):
        return "".join(map(str, arr))

    @staticmethod
    def replace(pattern, new, old):
        """Replace with indices"""
        ret = old
        span = 0
        for m in re.finditer(pattern, ret):
            ind = m.start()
            match = m.group()
            ret = ret.replace(match, new[ind-span])
            span += len(match)-1
        return ret

    def placeWord(self, word, i, j, axis):
        """Put the Letters on the grid"""

        length = len(word)

        if axis == "row":
            coords = (i, slice(j, j+length))
        else:
            coords = (slice(i, i+length), j)

        self.grid[coords] = list(word)
        self.gridPts[coords] = [self.letters.loc[let]["Points"] for let in word]

    def neighbours(self, i, j, axis):
        """Return the indices of the across neighbourhood"""

        if axis == "row":
            prev = np.concatenate([" "], self.grid[:i, j])
            post = np.concatenate(self.grid[i+1:, j], [" "])
            inf = np.flatnonzero(prev == " ")[-1]+1
            sub = np.flatnonzero(prev == " ")[0]
            return np.index_exp[inf:sub, j]
        else:
            prev = np.concatenate([" "], self.grid[i, :j])
            post = np.concatenate(self.grid[i, j+1:], [" "])
            inf = np.flatnonzero(prev == " ")[-1]+1
            sub = np.flatnonzero(prev == " ")[0]
            return np.index_exp[i, inf:sub]

    def wordAcross(self, letter, i, j, axis):
        """Return the word made accross"""

        if axis == "row":
            axis = "col"
        else:
            axis = "row"

        prevLetters = self.prevLetters(i, j, axis)
        postLetters = self.postLetters(i, j, axis)
        wordAcross = prevLetters + letter + postLetters
        return wordAcross

    def prevLetters(self, i, j, axis):
        """Return the the letters going backward"""

        if axis == "row":
            coords = (i, slice(j))
        else:
            coords = (slice(i), j)

        prevLetters = self.grid[coords][::-1]
        prevLetters = self.arr2str(prevLetters)
        prevLetters = prevLetters.split(" ")[0]

        return prevLetters[::-1]

    def postLetters(self, i, j, axis):
        """Return the the letters going forward"""

        if axis == "row":
            coords = (i, slice(j+1, None))
        else:
            coords = (slice(i+1, None), j)

        postLetters = self.arr2str(self.grid[coords])
        postLetters = postLetters.split(" ")[0]

        return postLetters

    def countPtAcross(self, letter, i, j, axis):
        """Count the points made by the word beside"""

        if axis == "row":
            coords = (i, slice(j))
        else:
            coords = (slice(i), j)

        pts = 0
        mult = 1

        wordAcross = self.wordAcross(letter, i, j, axis)
        for let in wordAcross:
            if let.isupper():
                pts += self.letters.loc[let]["Points"]

        # letter on bonus tile:
        bonusCase = self.gridBonus[i, j]
        if bonusCase == 1:
            if letter.isupper():
                pts += self.letters.loc[letter]["Points"]
        elif bonusCase == 2:
            if letter.isupper():
                pts += self.letters.loc[letter]["Points"] * 2
        elif bonusCase == 3:
            mult *= 2
        elif bonusCase == 4:
            mult *= 3

        return pts * mult

    def countPtWord(self, wordToCount, i, j, axis):
        """Count the points of the word made"""

        length = len(wordToCount)

        if axis == "row":
            coords = (i, slice(j, j+length))
        else:
            coords = (slice(i, i+length), j)

        totPts = 0
        wordPts = 0
        mult = 1
        nbLetUsed = 0

        for letter, case, bonus in zip(wordToCount, self.grid[coords], self.gridBonus[coords]):
            if letter.isupper():
                wordPts += self.letters.loc[letter]["Points"]

            if case != " ":  # If the tile was occupied:
                continue

            nbLetUsed += 1

            if bonus == 1:
                if letter.isupper():
                    wordPts += self.letters.loc[letter]["Points"]
            elif bonus == 2:
                if letter.isupper():
                    wordPts += self.letters.loc[letter]["Points"] * 2
            elif bonus == 3:
                mult *= 2
            elif bonus == 4:
                mult *= 3

            if self.neighbours(i, j, axis):
                totPts += self.countPtAcross(letter, i, j, axis)

            orCoords += 1

        totPts += wordPts * mult

        if nbLetUsed == 7:
            totPts += 50

        return totPts

    def isConnected(self, newLetters, i, j, axis):

        if self.grid[orCoords - 1]:  # Letter before
            return True

        for letter in newLetters:
            if self.neighbours(i, j, axis):
                return True
            orCoords += 1

        if self.grid[orCoords]:  # Letter after
            return True

        return False

    def isValid(self, word, i, j, axis):
        """Check if Letters added make legit play"""
        length = len(word)
        if not re.search(f"^{word.upper()}$", self.WORDS[str(length)], re.M):
            print(f"{word} not in the dictionnary")
            return False

        if np.all(self.grid == r"[\w]"):  # Empty grid, first play
            if axis == "row":
                if not (i == 7 and 7 in range(j, j+length)):
                    return False
            else:
                if not (7 in range(i, i+length) and j == 7):
                    return False
            return True

        if axis == "row":
            coords = (i, slice(j, j+length))
        else:
            coords = (slice(i, i+length), j)

        letters = self.arr2str(self.grid[coords])

        if not re.fullmatch(letters, word):
            print("Do not match with the grid")
            return False

        return True

        wordToCount = self.replace(r"\[[^\]]*\]", word, letters)

        return wordToCount


if __name__ == '__main__':
    scrg = ScrabbleGrid()
    scrg.placeWord("ARBRE", 7, 6, "row")
    scrg.placeWord("MIMES", 4, 10, "col")
    print(scrg)
