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

    try:
        s.connect((host))
    except:
        print "Sorry, we are unable to connect to the server\n"
        raise
    
    s.send(game.INITIAL_CONNECT_MESSAGE)

    while True:
        #all messages passed between client and server are game status object
        my_status = Game_Status()
      
        try:
            data = s.recv(size)
            #print data
            my_status.load_from_json(data)
        except:
            print "Sorry, an error occured:  game exiting\n"
            s.close()
            break
        
        if my_status.status_flag > game.IN_PLAY:
            print my_status.display #game over
            break
        elif my_status.status_flag == game.WAIT_TO_GET_WORD:
            print my_status.display #we are waiting for opponent connect
            continue
        else:
            my_status.user_input = raw_input(my_status.display) 
            s.sendall(my_status.save_to_json())


    s.close() 

