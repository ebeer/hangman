"""
Hangman game that uses basic socket networking
Game Status objects contain the messages passed between client and server
these are serialized to json to be passed between client and server.

This client merely displays the plain text from the status object
~~snazzy ascii art

"""
import sys
import game
from game import Game_Status
import socket




if __name__ == "__main__":


    if len(sys.argv) > 2:
        host = sys.argv[1],sys.argv[2]
    else:
        host = '',50000
    
    size = 5000 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((host))

    s.send(game.INITIAL_CONNECT_MESSAGE)

    while True:
        #all messages passed between client and server are game status object
        my_status = Game_Status()
        data = s.recv(size)
        my_status.load_from_json(data)
        
        if (my_status.get_status_flag() > game.IN_PLAY):
            print my_status.get_display() #game over
            break
        elif (my_status.get_status_flag() == game.WAIT_TO_GET_WORD):
            print my_status.get_display() #we are waiting for opponent connect
            continue
        else:
            user_input = raw_input(my_status.get_display()) 
            my_status.set_user_input(user_input)
            s.sendall(my_status.save_to_json())


    s.close() 

