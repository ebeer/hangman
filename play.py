"""
hangman - starting with basic one player

"""

import random
import sys
from game import Game




if __name__ == "__main__":

    max_failures = 6

    #initially starting from a set list of words
    #move to reading from text files or web
    wordlist = ("across", "beyond", "carnival", "document")
    solution = random.choice(wordlist);

    my_game = Game()
    my_game.set_difficulty(10, max_failures)

    #this will change to being done by the other player
    my_game.set_word(solution)

    print my_game.get_directions()
    
    
    done = False
    while not(done):

        guess = raw_input("please enter one character or try to solve the puzzle: ")
        print "\n\n"

        done, response = my_game.check_guess(guess)

        print response




