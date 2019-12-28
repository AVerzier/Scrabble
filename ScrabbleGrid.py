
import numpy as np
import pandas as pd
import json
import re


class ScrabbleGrid:

    def __init__(self, data=None, lang="FR"):

        self.grid = {"row": np.zeros((15, 15), dtype=object)}
        self.grid["row"].fill(" ")
        self.grid["col"] = self.grid["row"].view().T

        self.lang = lang
        # Dictionnary
        with open(f"Words/SCRDICT {self.lang}.json", "r") as file:
            self.WORDS = json.load(file)
        # Points on each letter
        with open(f"Letters/letters {self.lang}.csv", "r") as file:
            self.letters = pd.read_csv(file, index_col=0)

        self.wordMult = {"row": np.loadtxt("wordMult.txt", dtype="uint8")}
        self.wordMult["col"] = self.wordMult["row"].view().T

        self.letMult = {"row": np.loadtxt("letMult.txt", dtype="uint8")}
        self.letMult["col"] = self.letMult["row"].view().T

        self.gridPts = {"row": np.zeros_like(self.grid["row"], dtype="uint8")}
        self.gridPts["col"] = self.gridPts["row"].view().T

    def __str__(self):
        return str(self.grid["row"])

    def swichij(f):
        def wrapper(self, i, j, axis, *args, **kwargs):
            if axis == "col":
                i, j = j, i
            return f(self, i, j, axis, *args, **kwargs)
        return wrapper

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

    @swichij
    def placeWord(self, i, j, axis, word):
        """Put the Letters on the grid"""

        length = len(word)

        coords = np.index_exp[i, j:j+length]

        self.grid[axis][coords] = list(word)
        self.gridPts[axis][coords] = [self.letters.loc[let]["Points"] for let in word]

    @swichij
    def neighbours(self, i, j, axis):
        """Return the indices of the neighbourhood"""

        free = np.flatnonzero(np.concatenate(
            ([" "], self.grid[axis][:i, j], [0], self.grid[axis][i+1:, j], [" "])) == " ")-1
        ind = np.searchsorted(free, i)

        return np.index_exp[free[ind-1]+1: free[ind], j]

        if axis == "row":
            free = np.flatnonzero(np.concatenate(
                ([" "], self.grid[:i, j], [0], self.grid[i+1:, j], [" "])) == " ")-1
            ind = np.searchsorted(free, i)
            return (slice(free[ind-1]+1, free[ind]), j)
        else:
            free = np.flatnonzero(np.concatenate(
                ([" "], self.grid[i, :j], [0], self.grid[i, j+1:], [" "])) == " ")-1
            ind = np.searchsorted(free, j)
            return (i, slice(free[ind-1]+1, free[ind]))

        # if axis == "row":
        #     prev = self.grid[i, :j]
        #     post = self.grid[i, j+1:]
        # else:
        #     prev = self.grid[:i, j]
        #     post = self.grid[i+1:, j]

        # return np.any(self.grid[coords] != " ")

    @swichij
    def wordAcross(self, i, j, axis, letter):
        """Return the word made accross"""

        coords = self.neighbours(i, j, axis)

        wordAcross = self.arr2str(self.grid[axis][coords]).replace(" ", letter, 1)

        return wordAcross

        # if axis == "row":
        #     axis = "col"
        # else:
        #     axis = "row"

        # prevLetters = self.prevLetters(i, j, axis)
        # postLetters = self.postLetters(i, j, axis)
        # wordAcross = prevLetters + letter + postLetters
        # return wordAcross

    @swichij
    def prevLetters(self, i, j, axis):
        """Return the the letters going backward"""

        if axis == "col":
            i, j = j, i

        coords = np.index_exp[i, :j]

        prevLetters = self.grid[axis][coords][::-1]
        prevLetters = self.arr2str(prevLetters)
        prevLetters = prevLetters.split(" ")[0]

        return prevLetters[::-1]

    @swichij
    def postLetters(self, i, j, axis):
        """Return the the letters going forward"""

        if axis == "col":
            i, j = j, i

        coords = np.index_exp[i, j+1:]

        postLetters = self.arr2str(self.grid[axis][coords])
        postLetters = postLetters.split(" ")[0]

        return postLetters

    def countPtAcross(self, i, j, axis, letter):
        """Count the points made by the word beside"""

        print(self.neighbours(i, j, axis))

        pts = self.gridPts[axis][self.neighbours(i, j, axis)]

        if len(pts) <= 1:  # No neigbour
            return 0

        letPts = self.letters.loc[letter]["Points"] * self.letMult[axis][i, j]

        return (np.sum(pts)+letPts)*self.wordMult[axis][i, j]

    @swichij
    def countPtWord(self, i, j, axis, word):
        """Count the points of the word made"""

        length = len(word)

        word = re.sub(r"[a-z]", "?", word)

        coords = np.index_exp[i, j:j+length]

        letMult = np.where(self.grid[axis] != " ", self.letMult[axis], 1)[coords]
        wordMult = np.prod(np.where(self.grid[axis] != " ", self.wordMult[axis], 1)[coords])
        letPts = np.array([self.letters.loc[let]["Points"] for let in word])

        pts = np.sum(letPts * letMult) * wordMult

        J, I = np.indices(self.grid[axis].shape)

        arr = np.zeros((4, length), dtype=object)

        np.stack((I[coords], J[coords], [axis]*length, list(word)), axis=1, out=arr)

        print(arr)
        arr = np.apply_along_axis(lambda a: self.countPtAcross(*a), 1, arr)
        print(arr)

    @swichij
    def isValid(self, i, j, axis, word):
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

        # Test word across

        if not re.fullmatch(letters, word):
            print("Do not match with the grid")
            return False

        return True

        wordToCount = self.replace(r"\[[^\]]*\]", word, letters)

        return wordToCount


if __name__ == '__main__':
    scrg = ScrabbleGrid()
    scrg.placeWord(7, 6, "row", "ARBRE")
    scrg.placeWord(7, 0, "row", "MIMES")
    print(scrg)
    print(scrg.countPtWord(7, 5, "row", "ETRE"))
