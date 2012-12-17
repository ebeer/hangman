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
class Game_Status:
    
    def __init__(self):
        self.status_message = {"display": "","response": "","flag": WAIT_FOR_INIT}
        
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
        
        




#container for game(s) coordinated 'trading' of words and status communications
class Match:
    
    
    def __init__(self):
        self.waiting = True
        self.match_dict = {} #indexes the game objects by the associated socket file number
        self.is_two_player =  False
        self.socketa = ""
        self.socketb = ""
        self.players = 0

    #prompt user to either start 1 player or 2 player game    
    def prompt_for_multiplayer(self):
        start = Game_Status()
        start.set_status_flag(WAIT_FOR_INIT)
        start.set_display("Would you like to wait for opponent(Y) or play as 1 player(N)?\n")
        self.players +=1
        return start

    #process user response and set flags for 1 or 2 player game
    def process_multi_request(self, answer):
        if answer.get_user_input() in ONE_PLAYER_RESPONSE :
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
            player1 = Game(socket1)
            self.match_dict[socket1.fileno()] = player1
            status = Game_Status()
            status.set_from_game(player1)
            status.set_status_flag(WAIT_TO_GIVE_WORD)
            status.set_display(player1.init_directions() + "\n")
        else:
            #two player game and this is player #2
            #prompt for word and send go to both 
            self.socketb = socket1
            player2 = Game(socket1)
            self.match_dict[socket1.fileno()] = player2
            status = Game_Status()
            status.set_from_game(player2)
            status.set_status_flag(WAIT_TO_GIVE_WORD)
            status.set_display(player2.init_directions() + "\n")
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
        #print ("set opp word rec'd " + str(my_game.get_opponent_word()))
        opp.set_word(my_game.get_opponent_word())
        #print ("my game being set to " + str(opp.get_opponent_word()))
        my_game.set_word(opp.get_opponent_word())

        self.waiting = False
        return True
        

     #start one player game and initialize accordingly   
    def start_1player(self, socket1):
        player1= Game(socket1)
        
        #one player game reads from text file of source words
        wordlist = open(ONE_PLAYER_WORD_FILE, 'r').readlines()
        words = [word.strip() for word in wordlist]
        solution = random.choice(words)

        done = player1.set_word(solution)
       # print "done= " + str(done) + " solution= " + solution
        self.match_dict[socket1.fileno()] = player1
        self.is_two_player = False
        self.waiting = False
        status = Game_Status()
        status.set_from_game(player1)
        status.set_display(player1.get_directions())
        return status


        
    def process_game_response (self, socket1, game_status):
        game_status_opp = Game_Status()
        my_game = self.match_dict[socket1.fileno()] #retrieve game object
       
        if (my_game.get_status() == WAIT_TO_GIVE_WORD):
            #user has entered a word for the opponent
            done = my_game.init_for_opponent(game_status.get_user_input())
            if (not self.set_opponent_word(socket1)):
                game_status.set_status_flag(WAIT_TO_GET_WORD)
                game_status.set_display("thank you... waiting for opponent connect")
            else:
                game_status.set_status_flag(READY)
                if (self.players == 2):
                    game_status.set_display(my_game.get_directions())
                    opp_game = self.get_opponent_game(socket1)
                    game_status_opp.set_from_game(opp_game)
                    game_status_opp.set_display(opp_game.get_directions())
                
        elif (my_game.get_status() == IN_PLAY) or (my_game.get_status() == READY):
            done, response = my_game.check_guess(game_status.get_user_input())
            game_status.set_display(response)
            game_status.set_status_flag(done)
           
            if (self.is_two_player) & (done > IN_PLAY): #player just ended the game/lost/won, send msg to opponent
                if socket1 == socketa:
                    opp_game = self.match_dict[socketb]
                else:
                    opp_game = self.match_dict[socketa]

                opp_game.opponent_game_over(done)

        return game_status, game_status_opp
           
            



        


#logic container for individual game    
class Game:
    
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

    def __init__ (self, socket):
        self._solution = ""
        self._failed_guesses = ""
        self._display_string = ""
        self._unique_letters = 0
        self._wrong_count = 0
        self._correct_count = 0
        self._status = WAIT_FOR_INIT 
        self._response = ""


    def init_directions(self):
        self.set_status(WAIT_TO_GIVE_WORD)
        return "Please enter an up to " + str(self._max_word_length) + " letter word for your opponent to guess:\n"

    def init_for_opponent(self, word):
        self._opponent = word
        return True
      
    def get_opponent_word(self):
        return self._opponent
    
    def set_status(self, flag):
        self._status = flag

    def get_status(self):
        return self._status


    def get_display_string(self):
        return self._display_string


    def get_directions(self):
        return "Hello, you have " + str(self._max_wrong) + " chances to guess wrong.\nEnter " + QUIT_CHARACTER + " to quit.\n" + self._display_string  + "\n" 
    
    
    def get_response(self):
        return self._response


    def set_word(self, word):
        self._solution = word
        self._display_string = " _" * len(word)
        self._unique_letters = len(set (''.join(word)))
        self._status = READY
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

    

