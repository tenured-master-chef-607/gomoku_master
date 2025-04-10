"""
Gomoku Master
Author: TJ Qiu
Copyright © 2023 TJ Qiu. All rights reserved.
"""

from gui import GomokuGUI

def main():
    print("Welcome to Gomoku!")
    print("You can choose to play as either Black or White")
    print("Click on the board to place your stones")
    print("Click anywhere after game over to play again")
    
    game = GomokuGUI()
    game.run()

if __name__ == "__main__":
    main() 