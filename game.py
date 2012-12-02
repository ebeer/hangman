"""
single game object

match container for 2 game matchup or processing of single player

game status message for communication with the client

"""

import re
import json
import random

WAIT_FOR_INIT = 0
READY = 1
IN_PLAY = 2
LOST = 3
WON = 4
QUIT_CHARACTER = "*"
ONE_PLAYER_RESPONSE = ("N", "n")


class Game_Status:
    status_message = {"display": "","response": "","flag": WAIT_FOR_INIT}

    def set_from_game(self, game_obj):
        self.set_status_flag(game_obj.get_status())   
    
    def get_status_flag(self):
        return self.status_message["flag"]

    def set_status_flag(self, flag):
        self.status_message["flag"] = flag

    def get_display(self):
        return self.status_message["display"]

    def set_display(self, display_message):
        self.status_message["display"] = display_message

    def get_user_input(self):
        return self.status_message["response"]

    def set_user_input(self, user_input):
        self.status_message["response"] = user_input

    def save_to_json(self):
        return json.dumps(self.status_message)

    def load_from_json(self, json_data):
        self.status_message = json.loads(json_data)
        
        





class Match:
    match_dict = {} #indexes the game objects by the associated socket file number
    is_two_player =  False
    socketa = ""
    socketb = ""
    waiting = True
    players = 0
    
    def __init__(self):
        waiting = True

    def process_multi_request(self, answer):
        if answer.get_user_input() in ONE_PLAYER_RESPONSE :
            waiting = False
            is_two_player = False
            return False
        else:
            waiting = True
            is_two_player = True
            return True
        
    def prompt_for_multiplayer(self):
        start = Game_Status()
        start.set_status_flag(WAIT_FOR_INIT)
        start.set_display("Would you like to wait for opponent(Y) or play as 1 player(N)?\n")
        self.players +=1
        return start
        
    def start_2player(self):
        player1 = Game(socketa)
        player2 = Game(socketb)
        
        self.match_dict[socket1.fileno()] = player1
        self.match_dict[socket2.fileno()] = player2

        self.is_two_player = True
        self.waiting = False
        return player1, player2


        
    def start_1player(self, socket1):
        player1= Game(socket1)
        
        #one player game reads from text file of source words
        wordlist = open('source words.txt', 'r').readlines()
        words = [word.strip() for word in wordlist]
        solution = random.choice(words)

        done = player1.set_word(solution)
       # print "done= " + str(done) + " solution= " + solution
        self.match_dict[socket1.fileno()] = player1
        self.is_two_player = False
        self.waiting = False
        status = Game_Status()
        status.set_from_game(player1)
        status.set_display(player1.get_directions() + "\n" )
        return status


        
    def process_game_response (self, socket1, game_status):
        
        my_game = self.match_dict[socket1.fileno()] #retrieve game object
       # print "mygame status is - " + str(my_game.get_status())
        if (my_game.get_status() == WAIT_FOR_INIT):
            #sending word to opponent
            game_status.set_display("hello")
        elif (my_game.get_status() == IN_PLAY) or (my_game.get_status() == READY):
           #print "user entered = " + game_status.get_user_input()
            #print "solution is " + my_game.get_word()
            done, response = my_game.check_guess(game_status.get_user_input())
            game_status.set_display(response)
           # print "response is " + response
            game_status.set_status_flag(done)
           
            if (self.is_two_player) & (done > IN_PLAY):
                if socket1 == socketa:
                    opp_game = self.match_dict[socketb]
                else:
                    opp_game = self.match_dict[socketa]

                opp_game.opponent_game_over(done)
            return game_status
           
            



        

    
