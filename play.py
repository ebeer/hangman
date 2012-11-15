"""
hangman - starting with basic one player

"""

import random
import sys
import re

def question_display(solution, display_string, guess):
    if (guess == "") & (display_string == ""):
        #initialize
        for i in range(len(solution)):
            display_string += " _"
        success = False
    elif (guess != ""):
        found = [match.start() for match in re.finditer(re.escape(guess), solution, re.IGNORECASE)]
        if len(found) > 0:
            success = True
            for char_index in found:
                if char_index == 0:
                    char_index += 1
                else:
                    char_index = char_index * 2 + 1
            display_string = display_string[0:char_index] + guess + display_string[char_index+1:]
            
        else:  #not found
            success = False
                
    return display_string, success



if __name__ == "__main__":

    max_failures = 6
    
    #initially starting from a set list of words
    #move to reading from text files or web
    wordlist = ("across", "beyond", "carnival", "document")
    failed_guess = ""
    display_string =""
    wrong = 0
    correct = 0
    
    solution = random.choice(wordlist);
    unique_letters = len(set (''.join(solution)))
    print "Hello, you have " + str(max_failures) + " chances to guess wrong."
    print "enter * to quit\n"
    guess = ""
    success = False

    display_string, success = question_display(solution, display_string, guess)
    print display_string

    while ((wrong < max_failures) & (correct < unique_letters)):
        #need to make sure this is only one character
        guess = raw_input("please enter one character: ")
        print "\n\n"
        display_string, success = question_display(solution, display_string, guess)
        if guess == '*':
            print "quitting the game"
            break #quit the game
        if ((guess != "") & (success != True)):
            failed_guess = failed_guess + guess + " "
            wrong += 1
           
        else:
            correct += 1

        print "your guesses so far: " + failed_guess
        print display_string
            
        


    print "thanks for playing!"
    if (correct == unique_letters):
        print "you win!"
    else:
        print "the answer is " + solution
    
        
