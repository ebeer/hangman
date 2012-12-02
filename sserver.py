"""
simple server for gameplay

TODO - echo host/port
TODO - get 2 player working
"""

import select 
import socket 
import sys
import game

host = '' 
port = 50000 
backlog = 5 
size = 1024 
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host,port)) 
server.listen(backlog)
inputs = [server]
running = 1
socket1 = ""
socket2 = ""
versus = game.Match()

while running: 
    inputready,outputready,exceptready = select.select(inputs,[],[]) 

    for s in inputready: 
      #  print "input ready contains: " + str(len(inputready))
        if s == server: 
            # handle the server socket 
            client, address = server.accept()  
            inputs.append(client)
        else:
            data = s.recv(size)
       #     print "data = " + data
        #    print "waiting value = " + str(versus.waiting)
            if versus.waiting:
                if (versus.is_two_player & versus.players <2):
                    #waiting
                    versus.waiting = True
                elif (versus.is_two_player & versus.players == 2):
                    versus.start_2player()
                    
                status_message = game.Game_Status()
                if (not data == "start"):
                    status_message.load_from_json(data)
                    if (not versus.process_multi_request(status_message)):
                        status_message = versus.start_1player(s)
                else:
                    status_message = versus.prompt_for_multiplayer()
                    
                s.send(status_message.save_to_json())
            else:
         #       print "got response"
                status_message = game.Game_Status()
                status_message.load_from_json(data)
                status_message = versus.process_game_response(s, status_message)
                s.send(status_message.save_to_json())
                if (status_message.get_status_flag() > game.IN_PLAY):
                    s.close()
                
    
server.close()
