"""
hangman - starting with basic one player
TODO - remove hardcoding

"""
import sys
import game
from game import Game_Status
import socket




if __name__ == "__main__":


    host = 'localhost' 
    port = 50000 
    size = 1024 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect((host,port))

    s.send("start")

   # print "connected"
    while True:
    #    print "waiting for data"
        my_status = Game_Status()
        my_status.load_from_json(s.recv(size))
     #   print "got data"
        
        if (my_status.get_status_flag() > game.IN_PLAY):
            print my_status.get_display()
            break
        else:
            user_input = raw_input(my_status.get_display())
            
            my_status.set_user_input(user_input)
            s.sendall(my_status.save_to_json())


    s.close() 

