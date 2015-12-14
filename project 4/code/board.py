__author__ = 'Haohan'

""" This file defines all related classes for the environment
    representation and utility and policy representations """


def Enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


Ops = Enum('UP', 'DOWN', 'LEFT', 'RIGHT', 'TERMINATE', 'BLOCK', 'UNKNOWN')


class Board:

    """ Class to represent the environment and rewards for each tile """

    def __init__(self, path):
        self.board = []
        self.reward = []
        with open(path, 'r') as file:
            for line in file.readlines():
                self.board.append(line.split())

        self.height = len(self.board)
        self.width = len(self.board[0])

    def set_reward(self, reward):
        self.reward = []
        for row in self.board:
            line = []
            for element in row:
                line.append(reward[element])
            self.reward.append(line)


class Utility:

    """ Class to represent the utility of an height * width environment """
    def __init__(self, height, width):
        self.value = [[0]*width for _ in range(height)]


class Policy:

    """ Class to represent a policy for a given Board """

    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.policy = [[Ops.UNKNOWN] * width for _ in range(height)]

    def equals(self, p):
        if self.width != p.width or self.height != p.height:
            return False
        if self.policy != p.policy:
            return False

        return True
