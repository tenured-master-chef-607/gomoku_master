from gui import GomokuGUI

def main():
    print("Welcome to Gomoku!")
    print("You are playing as Black, the AI is White")
    print("Click on the board to place your stones")
    print("Click anywhere after game over to play again")
    
    game = GomokuGUI()
    game.run()

if __name__ == "__main__":
    main() 