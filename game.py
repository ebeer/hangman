"""
Game Status obects are serialized and passed between the client and server as the game play progresses

Match object is a container for 2 game matchup or processing of single player

Game object processes game logic for each player

"""

import re
import json
import random

#constants
WAIT_FOR_INIT = -1
WAIT_TO_GIVE_WORD = 0
WAIT_TO_GET_WORD = 1
READY = 2
IN_PLAY = 3
LOST = 4
WON = 5
QUIT_CHARACTER = "*"
ONE_PLAYER_RESPONSE = ("N", "n")
INITIAL_CONNECT_MESSAGE = "start"
ONE_PLAYER_WORD_FILE = 'source words.txt'


#communication object passed between client and server
class Game_Status(object):

    def __init__(self):
        self.status_message = {"display": "","response": "","flag": WAIT_FOR_INIT}

    @property
    def status_flag(self):
        return self.status_message["flag"]

    @status_flag.setter
    def status_flag(self, flag):
        self.status_message["flag"] = flag

    @property
    def display(self):
        return self.status_message["display"]

    @display.setter
    def display(self, display_message):
        self.status_message["display"] = display_message

    @property
    def user_input(self):
        return self.status_message["response"]

    @user_input.setter
    def user_input(self, user_input):
        self.status_message["response"] = user_input

    def save_to_json(self):
        return json.dumps(self.status_message)

    def load_from_json(self, json_data):
        self.status_message = json.loads(json_data)






#container for game(s) coordinated 'trading' of words and status communications
class Match(object):


    def __init__(self):
        self.waiting = True
        self.match_dict = {} #indexes the game objects by the associated socket file number
        self.is_two_player =  False
        self.socketa = ""
        self.socketb = ""
        self.players = 0

    #prompt user to either start 1 player or 2 player game
    def prompt_for_multiplayer(self):
        print "at prompt"
        start = Game_Status()
        start.status_flag = WAIT_FOR_INIT
        start.display = "Would you like to wait for opponent(Y) or play as 1 player(N)?\n"
        print start.display
        self.players +=1
        print start.save_to_json()
        return start

    #process user response and set flags for 1 or 2 player game
    def process_multi_request(self, answer):
        if answer.user_input in ONE_PLAYER_RESPONSE :
            self.waiting = False
            self.is_two_player = False
            return False
        else:
            self.waiting = True
            self.is_two_player = True
            return True


     #start method for 2 player games
    def start_2player(self, socket1):
       # print ("entering start 2 player function")
        #print ("players connected = " + str(self.players))
        if self.players == 1 :
            #this is player one
            #we are waiting for player 2
            #prompt player 1 for word and wait
            self.socketa = socket1
            print "socketa = " + str(socket1.fileno())
            player1 = Game()
            self.match_dict[socket1.fileno()] = player1
            status = Game_Status()
            status.status_flag = WAIT_TO_GIVE_WORD
            status.display = player1.init_directions() + "\n"
        else:
            #two player game and this is player #2
            #prompt for word and send go to both
            self.socketb = socket1
            print "socketb = " + str(socket1.fileno())
            player2 = Game()
            self.match_dict[socket1.fileno()] = player2
            status = Game_Status()
            status.status_flag = WAIT_TO_GIVE_WORD
            status.display = player2.init_directions() + "\n"
        return status

    #retreive oppenent game object from the match dict, keyed by socket
    def get_opponent_game(self, socket1):
        if (socket1 == self.socketa):
            socket2 = self.socketb
        else:
            socket2 = self.socketa

        opp = self.match_dict[socket2.fileno()]
        return opp


    def set_opponent_word(self, socket1):
        #pass word to opponent game object if any has connected yet
        try:
            my_game = self.match_dict[socket1.fileno()]
            opp = self.get_opponent_game(socket1)
        except:
            return False

        opp.word = my_game.opponent
        my_game.word = opp.opponent

        self.waiting = False
        return True


     #start one player game and initialize accordingly
    def start_1player(self, socket1):
        player1= Game()

        #one player game reads from text file of source words
        wordlist = open(ONE_PLAYER_WORD_FILE, 'r').readlines()
        words = [word.strip() for word in wordlist]
        solution = random.choice(words)

        done = player1.set_word(solution)
        self.match_dict[socket1.fileno()] = player1
        self.is_two_player = False
        self.waiting = False
        status = Game_Status()
        status.status_flag = done
        status.display = player1.get_directions()
        return status



    def process_game_response (self, socket1, game_status):
        game_status_opp = Game_Status()
        my_game = self.match_dict[socket1.fileno()] #retrieve game object

        if my_game.status == WAIT_TO_GIVE_WORD:
            #user has entered a word for the opponent
            my_game.opponent = game_status.user_input
            if not self.set_opponent_word(socket1):
                game_status.status_flag = WAIT_TO_GET_WORD
                game_status.display = "thank you... waiting for opponent connect"
            else:
                game_status.status_flag = READY
                if self.players == 2:
                    game_status.display = my_game.get_directions()
                    opp_game = self.get_opponent_game(socket1)
                    game_status_opp.status_flag = opp_game.status
                    game_status_opp.display = opp_game.get_directions()

        elif (my_game.status == IN_PLAY) or (my_game.status == READY):
            done, response = my_game.check_guess(game_status.user_input)
            game_status.display = response
            game_status.status_flag = done

            if (self.is_two_player) & (done > IN_PLAY): #player just ended the game/lost/won, send msg to opponent
                if socket1 == self.socketa:
                    opp_game = self.match_dict[self.socketb.fileno()]
                else:
                    opp_game = self.match_dict[self.socketa.fileno()]

                opp_game.opponent_game_over(done)

        return game_status, game_status_opp








