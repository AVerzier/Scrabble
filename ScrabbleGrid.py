
import numpy as np
import pandas as pd
import json
import re


class ScrabbleGrid:
    """
    Use numpy array as a Scrabble Board
    Count points
    Does not implement rules

    axis:
        0: column
        1: row
    """

    def __init__(self, lang="FR"):

        self.grid = np.zeros((15, 15), dtype=object)
        self.grid.fill(" ")

        self.lang = lang

        # Points on each letter
        with open(f"Letters/letters {self.lang}.csv", "r") as file:
            letters = pd.read_csv(file, index_col=0)
            self.Points = letters["Points"].to_dict()

        self.wordMult = np.loadtxt("wordMult.txt", dtype="uint8")

        self.letMult = np.loadtxt("letMult.txt", dtype="uint8")

        self.gridPts = np.zeros_like(self.grid, dtype="uint8")

    def __str__(self):
        return str(self.grid)

    @staticmethod
    def arr2str(arr):
        return "".join(map(str, arr))

    def placeWord(self, word, i, j, axis):
        """Put the Letters on the grid"""

        length = len(word)

        if axis == 1:
            coords = np.index_exp[i, j:j+length]
        else:
            coords = np.index_exp[i:i+length, j]

        self.grid[coords] = list(word)
        self.gridPts[coords] = [self.Points[let] for let in word]
        self.letMult[coords] = 1
        self.wordMult[coords] = 1

    def prevInd(self, i, j, axis):
        """Return the indices of the prev non-free tiles along axis"""
        if axis == 1:
            prev = np.concatenate(([" "], self.grid[i, :j]))
            free = np.flatnonzero(prev == " ")[-1]
            return np.index_exp[i, free+1:j]
        else:
            prev = np.concatenate(([" "], self.grid[:i, j]))
            free = np.flatnonzero(prev == " ")[-1]
            return np.index_exp[free+1:i, j]

    def postInd(self, i, j, axis):
        """Return the indices of the post non-free tiles along axis"""
        if axis == 1:
            post = np.concatenate((self.grid[i, j+1:], [" "]))
            free = np.flatnonzero(post == " ")[0] + j+1
            return np.index_exp[i, j+1:free]
        else:
            post = np.concatenate((self.grid[i+1:, j], [" "]))
            free = np.flatnonzero(post == " ")[0] + i+1
            return np.index_exp[i+1:free, j]

    def prevLetters(self, i, j, axis):
        """Return the str letters going backward"""
        coords = self.prevInd(i, j, axis)
        return self.arr2str(self.grid[coords])

    def postLetters(self, i, j, axis):
        """Return the str letters going forward"""
        coords = self.postInd(i, j, axis)
        return self.arr2str(self.grid[coords])

    def wordAcross(self, letter, i, j, axis):
        """Return the word made accross"""

        # Reverse axis
        axis = 1-axis

        prevLetters = self.prevLetters(i, j, axis)
        postLetters = self.postLetters(i, j, axis)
        return prevLetters+letter+postLetters

    def countPtAcross(self, letter, i, j, axis):
        """Count the points made by the word beside"""

        # Reverse axis
        axis = 1-axis

        pts = self.Points[letter]*self.letMult[i, j]
        prev = self.prevInd(i, j, axis)
        post = self.postInd(i, j, axis)
        pts += np.sum(self.gridPts[prev]) + np.sum(self.gridPts[post])
        return pts * self.wordMult[i, j]

    def countPtWord(self, word, i, j, axis):
        """Count the points of the word made"""

        length = len(word)
        word = re.sub(r"[a-z]", ",", word)

        if axis == 1:
            coords = np.index_exp[i, j:j+length]
            I = [i]*length
            J = range(j, j+length)
        else:
            coords = np.index_exp[i:i+length, j]
            I = range(i, i+length)
            J = [j]*length

        letPts = [self.Points[let] for let in word]

        pts = np.sum(self.letMult[coords] * letPts) * np.prod(self.wordMult[coords])

        arr = np.empty((3, length), dtype=object)
        np.stack((list(word), I, J), out=arr)

        across = np.apply_along_axis(lambda a: self.countPtAcross(*a, axis), 0, arr)

        pts += np.sum(across)

        if len(np.flatnonzero(self.grid[coords] == " ")) == 7:
            pts += 50

        return pts


if __name__ == '__main__':
    scrg = ScrabbleGrid()
    scrg.placeWord("ARBRE", 7, 6, 1)
    scrg.placeWord("MIMES", 4, 10, 0)
    print(scrg)
    print(scrg.countPtWord("ETAIENT", 7, 5, 0))
    # scrg.postInd(7, 5, 0)
