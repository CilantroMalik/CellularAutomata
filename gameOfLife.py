import random
import time
import os
from pprint import pprint

BOARD_SIZE = 50
DENSITY_FACTOR = 0.3
SPEED = 0.5


board = []
for row in range(BOARD_SIZE):
    tempRow = []
    for col in range(BOARD_SIZE):
        tempRow.append("▉▉" if random.random() <= DENSITY_FACTOR else "  ")
    board.append(tempRow)

def adj(row, col):
    adjacents = []
    possibleIndices = [(row-1, col-1), (row-1, col+1), (row+1, col-1), (row+1, col+1), (row-1, col), (row+1, col), (row, col-1), (row, col+1)]
    for coords in possibleIndices:
        if 0 <= coords[0] < BOARD_SIZE and 0 <= coords[1] < BOARD_SIZE:
            adjacents.append(coords)
    return adjacents


def printBoard():
    for r in range(BOARD_SIZE):
        print("|".join(board[r]))
        #print("—"*(2*BOARD_SIZE+BOARD_SIZE-1))


os.system('clear')
printBoard()
time.sleep(SPEED)
while True:
    os.system('clear')
    willBeBorn = []
    willDie = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            countAlive = 0
            for cell in adj(row, col):
                if board[cell[0]][cell[1]] == "▉▉":
                    countAlive += 1
            if countAlive > 3 and board[row][col] == "▉▉":
                willDie.append((row, col))
            if countAlive < 2 and board[row][col] == "▉▉":
                willDie.append((row, col))
            if countAlive == 3 and board[row][col] == "  ":
                willBeBorn.append((row, col))
    for cell in willBeBorn:
        board[cell[0]][cell[1]] = "▉▉"
    for cell in willDie:
        board[cell[0]][cell[1]] = "  "
    printBoard()
    time.sleep(SPEED)