#logic container for individual game
class Game(object):

    _max_word_length = 10
    _max_wrong = 6
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

    def __init__ (self):
        self._solution = ""
        self._failed_guesses = ""
        self.display_string = ""
        self._unique_letters = 0
        self._wrong_count = 0
        self._correct_count = 0
        self.status = WAIT_FOR_INIT
        self.response = ""
        self.opponent = "" #opponent word to guess

    @property
    def word (self):
        return self._solution

    @word.setter
    def word(self, secret_word):
        self._solution = secret_word
        self.display_string = " _" * len(secret_word)
        self._unique_letters = len(set (''.join(secret_word)))
        self.status = READY                    

    
    def init_directions(self):
        self.status = WAIT_TO_GIVE_WORD
        return "Please enter an up to " + str(self._max_word_length) + " letter word for your opponent to guess:\n"


    def get_directions(self):
        return "Hello, you have " + str(self._max_wrong) + " chances to guess wrong.\nEnter " + QUIT_CHARACTER + " to quit.\n" + self.display_string  + "\n"


    def _is_valid_guess(self, guess):
        if (guess == "") or (guess in self._failed_guesses) or (guess in self.display_string) or not(str.isalpha(str(guess))):
            return False
        return True

    def _is_quit_game(self, guess):
        if guess == QUIT_CHARACTER:
            self.response = "Thank you for playing \nThe answer was: " + self._solution
            self.status = LOST
            return self.status

    def check_guess(self, guess):
        if self.status > IN_PLAY:
            return self.status, self.response

        guess.strip
        self.status = IN_PLAY
        if (not self._is_quit_game(guess)) and self._is_valid_guess(guess):
            if len(guess) > 1:
               return self.check_for_solved(guess)
            else:
                found = [match.start() for match in re.finditer(re.escape(guess), self.word, re.IGNORECASE)]
                if len(found) > 0:
                    self.response = "Good Guess!\n" + self._hangman[self._wrong_count] + "\n"
                    self._correct_count += 1

                    for char_index in found:
                        if char_index == 0:
                            char_index += 1
                        else:
                            char_index = char_index * 2 + 1
                        self.display_string = self.display_string[0:char_index] + guess + self.display_string[char_index+1:]

                    self.response = self.response + self.display_string + "\n"
                else:
                    self._failed_guesses = self._failed_guesses + " "+ guess
                    self.response = "Sorry!\n You have guessed: " + self._failed_guesses + "\n"
                    self._wrong_count +=1
                    self.response = self.response + self._hangman[self._wrong_count]
                    if (self._wrong_count == self._max_wrong):
                        self._status = LOST
                        self.response = self.response + "Sorry, you lost the game\nThe answer was: " + self.word
                    else:
                        self.response = self.response + "\n" + self.display_string + "\n"

                if self._correct_count == self._unique_letters:
                    self.response = self.response + "Congratualtions! You win!\n"
                    self.status = WON
        return self.status, self.response



    def check_for_solved(self, guess):
        if (guess.upper()).strip(" ") == (self.word.upper()).strip(" "):
            self.response = "Congratulations!  You win\n"
            self.status = WON
        else:
            self.response = "Sorry, that was not correct.\nThe solution is: " + self.word + "\n"
            self.status = LOST
        return self.status, self.response

    def opponent_game_over(self, status):
        if status == WON :
            self.response = "Sorry!  Your opponent just solved the puzzle!\nYour solutions was: " + self.word + "\n"
            self.status = LOST
        else:
            self.response = "Your opponent just lost the game! You win.\nYour solution was: " + self.word + "\n"
            self.status = WON
        return self.status, self.response



