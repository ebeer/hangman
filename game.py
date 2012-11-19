"""
single game object
tracks status for this one game.

"""

import re


class Game:
    solution = ""
    failed_guesses = ""
    max_word_length = 6
    display_string = ""
    done = False;
    unique_letters = 0
    wrong_count = 0
    correct_count = 0
    max_wrong = 6
    quit_character = "*"


    def set_difficulty(self, word_length, max_wrong):
        self.max_word_length = word_length
        self.max_wrong = max_wrong


    def get_display_string(self):
        return self.display_string


    def get_directions(self):
        return "Hello, you have " + str(self.max_wrong) + " chances to guess wrong.\nEnter " + self.quit_character +" to quit\n"+ self.display_string
    
    
    def get_response(self):
        return self.response


    def set_word(self, word):
        if len(word) <= self.max_word_length:
            self.solution = word
            self.display_string = " _" * len(word)
            self.unique_letters = len(set (''.join(word)))
            return True
        else:
            return False


    def get_word(self):
        return self.solution



    def is_valid_guess(self, guess):
        if (guess == "") or (guess in self.failed_guesses) or (guess in self.display_string):
            return False
        return True

    def is_quit_game(self, guess):
        if (guess == self.quit_character):
            self.done = True
            self.response = "Thank you for playing \nThe answer was: " + self.solution
            return True

    def check_guess(self, guess):
        if ((not self.is_quit_game(guess)) and self.is_valid_guess(guess)):
            if len(guess) > 1:
               return self.check_for_solved(guess)
            else:
                found = [match.start() for match in re.finditer(re.escape(guess), self.solution, re.IGNORECASE)]
                if len(found) > 0:
                    self.response = "Good Guess!\n"
                    self.correct_count += 1

                    for char_index in found:
                        if char_index == 0:
                            char_index += 1
                        else:
                            char_index = char_index * 2 + 1
                        self.display_string = self.display_string[0:char_index] + guess + self.display_string[char_index+1:]

                    self.response = self.response + self.display_string
                else:
                    self.failed_guesses = self.failed_guesses + " "+ guess
                    self.response = "Sorry!\n You have guessed: " + self.failed_guesses + "\n"
                    self.wrong_count +=1
                    
                    if (self.wrong_count == self.max_wrong):
                        self.done = True
                        self.winner = False
                        self.response = self.response + "Sorry, you lost the game\nThe answer was: " + self.solution
                    else:
                        self.response = self.response + "\n" + self.display_string
                           
                if (self.correct_count == self.unique_letters):
                    self.response = self.response + "Congratualtions! You win!\n"
                    self.done = True
                    self.winner = True

        return self.done, self.response



    def check_for_solved(self, guess):
        if ((guess.upper()).strip(" ") == (self.solution.upper()).strip(" ")):
            self.done = True
            self.response = "Congratulations!  You win"
            self.winner = True
        else:
            self.done = True
            self.response = "Sorry, that was not correct\n The solution is: " + self.solution
            self.winner = False
        return self.done, self.response