class Game:
    _solution = ""
    _failed_guesses = ""
    _max_word_length = 10
    _display_string = ""
    _unique_letters = 0
    _wrong_count = 0
    _correct_count = 0
    _max_wrong = 6
    _status = 0
    _opponent = ""
    _response = ""
    _player_network_connection = ""

    _hangman = [
"""
            -----
            |   |
                |
                |
                |
                |
            ---------
""",
"""
            -----
            |   |
            O   |
                |
                |
                |
            ---------
""",

"""
            -----
            |   |
            O   |
            |   |
                |
                |
            ---------
""",
"""
            -----
            |   |
            O   |
            |\  |
                |
                |
            ---------
""",
"""
            -----
            |   |
            O   |
           /|\  |
                |
                |
            ---------
""",
"""
            -----
            |   |
            O   |
           /|\  |
             \  |
                |
            ---------
""",
"""
            -----
            |   |
            O   |
           /|\  |
           / \  |
                |
            ---------
"""]

    def __init__ (self, socket):
        _player_network_connection = socket
        self.set_status(WAIT_FOR_INIT)

    def get_network_connection(self):
        return _player_network_connection
    
    def init_directions(self):
        return "Please enter an up to " + str(self._max_word_length) + " letter word for your opponent to guess:\n"

    def init_for_opponent(self, word):
        if len(word) < self._max_word_length:
            self._opponent = word
            return True
        else:
            return False
        
    def set_status(self, flag):
        self._status = flag

    def get_status(self):
        return self._status


    def get_display_string(self):
        return self._display_string


    def get_directions(self):
        return "Hello, you have " + str(self._max_wrong) + " chances to guess wrong.\nEnter " + QUIT_CHARACTER + " to quit.\n" + self._display_string
    
    
    def get_response(self):
        return self._response


    def set_word(self, word):
        if len(word) <= self._max_word_length:
            self._solution = word
            self._display_string = " _" * len(word)
            self._unique_letters = len(set (''.join(word)))
            self._status = READY
        else:
            self._status = WAIT_FOR_INIT
        return self._status


    def get_word(self):
        return self._solution



    def _is_valid_guess(self, guess):
        if (guess == "") or (guess in self._failed_guesses) or (guess in self._display_string):
            return False
        return True

    def _is_quit_game(self, guess):
        if (guess == QUIT_CHARACTER):
            self._response = "Thank you for playing \nThe answer was: " + self._solution
            self._status = LOST
            return self._status
        
    def check_guess(self, guess):
        if self._status > IN_PLAY:
            return self._status, self._response

        guess.strip
        self._status = IN_PLAY
        if ((not self._is_quit_game(guess)) and self._is_valid_guess(guess)):
            if len(guess) > 1:
               return self.check_for_solved(guess)
            else:
                found = [match.start() for match in re.finditer(re.escape(guess), self._solution, re.IGNORECASE)]
                if len(found) > 0:
                    self._response = "Good Guess!\n" + self._hangman[self._wrong_count] + "\n"
                    self._correct_count += 1

                    for char_index in found:
                        if char_index == 0:
                            char_index += 1
                        else:
                            char_index = char_index * 2 + 1
                        self._display_string = self._display_string[0:char_index] + guess + self._display_string[char_index+1:]

                    self._response = self._response + self._display_string + "\n"
                else:
                    self._failed_guesses = self._failed_guesses + " "+ guess
                    self._response = "Sorry!\n You have guessed: " + self._failed_guesses + "\n"
                    self._wrong_count +=1
                    self._response = self._response + self._hangman[self._wrong_count]
                    if (self._wrong_count == self._max_wrong):
                        self._status = LOST
                        self._response = self._response + "Sorry, you lost the game\nThe answer was: " + self._solution
                    else:
                        self._response = self._response + "\n" + self._display_string + "\n"
                           
                if (self._correct_count == self._unique_letters):
                    self._response = self._response + "Congratualtions! You win!\n"
                    self._status = WON
        return self._status, self._response



    def check_for_solved(self, guess):
        if ((guess.upper()).strip(" ") == (self._solution.upper()).strip(" ")):
            self._response = "Congratulations!  You win\n"
            self._status = WON
        else:
            self._response = "Sorry, that was not correct.\nThe solution is: " + self._solution + "\n"
            self._status = LOST
        return self._status, self._response

    def opponent_game_over(self, status):
        if status == WON :
            self._response = "Sorry!  Your opponent just solved the puzzle!\nYour solutions was: " + self.solution + "\n"
            seld._status = LOST
        else:
            self._response = "Your opponent just lost the game! You win.\nYour solution was: " + self.solution + "\n"
            self._status = WON
        return self._status, self._response

    

